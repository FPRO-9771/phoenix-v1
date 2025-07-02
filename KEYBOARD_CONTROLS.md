# Keyboard Controls for Simulation Testing

This guide shows how to test Ruby's functions using keyboard controls in the simulation GUI.

## How to Use

1. Run the simulation: `robotpy sim`
2. The GUI will open showing joystick controls
3. Enable the robot (click "Robot" > "Teleop")
4. Use the keyboard keys below to control Ruby

## Driver Controls (Keyboard 0)
**Used for driving and robot movement**

| Key | Function | Description |
|-----|----------|-------------|
| W/S | Forward/Backward | Drive forward/back |
| A/D | Left/Right | Drive left/right |
| E/R | Rotate | Rotate left/right |
| Z   | Button A | Brake |
| X   | Button B | Point wheels |
| C   | Button X | SysId reverse |
| V   | Button Y | SysId forward |

## Operator Controls (Keyboard 1) 
**Used for mechanisms including Parade shooter**

### Parade Shooter Controls (SHOOTER_TYPE = "Parade")
| Key | Function | Description |
|-----|----------|-------------|
| **Q** | **Left Trigger** | **🔄 Pull-back (hold)** |
| **E** | **Right Trigger** | **🔥 Fire (press)** |

### Other Mechanism Controls
| Key | Function | Description |
|-----|----------|-------------|
| I/K | Left Stick Y | Elevator up/down |
| J/L | Left Stick X | (not used) |
| M   | Button A | Shoot level 2 |
| ,   | Button B | Intake |
| .   | Button X | Shoot level 3 |
| /   | Button Y | Shoot level 4 |
| A   | Button 5 | (additional) |
| B   | Button 6 | (additional) |
| X   | Button 7 | (additional) |
| Y   | Button 8 | (additional) |

## Testing the Parade Shooter

1. **Set Parade Mode**: Ensure `SHOOTER_TYPE = "Parade"` in `constants.py`
2. **Run Simulation**: `robotpy sim`
3. **Enable Robot**: Click "Robot" > "Teleop" in the GUI
4. **Test Pull-back**: Hold **Q** key - should see motor voltage in sim GUI
5. **Test Fire**: Press **E** key - should see motors spin at max speed for 0.5s

## Watching Motor Behavior

In the simulation GUI:
- Look for "TalonFX" devices in the device tree
- Motors 27 (Left) and 28 (Right) are the Parade shooter
- Watch "Motor Voltage" values change when you press Q or E
- Voltage should be negative for pull-back, positive for fire

## Troubleshooting

**No response when pressing keys:**
- Make sure the GUI window has focus
- Ensure robot is in "Teleop" mode
- Check that `SHOOTER_TYPE = "Parade"` in constants.py

**Can't see motor voltages:**
- Expand the device tree in the sim GUI
- Look for TalonFX devices with IDs 27 and 28
- Right-click and add them to display

**Joystick errors:**
- These are normal when no physical controllers are connected
- Keyboard controls will still work