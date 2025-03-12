# from autonomous.auton_modes import AutonModes
from wpilib import SendableChooser, SmartDashboard
from commands2 import SequentialCommandGroup, WaitCommand

def create_auton_chooser(auton_modes):
    chooser = SendableChooser()


    def blue_left():
        return auton_modes.full_auton("blue_left")

    def blue_right():
        return auton_modes.full_auton("blue_right")

    def red_left():
        return auton_modes.full_auton("red_left")

    def red_right():
        return auton_modes.full_auton("red_right")

    def seek_and_shoot_11():
        return auton_modes.seek_and_shoot(11)

    # Create functions that will create fresh command instances when called
    # def timer():
    #     return auton_modes.test_timer_auto()
    #
    def ll_data():
        return auton_modes.test_ll_data(6)

    def ap_no_move():
        return auton_modes.align_pipe_debug()

    def ap_move_left():
        return auton_modes.align_pipe_debug(True, "right")

    def ap_move_right():
        return auton_modes.align_pipe_debug(True, "left")

    def sl():
        return auton_modes.test_servo()

    def at():
        return auton_modes.test_auton()

    chooser.addOption("Blue Left", blue_left)
    chooser.addOption("Blue Right", blue_right)
    chooser.addOption("Red Left", red_left)
    chooser.addOption("Red Right", red_right)
    chooser.addOption("Seek and Shoot 11", seek_and_shoot_11)
    # chooser.setDefaultOption("Seek and Shoot closest", seek_and_shoot)
    # chooser.addOption("Timer", timer)
    chooser.addOption("Limelight Data Only", ll_data)
    # chooser.addOption("Limelight", ll)
    chooser.addOption("Align Pipe Debug Distance", ap_no_move)
    chooser.addOption("Align Pipe Debug Right", ap_move_left)
    chooser.addOption("Align Pipe Debug Left", ap_move_right)
    chooser.addOption("Shooter Lock", sl)
    chooser.addOption("Auton Test", at)
    # chooser.addOption("Timer", timer)
    # chooser.setDefaultOption("Limelight", ll)

    SmartDashboard.putData("Auto Mode", chooser)

    return chooser
