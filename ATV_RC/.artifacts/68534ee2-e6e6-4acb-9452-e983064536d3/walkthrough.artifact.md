# Walkthrough - ATV Remote Control (Custom JSON & Gear Mapping)

I have updated the transmission format to match your specific JSON requirements and implemented the hardware-level gear mapping.

## Changes Made

### 1. New JSON Structure
- **File**: [MainActivity.kt](file:///C:/Users/Tural Gasimov/Desktop/repos/AzSimX/ATV_stack/ATV_RC/app/src/main/java/com/example/atv_rc/MainActivity.kt)
- **Format**: All packets now follow the provided template:
  ```json
  {
      "MSGshort": 0,
      "LOG": 1,
      "PrintLastLog": 1,
      "SysPWDN": 0,
      "MotorPWDN": 0,
      "PBTT0": 0,
      "PBTT1": 0,
      ...
      "HBTT": 350
  }
  ```
- **Motor Logic**: `MotorPWDN` is set to `0` when the motor is engaged (Latch Down) and `1` (Power Down) when released.

### 2. Gear Direction Mapping
- **Drive (D)**: Sets `PBTT1: 1` and `PBTT2: 1`. All other `PBTT` fields are `0`.
- **Reverse (R)**: Sets `PBTT0: 1` and `PBTT3: 1`. All other `PBTT` fields are `0`.
- **Latency**: These bits update instantly in the 10ms stream as soon as L1 is pressed or released.

### 3. Safety & Throttling
- **Analog Throttle**: The `HBTT` key contains the `0-4095` value.
- **Interlock**: If the system is LOCKED or the motor is OFF, `HBTT` is forced to `0` for safety.

## Verification
1.  **D-Gear Check**: Hold L1. Verify the UDP packet shows `PBTT1: 1` and `PBTT2: 1`.
2.  **R-Gear Check**: Release L1. Verify the UDP packet shows `PBTT0: 1` and `PBTT3: 1`.
3.  **Power Down**: Release the Z latch. Verify `MotorPWDN: 1` and `HBTT: 0`.
4.  **Heartbeat**: Verify the full JSON block is sent every 10ms.
