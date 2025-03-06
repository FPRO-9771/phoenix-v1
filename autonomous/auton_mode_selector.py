from autonomous.auton_modes import AutonModes
from wpilib import SendableChooser
from commands2 import SequentialCommandGroup, WaitCommand


def create_auton_chooser(auton_drive, auton_operator):
    chooser = SendableChooser()
    auton_modes = AutonModes(auton_drive, auton_operator)

    # Create functions that will create fresh command instances when called
    def blue_right():
        return auton_modes.blue_right_auto()

    chooser.setDefaultOption("Auto Blue Right", blue_right)

    return chooser
