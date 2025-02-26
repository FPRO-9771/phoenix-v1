from autonomous.auton_modes import AutonBlueLeft, AutonBlueRight
from wpilib import SendableChooser

def create_auton_chooser(drivetrain, drive, max_angular_rate, auton_operator, elevator, arm, shooter):
    chooser = SendableChooser()
    modes = {
        "Auto Blue Left": AutonBlueLeft(),
        "Auto Blue Right": AutonBlueRight(drivetrain, drive, max_angular_rate, auton_operator, elevator, arm, shooter),
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
