from autonomous.auton_modes import Leave, ShootLeft, ShootRight, ShootCenter
from wpilib import SendableChooser

def create_auton_chooser(drivetrain, drive, auton_operator):
    chooser = SendableChooser()
    modes = {
        "Leave": Leave(drivetrain, drive),
        "Left": ShootLeft(drivetrain, drive, auton_operator),
        "Right": ShootRight(drivetrain, drive, auton_operator),
        "Center": ShootCenter(drivetrain, drive, auton_operator),
    }

    default_modes = []
    mode_names = []

    for k, v in sorted(modes.items()):
        if getattr(v, "DEFAULT", False):  # Check if it's the default mode
            print(f"***** AUTON Mode Loaded: {k} [Default]")
            chooser.setDefaultOption(k, v)
            default_modes.append(k)
        else:
            print(f"***** AUTON Mode Loaded: {k}")
            chooser.addOption(k, v)

        mode_names.append(k)

    return chooser  # Return the configured chooser
