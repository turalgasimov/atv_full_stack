#!/usr/bin/env python3
import socket
import json
import serial
import serial.tools.list_ports
import time
import os

# config
BAUD_RATE = 38400
UDP_IP = "0.0.0.0"
UDP_PORT = 5005

def calculate_modbus_crc(data: bytes) -> int:
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

def find_stm32_port():
    ports = serial.tools.list_ports.comports()
    for port in ports:
        if "ttyTHS" in port.device or "ttyACM" in port.device or "COM" in port.device:
            return port.device
    return "/dev/ttyACM0" if os.path.exists("/dev/ttyACM0") else None

def send_frame_immediately(ser, msg_dict: dict):
    # Format directly from incoming Android JSON payload
    json_str = json.dumps(msg_dict, separators=(',', ':'))
    crc = calculate_modbus_crc(json_str.encode('ascii'))
    crc_str = f"{crc & 0xFF:02x}{(crc >> 8) & 0xFF:02x}"
    
    full_msg = f"{json_str}:{crc_str}\r\n"    
    ser.write(full_msg.encode('ascii'))
    print(f"[TX DIRECT] HBTT: {msg_dict.get('HBTT', 0)} | Frame: {full_msg.strip()}")

def main():
    port_name = find_stm32_port()
    if not port_name:
        print("Error: Serial port not found.")
        return

    try:
        ser = serial.Serial(
            port=port_name,
            baudrate=BAUD_RATE,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            timeout=0.1,
            write_timeout=2
        )

        ser.dtr = True
        ser.rts = True
        time.sleep(0.1)
        ser.dtr = False
        ser.rts = False
        time.sleep(0.5)
        ser.reset_input_buffer()
        ser.reset_output_buffer()
        print(f"Connected to {port_name}. Ready for immediate transmission.\n")

    except Exception as e:
        print(f"Failed to open port: {e}")
        return

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((UDP_IP, UDP_PORT))

    try:
        while True:
            # 1. Receive packet from Android
            data, _ = sock.recvfrom(1024)

            # 2. Forward received payload straight to STM32
            try:
                payload = json.loads(data.decode('utf-8'))
                send_frame_immediately(ser, payload)
            except (json.JSONDecodeError, ValueError):
                pass

    except KeyboardInterrupt:
        print("\nStopping...")
    finally:
        sock.close()
        ser.close()

if __name__ == "__main__":
    main()