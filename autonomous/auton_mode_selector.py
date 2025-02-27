from autonomous.auton_modes import AutonBlueLeft, create_blue_right_auto
from wpilib import SendableChooser
from commands2 import SequentialCommandGroup, WaitCommand


def create_auton_chooser(drivetrain, drive, max_angular_rate, auton_operator, elevator, arm, shooter):
    chooser = SendableChooser()

    # Create functions that will create fresh command instances when called
    def blue_right():
        create_blue_right_auto(drivetrain, drive, max_angular_rate, auton_operator, elevator, arm, shooter)

    chooser.setDefaultOption("Auto Blue Right", blue_right)

    return chooser
