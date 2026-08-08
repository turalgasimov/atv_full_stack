import serial
import serial.tools.list_ports
import time
import threading
import os
import socket
import json

BAUD_RATE = 38400  # Matches Qt configuration
UDP_IP = "0.0.0.0" 
UDP_PORT = 5005    

def calculate_modbus_crc(data: bytes) -> int:
    crc = 0xFFFF
    for byte in data:
        crc ^= byte
        for _ in range(8):
            if (crc & 0x0001) != 0:
                crc = (crc >> 1) ^ 0xA001
            else:
                crc >>= 1
    return crc

def find_stm32_port():
    print("Scanning available serial ports...")
    ports = serial.tools.list_ports.comports()
    for port in ports:
        if "ttyTHS" in port.device or "ttyACM" in port.device:
            print(f"-> Selected STM32 connection: {port.device}")
            return port.device
            
    default_uart = "/dev/ttyACM0"
    if os.path.exists(default_uart):
        return default_uart
    return None

def build_short_message(ccw=1, ang=0, rpm=0):
    json_str = f'{{"MSGshort":1,"CCW":{ccw},"ANG":{ang},"RPM":{rpm}}}'
    data_bytes = json_str.encode('utf-8')
    crc = calculate_modbus_crc(data_bytes)
    low_byte = crc & 0xFF
    high_byte = (crc >> 8) & 0xFF
    crc_hex = f"{low_byte:02X}{high_byte:02X}"
    return data_bytes + b":" + crc_hex.encode('utf-8') + b"\n"

def build_long_message(log=1, print_last_log=0, sys_pwdn=0, motor_pwdn=0, 
                       pbtt_states=[0]*10, hbtt=0):
    if len(pbtt_states) != 10:
        pbtt_states = [0] * 10

    json_str = (
        f'{{"MSGshort":0,'
        f'"LOG":{log},'
        f'"PrintLastLog":{print_last_log},'
        f'"SysPWDN":{sys_pwdn},'
        f'"MotorPWDN":{motor_pwdn},'
        f'"PBTT0":{pbtt_states[0]},'
        f'"PBTT1":{pbtt_states[1]},'
        f'"PBTT2":{pbtt_states[2]},'
        f'"PBTT3":{pbtt_states[3]},'
        f'"PBTT4":{pbtt_states[4]},'
        f'"PBTT5":{pbtt_states[5]},'
        f'"PBTT6":{pbtt_states[6]},'
        f'"PBTT7":{pbtt_states[7]},'
        f'"PBTT8":{pbtt_states[8]},'
        f'"PBTT9":{pbtt_states[9]},'
        f'"HBTT":{hbtt}}}'
    )
    data_bytes = json_str.encode('utf-8')
    crc = calculate_modbus_crc(data_bytes)
    low_byte = crc & 0xFF
    high_byte = (crc >> 8) & 0xFF
    crc_hex = f"{low_byte:02X}{high_byte:02X}"
    return data_bytes + b":" + crc_hex.encode('utf-8') + b"\n"

def read_from_stm(ser):
    while ser.is_open:
        try:
            if ser.in_waiting > 0:
                line = ser.readline().decode('utf-8', errors='ignore').strip()
                if line:
                    print(f"\n[STM32 RX] {line}")
            else:
                time.sleep(0.01)
        except Exception as e:
            print(f"\nRead error: {e}")
            break

def main():
    port_name = find_stm32_port()
    if not port_name:
        print("Error: No UART/USB ports detected.")
        return

    try:
        ser = serial.Serial(
            port=port_name,
            baudrate=BAUD_RATE,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            timeout=1
        )
        print(f"Successfully opened {port_name} at {BAUD_RATE} baud.")
    except Exception as e:
        print(f"Failed to open port {port_name}: {e}")
        return

    rx_thread = threading.Thread(target=read_from_stm, args=(ser,), daemon=True)
    rx_thread.start()

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((UDP_IP, UDP_PORT))
    print(f"Listening for UDP on port {UDP_PORT}...\n")

    cached_state = {
        "motor_on": 0,
        "direction": "R",
        "ready": False,
        "x": 0.0,
        "hbtt": 0
    }

    last_long_send_time = 0.0
    last_sent_hbtt = None

    try:
        while True:
            # 1. Blocking wait for the first incoming UDP packet
            data, addr = sock.recvfrom(1024)
            
            # 2. DRAIN UDP BUFFER: Keep pulling non-blocking packets to process ONLY the newest packet
            sock.setblocking(False)
            try:
                while True:
                    more_data, _ = sock.recvfrom(1024)
                    data = more_data
            except BlockingIOError:
                pass
            finally:
                sock.setblocking(True)
            
            try:
                payload = json.loads(data.decode('utf-8'))
                
                button_event = False
                if "motor_on" in payload:
                    cached_state["motor_on"] = payload.get("motor_on", cached_state["motor_on"])
                    cached_state["direction"] = payload.get("direction", cached_state["direction"])
                    cached_state["ready"] = payload.get("ready", cached_state["ready"])
                    button_event = True

                if "hbtt" in payload:
                    cached_state["x"] = payload.get("x", cached_state["x"])
                    cached_state["hbtt"] = payload.get("hbtt", cached_state["hbtt"])

                # Extract values
                motor_on = cached_state["motor_on"]
                is_ready = cached_state["ready"]
                direction = cached_state["direction"]
                x_val = cached_state["x"]
                hbtt = cached_state["hbtt"]

                if motor_on == 0 or not is_ready:
                    ccw = 0  # Stop
                    rpm = 0
                    motor_pwdn = 1
                else:
                    ccw = 1 if direction == "D" else 2  # 1 = CW, 2 = CCW
                    rpm = 100
                    motor_pwdn = 0

                ang = int(((x_val + 1.0) / 2.0) * 360)

                # Send Short Message (Steering & Motion)
                short_packet = build_short_message(ccw=ccw, ang=ang, rpm=rpm)
                ser.write(short_packet)

                # Rate-limit Long Message to max 10 Hz (100 ms) OR immediate on button press
                now = time.time()
                should_send_long = button_event or (
                    (now - last_long_send_time > 0.1) and (hbtt != last_sent_hbtt)
                )

                if should_send_long:
                    long_packet = build_long_message(
                        log=1, print_last_log=0, 
                        sys_pwdn=0, motor_pwdn=motor_pwdn, 
                        pbtt_states=[0]*10, hbtt=hbtt
                    )
                    ser.write(long_packet)
                    last_sent_hbtt = hbtt
                    last_long_send_time = now

                # Real-time live status monitor on Python console
                print(
                    f"\r[LIVE TX] Motor:{motor_on} | Ready:{is_ready} | Dir:{direction} | "
                    f"ANG:{ang}° | HBTT:{hbtt}  ", 
                    end="", 
                    flush=True
                )

            except json.JSONDecodeError:
                pass

    except KeyboardInterrupt:
        print("\nStopping script...")
    finally:
        sock.close()
        ser.close()
        print("\nPorts closed.")

if __name__ == "__main__":
    main()