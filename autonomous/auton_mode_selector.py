from autonomous.auton_modes import AutonModes
from wpilib import SendableChooser, SmartDashboard
from commands2 import SequentialCommandGroup, WaitCommand

def create_auton_chooser(auton_drive, auton_operator):
    chooser = SendableChooser()
    auton_modes = AutonModes(auton_drive, auton_operator)

    # Create functions that will create fresh command instances when called
    def timer():
        return auton_modes.test_timer_auto()

    def ll_data():
        return auton_modes.test_ll_data()

    def ll():
        return auton_modes.test_ll_auto()

    def ap():
        return auton_modes.test_pa_auto()

    def sl():
        return auton_modes.test_servo()

    chooser.addOption("Timer", timer)
    chooser.addOption("Limelight Data Only", ll_data)
    chooser.addOption("Limelight", ll)
    chooser.addOption("Align Pipe", ap)
    chooser.setDefaultOption("Shooter Lock", sl)
    # chooser.addOption("Timer", timer)
    # chooser.setDefaultOption("Limelight", ll)

    SmartDashboard.putData("Auto Mode", chooser)

    return chooser
