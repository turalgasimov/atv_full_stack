#!/usr/bin/env python3
"""
Quadrocycle Control GUI
Controls STM32F401 quadrocycle system via USB CDC COM port
"""

import tkinter as tk
from tkinter import ttk, scrolledtext
import serial
import serial.tools.list_ports
import json
import queue
import threading
import time


def calculate_modbus_crc(data):
    """Calculate Modbus CRC16 for the given data"""
    crc = 0xFFFF
    for byte in data:
        crc ^= byte
        for _ in range(8):
            if crc & 0x0001:
                crc >>= 1
                crc ^= 0xA001
            else:
                crc >>= 1
    return crc


class QuadrocycleControlGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Quadrocycle Control Panel")
        self.root.geometry("800x700")

        self.serial_port = None
        self.is_connected = False
        self.receive_thread = None
        self.running = False
        self.port_lock = threading.Lock()

        # Set once the reader thread has finished resetting the device. Starts set
        # so a send before the first connect fails on the port check, not here.
        self.port_ready = threading.Event()
        self.port_ready.set()

        # Auto-send state. auto_send_job holds the pending after() id so it can be
        # cancelled; leaving it scheduled would keep transmitting after disconnect.
        self.auto_send_on = False
        self.auto_send_job = None
        self.auto_send_interval_ms = 500

        # The reader thread must not touch Tk directly, so it hands lines to the
        # main thread through this queue, drained by poll_rx_queue().
        self.rx_queue = queue.Queue()

        self.setup_ui()
        self.poll_rx_queue()

    def setup_ui(self):
        # Connection Frame
        conn_frame = ttk.LabelFrame(self.root, text="Connection", padding=10)
        conn_frame.grid(row=0, column=0, columnspan=2, sticky="ew", padx=10, pady=5)

        ttk.Label(conn_frame, text="COM Port:").grid(row=0, column=0, padx=5)
        self.port_combo = ttk.Combobox(conn_frame, width=15, state="readonly")
        self.port_combo.grid(row=0, column=1, padx=5)

        ttk.Button(conn_frame, text="Refresh", command=self.refresh_ports).grid(row=0, column=2, padx=5)
        self.connect_btn = ttk.Button(conn_frame, text="Connect", command=self.toggle_connection)
        self.connect_btn.grid(row=0, column=3, padx=5)

        # Auto-send toggle. Enabled: repeatedly transmits the currently selected
        # motor state. Disabled: sends nothing.
        self.auto_send_btn = ttk.Button(conn_frame, text="Auto-Send: OFF",
                                        width=16, command=self.toggle_auto_send)
        self.auto_send_btn.grid(row=0, column=4, padx=5)

        self.status_label = ttk.Label(conn_frame, text="Disconnected", foreground="red")
        self.status_label.grid(row=0, column=5, padx=10)

        # Chooses which frame(s) the auto-send loop transmits each tick.
        self.auto_mode_var = tk.StringVar(value="motor")
        mode_frame = ttk.Frame(conn_frame)
        mode_frame.grid(row=1, column=0, columnspan=6, sticky="w", padx=5, pady=(6, 0))
        ttk.Label(mode_frame, text="Auto-send payload:").pack(side="left")
        for text, val in (("Motor (short)", "motor"),
                          ("GPIO (long)", "gpio"),
                          ("Both", "both")):
            ttk.Radiobutton(mode_frame, text=text, value=val,
                            variable=self.auto_mode_var).pack(side="left", padx=4)

        # Motor Control Frame
        motor_frame = ttk.LabelFrame(self.root, text="Motor Control (Short Message)", padding=10)
        motor_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)

        ttk.Label(motor_frame, text="Direction:").grid(row=0, column=0, sticky="w", pady=5)
        self.direction_var = tk.IntVar(value=6)
        directions = [
            ("Ignore", 6),
            ("Clockwise (CC)", 1),
            ("Counter-Clockwise (CCW)", 2),
            ("CC + Back Home", 3),
            ("CCW + Back Home", 4),
            ("Home", 5)
        ]
        for i, (text, value) in enumerate(directions):
            ttk.Radiobutton(motor_frame, text=text, variable=self.direction_var,
                          value=value).grid(row=i+1, column=0, sticky="w", padx=20)

        ttk.Label(motor_frame, text="Angle (0-360°):").grid(row=7, column=0, sticky="w", pady=5)
        self.angle_var = tk.IntVar(value=180)
        self.angle_scale = ttk.Scale(motor_frame, from_=0, to=360, orient="horizontal",
                                     variable=self.angle_var, length=200)
        self.angle_scale.grid(row=8, column=0, sticky="ew", padx=20)
        self.angle_label = ttk.Label(motor_frame, text="180°")
        self.angle_label.grid(row=9, column=0, pady=2)
        self.angle_var.trace_add("write", self.update_angle_label)

        ttk.Label(motor_frame, text="RPM (0-100):").grid(row=10, column=0, sticky="w", pady=5)
        self.rpm_var = tk.IntVar(value=30)
        self.rpm_scale = ttk.Scale(motor_frame, from_=0, to=100, orient="horizontal",
                                   variable=self.rpm_var, length=200)
        self.rpm_scale.grid(row=11, column=0, sticky="ew", padx=20)
        self.rpm_label = ttk.Label(motor_frame, text="30 RPM")
        self.rpm_label.grid(row=12, column=0, pady=2)
        self.rpm_var.trace_add("write", self.update_rpm_label)

        ttk.Button(motor_frame, text="Send Motor Command",
                  command=self.send_motor_command).grid(row=13, column=0, pady=10)

        # GPIO Control Frame
        gpio_frame = ttk.LabelFrame(self.root, text="GPIO Control (Long Message)", padding=10)
        gpio_frame.grid(row=1, column=1, sticky="nsew", padx=10, pady=5)

        # Logging controls
        self.logging_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(gpio_frame, text="Enable Logging",
                       variable=self.logging_var).grid(row=0, column=0, sticky="w", pady=2)

        self.print_log_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(gpio_frame, text="Print Last Log",
                       variable=self.print_log_var).grid(row=1, column=0, sticky="w", pady=2)

        # Power controls
        self.sys_pwdn_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(gpio_frame, text="System Power Down",
                       variable=self.sys_pwdn_var).grid(row=2, column=0, sticky="w", pady=2)

        self.motor_pwdn_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(gpio_frame, text="Motor Power Down",
                       variable=self.motor_pwdn_var).grid(row=3, column=0, sticky="w", pady=2)

        # Push buttons
        ttk.Label(gpio_frame, text="Push Buttons (PBTT0-9):").grid(row=4, column=0, sticky="w", pady=5)
        self.pbtt_vars = []
        for i in range(10):
            var = tk.BooleanVar(value=False)
            self.pbtt_vars.append(var)
            ttk.Checkbutton(gpio_frame, text=f"PBTT{i}",
                          variable=var).grid(row=5+i//2, column=i%2, sticky="w", padx=10, pady=2)

        # Hold button
        ttk.Label(gpio_frame, text="Hold Button (0-4095):").grid(row=10, column=0, sticky="w", pady=5)
        self.hbtt_var = tk.IntVar(value=2048)
        ttk.Entry(gpio_frame, textvariable=self.hbtt_var, width=10).grid(row=11, column=0, sticky="w", padx=10)

        ttk.Button(gpio_frame, text="Send GPIO Command",
                  command=self.send_gpio_command).grid(row=12, column=0, columnspan=2, pady=10)

        # Console Frame
        console_frame = ttk.LabelFrame(self.root, text="Console", padding=10)
        console_frame.grid(row=2, column=0, columnspan=2, sticky="nsew", padx=10, pady=5)

        self.console = scrolledtext.ScrolledText(console_frame, height=15, width=90,
                                                 state='disabled', bg='black', fg='lime')
        self.console.pack(fill="both", expand=True)

        ttk.Button(console_frame, text="Clear Console",
                  command=self.clear_console).pack(pady=5)

        # Configure grid weights
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_rowconfigure(2, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=1)

        # Initial port refresh
        self.refresh_ports()

    def update_angle_label(self, *args):
        self.angle_label.config(text=f"{self.angle_var.get()}°")

    def update_rpm_label(self, *args):
        self.rpm_label.config(text=f"{self.rpm_var.get()} RPM")

    def refresh_ports(self):
        ports = [port.device for port in serial.tools.list_ports.comports()]
        self.port_combo['values'] = ports
        if ports:
            self.port_combo.current(0)
        self.log_to_console(f"Found {len(ports)} COM ports")

    def toggle_connection(self):
        if self.is_connected:
            self.disconnect()
        else:
            self.connect()

    def connect(self):
        port = self.port_combo.get()
        if not port:
            self.log_to_console("Please select a COM port")
            return

        try:
            # USB CDC with explicit settings
            self.serial_port = serial.Serial(
                port=port,
                baudrate=38400,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                timeout=0.1,
                xonxoff=False,
                rtscts=False,
                dsrdtr=False,
                write_timeout=2
            )

            # The DTR/RTS reset toggle and its settle delay used to run here, on the
            # main thread, blocking it for ~625 ms. The window ignores every click
            # for that whole time. The reader thread now does this before its first
            # read, so the GUI stays live.
            self.port_ready.clear()

            self.is_connected = True
            self.status_label.config(text="Connected", foreground="green")
            self.connect_btn.config(text="Disconnect")
            self.log_to_console(f"Connected to {port} at 38400 baud")

            # Start receive thread
            self.running = True
            self.receive_thread = threading.Thread(target=self.receive_data, daemon=True)
            self.receive_thread.start()

        except serial.SerialException as e:
            self.serial_port = None
            detail = str(e)
            if "Access is denied" in detail or "PermissionError" in detail:
                detail += ("\n\nOnly one program can hold the port. Close any other "
                           "instance of this GUI or serial terminal using it.")
            self.port_ready.set()
            self.log_to_console(f"Connection failed: {detail}")
        except Exception as e:
            self.serial_port = None
            self.port_ready.set()
            self.log_to_console(f"Connection failed: {e}")

    def disconnect(self):
        self.auto_send_stop("disconnected")
        self.running = False

        # Let the reader finish its in-flight read before closing underneath it.
        if self.receive_thread and self.receive_thread.is_alive():
            self.receive_thread.join(timeout=1.0)

        with self.port_lock:
            if self.serial_port and self.serial_port.is_open:
                self.serial_port.close()

        self.is_connected = False
        self.status_label.config(text="Disconnected", foreground="red")
        self.connect_btn.config(text="Connect")
        self.log_to_console("Disconnected")

    def send_motor_command(self):
        if not self.is_connected:
            self.log_to_console("Not connected to device")
            return

        # ttk.Scale stores floats in the IntVar, so coerce explicitly rather
        # than relying on IntVar.get() to truncate.
        msg_dict = {
            "MSGshort": 1,
            "CCW": int(self.direction_var.get()),
            "ANG": int(float(self.angle_scale.get())),
            "RPM": int(float(self.rpm_scale.get()))
        }

        self.send_message(msg_dict)

    def send_gpio_command(self):
        if not self.is_connected:
            self.log_to_console("Not connected to device")
            return

        # A non-numeric entry makes IntVar.get() raise, which would otherwise
        # abort this callback silently and look like a dead button.
        try:
            hbtt = int(self.hbtt_var.get())
        except (tk.TclError, ValueError):
            self.log_to_console("Invalid input: Hold Button must be a whole number 0-4095")
            return

        if not 0 <= hbtt <= 4095:
            self.log_to_console(f"Invalid input: Hold Button must be 0-4095 (got {hbtt})")
            return

        # Build long message
        msg_dict = {
            "MSGshort": 0,
            "LOG": int(self.logging_var.get()),
            "PrintLastLog": int(self.print_log_var.get()),
            "SysPWDN": int(self.sys_pwdn_var.get()),
            "MotorPWDN": int(self.motor_pwdn_var.get()),
            "PBTT0": int(self.pbtt_vars[0].get()),
            "PBTT1": int(self.pbtt_vars[1].get()),
            "PBTT2": int(self.pbtt_vars[2].get()),
            "PBTT3": int(self.pbtt_vars[3].get()),
            "PBTT4": int(self.pbtt_vars[4].get()),
            "PBTT5": int(self.pbtt_vars[5].get()),
            "PBTT6": int(self.pbtt_vars[6].get()),
            "PBTT7": int(self.pbtt_vars[7].get()),
            "PBTT8": int(self.pbtt_vars[8].get()),
            "PBTT9": int(self.pbtt_vars[9].get()),
            "HBTT": hbtt
        }

        self.send_message(msg_dict)

    def toggle_auto_send(self):
        if self.auto_send_on:
            self.auto_send_stop("turned off")
            return

        if not self.is_connected:
            self.log_to_console("Auto-send needs a connection first")
            return

        self.auto_send_on = True
        self.auto_send_btn.config(text="Auto-Send: ON")
        self.log_to_console(f"Auto-send ON ({self.auto_send_interval_ms} ms interval)")
        self.auto_send_tick()

    def auto_send_tick(self):
        self.auto_send_job = None
        if not self.auto_send_on:
            return
        if not self.is_connected:
            self.auto_send_stop("disconnected")
            return

        # Whatever the controls read right now, so moving a slider changes what
        # goes out on the next tick.
        mode = self.auto_mode_var.get()

        if mode in ("motor", "both"):
            self.send_motor_command()

        # Re-check state: send_motor_command can drop the connection on a write
        # error, and the firmware handles one frame at a time.
        if mode in ("gpio", "both") and self.auto_send_on and self.is_connected:
            self.send_gpio_command()

        # Reschedule only if still on. send_motor_command can turn auto-send off
        # via the error path in send_message.
        if self.auto_send_on:
            self.auto_send_job = self.root.after(self.auto_send_interval_ms,
                                                 self.auto_send_tick)

    def auto_send_stop(self, reason):
        was_on = self.auto_send_on
        self.auto_send_on = False
        if self.auto_send_job is not None:
            try:
                self.root.after_cancel(self.auto_send_job)
            except Exception:
                pass
            self.auto_send_job = None
        try:
            self.auto_send_btn.config(text="Auto-Send: OFF")
        except Exception:
            pass
        if was_on:
            self.log_to_console(f"Auto-send OFF ({reason})")

    def send_message(self, msg_dict):
        # Convert to JSON
        json_str = json.dumps(msg_dict, separators=(',', ':'))

        # Calculate CRC on JSON string WITHOUT the colon
        # Based on firmware: calculate_modbus_crc((uint8_t*)msg, endofjsonstr+1)
        # where endofjsonstr is position of '}', so endofjsonstr+1 includes up to and including '}'
        data_for_crc = json_str.encode('ascii')
        crc = calculate_modbus_crc(data_for_crc)

        # Format: low byte first
        crc_str = f"{crc & 0xFF:02x}{(crc >> 8) & 0xFF:02x}"

        # Build final message
        full_message = f"{json_str}:{crc_str}\r\n"

        # Non-blocking check. For the first ~600 ms after Connect the reader thread
        # is still resetting the device. Never wait() here: that would stall the
        # main thread and freeze the window, which is the bug this file had.
        if not self.port_ready.is_set():
            self.log_to_console("Port still initializing (~0.6 s), try again")
            return

        try:
            with self.port_lock:
                if not (self.serial_port and self.serial_port.is_open):
                    self.log_to_console("Send error: port is not open")
                    return
                bytes_written = self.serial_port.write(full_message.encode('ascii'))
                # No flush() here. On Windows it calls FlushFileBuffers, which
                # write_timeout does not cover, so it can block the main thread
                # indefinitely if the CDC endpoint stops draining. write() with
                # write_timeout=2 already bounds delivery to the driver.
            self.log_to_console(f"TX ({bytes_written} bytes): {full_message.strip()}")
        except Exception as e:
            # Deliberately not a messagebox. Every messagebox does an internal
            # grab_set; if the dialog lands behind the main window or off-screen,
            # all input is redirected to a dialog the user cannot see and the GUI
            # appears permanently dead while Windows still reports it responsive.
            self.log_to_console(f"Send error: {e}")
            self.auto_send_stop("send error")

    def receive_data(self):
        buffer = ""

        # Reset the device and let USB CDC settle. This runs off the main thread so
        # the window keeps redrawing and accepting clicks while it happens.
        try:
            port = self.serial_port
            port.dtr = True
            port.rts = True
            time.sleep(0.1)
            port.dtr = False
            port.rts = False
            time.sleep(0.5)
            port.reset_input_buffer()
            port.reset_output_buffer()
        except Exception as e:
            self.rx_queue.put(f"Port initialization error: {e}")
        finally:
            self.port_ready.set()

        self.rx_queue.put("[Receive thread started]")
        consecutive_errors = 0

        while self.running:
            try:
                port = self.serial_port
                if not (port and port.is_open):
                    break

                # Never hold port_lock across this read. It blocks for the port
                # timeout and the loop re-acquires immediately, which starves
                # send_command on the main thread and freezes the GUI. pyserial
                # allows one reader thread alongside one writer thread.
                pending = port.in_waiting
                data = port.read(pending) if pending else port.read(1)

                consecutive_errors = 0

                if data:
                    buffer += data.decode('ascii', errors='ignore')

                    # The firmware terminates every reply with \r\n.
                    while '\n' in buffer:
                        line, buffer = buffer.split('\n', 1)
                        line = line.strip()
                        if line:
                            self.rx_queue.put(f"RX: {line}")
                else:
                    # A read timeout is normal when the device has nothing to say.
                    time.sleep(0.01)

            except serial.SerialTimeoutException:
                pass
            except Exception as e:
                # Don't kill reception permanently on a transient error; only
                # give up if it keeps failing (cable pulled, port revoked).
                consecutive_errors += 1
                self.rx_queue.put(f"Receive error: {e}")
                if consecutive_errors >= 5:
                    self.rx_queue.put("[Too many receive errors, stopping reader]")
                    break
                time.sleep(0.2)

        self.rx_queue.put("[Receive thread stopped]")

    def poll_rx_queue(self):
        """Drain the reader thread's queue on the main thread (Tk is not thread-safe)."""
        # Cap the work per tick. An unbounded drain lets a chatty device starve the
        # event loop, which looks exactly like a frozen window.
        try:
            for _ in range(200):
                self.log_to_console(self.rx_queue.get_nowait())
        except queue.Empty:
            pass
        self.root.after(50, self.poll_rx_queue)

    def log_to_console(self, message):
        self.console.config(state='normal')
        self.console.insert(tk.END, message + '\n')
        self.console.see(tk.END)
        self.console.config(state='disabled')

    def clear_console(self):
        self.console.config(state='normal')
        self.console.delete(1.0, tk.END)
        self.console.config(state='disabled')


def main():
    root = tk.Tk()
    app = QuadrocycleControlGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
