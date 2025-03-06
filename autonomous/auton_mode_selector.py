from autonomous.auton_modes import AutonModes
from wpilib import SendableChooser, SmartDashboard
from commands2 import SequentialCommandGroup, WaitCommand

def create_auton_chooser(auton_drive, auton_operator):
    chooser = SendableChooser()
    auton_modes = AutonModes(auton_drive, auton_operator)

    # Create functions that will create fresh command instances when called
    def timer():
        return auton_modes.test_timer_auto()

    def ll():
        return auton_modes.test_ll_auto()

    chooser.setDefaultOption("Timer", timer)
    chooser.addOption("Limelight", ll)
    # chooser.addOption("Timer", timer)
    # chooser.setDefaultOption("Limelight", ll)

    SmartDashboard.putData("Auto Mode", chooser)

    return chooser
