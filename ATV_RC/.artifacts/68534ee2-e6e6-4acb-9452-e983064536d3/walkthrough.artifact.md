# Walkthrough - ATV Remote Control (Optimized Transmission)

I have refactored the transmission logic to separate critical drive signals from state changes, improving network efficiency and control responsiveness.

## Changes Made

### 1. Drive Signal Stream (Heartbeat)
- **File**: [MainActivity.kt](file:///C:/Users/Tural Gasimov/Desktop/repos/AzSimX/ATV_stack/ATV_RC/app/src/main/java/com/example/atv_rc/MainActivity.kt)
- **Key Update**: The joystick Y-axis is now labeled as `hbtt` in the JSON payload.
- **Frequency**: The app sends a stream of `{"x": float, "hbtt": int}` packets every **10ms** (100Hz).
- **Safety Interlock**: If the motor is OFF or the system is LOCKED, the loop automatically sends neutral values (`x: 0.0, hbtt: 0`) to ensure safety.

### 2. Event-Driven State Updates
- **Description**: Non-analog states are now sent **only when they change** to reduce redundant network traffic.
- **Payload**: `{"motor_on": int, "direction": string, "ready": boolean}`.
- **Trigger**: Sent immediately when:
    - The motor latch (Z) is engaged/disengaged.
    - The gear (L1) is shifted between D and R.
    - The safety toggle (A) is clicked.

### 3. Logic & Stability Fixes
- **Fixed Typo**: Corrected a code error where the neutral value was incorrectly initialized.
- **Transmission Precision**: Switched to `scheduleAtFixedRate` for the 10ms loop to ensure a consistent 100Hz frequency without drift.

## Verification
1.  **Joystick Response**: Verify that `hbtt` scales from `0-4095` when pushing forward and is streamed constantly.
2.  **State Latency**: Verify that gear changes and safety toggles are received immediately by the Jetson as soon as the button is pressed.
3.  **Safety**: Verify that releasing the motor latch immediately forces the `hbtt` stream to 0 and sends a `motor_on: 0` state packet.
