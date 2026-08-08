# Implementation Plan - Refined Motor Interlock and State Hierarchy

This plan refines the control logic to ensure "Down is ON, Up is OFF" for the motor latch and implements a strict hierarchy for control visibility and packet transmission.

## Proposed Changes

### [app]

#### [MODIFY] [MainActivity.kt](file:///C:/Users/Tural Gasimov/Desktop/repos/AzSimX/ATV_stack/ATV_RC/app/src/main/java/com/example/atv_rc/MainActivity.kt)
- **State Transition Logic**:
    - **Motor (Button Z)**:
        - Update `onKeyDown` to set `motorOn = 1`.
        - Update `onKeyUp` to set `motorOn = 0`.
    - **Interlock Hierarchy**:
        - If `motorOn == 0`:
            - UI should visually disable all controls (Gears, Safety, Joystick labels).
            - Packet will send neutral values and `motor_on: 0`.
        - If `motorOn == 1`:
            - UI highlights gears and joystick movement.
            - If `isReady == false`: Packet sends neutral joystick values but `motor_on: 1`.
            - If `isReady == true`: Packet sends active joystick values.
- **UI Updates**:
    - Refine `updateUI()` to enforce visual graying-out of components when the motor is OFF.

## Verification Plan

### Manual Verification
1.  **Motor Latch**: Press Button Z. Engine light turns ON. Release Button Z. Engine light turns OFF.
2.  **Motor OFF state**:
    - While Z is NOT pressed, verify that moving the joystick or pressing A (Safety) / L1 (Gear) does not change the UI colors (everything stays dull) or send active movement in the packet.
3.  **Motor ON + LOCKED**:
    - Hold Button Z. Verify Engine light is ON.
    - Toggle A to see "LOCKED". Move joystick; verify UI numbers change but `nc` (UDP listener) shows neutral values.
4.  **Motor ON + READY**:
    - Hold Button Z. Toggle A to see "READY". Move joystick; verify active values are sent in the packet.
