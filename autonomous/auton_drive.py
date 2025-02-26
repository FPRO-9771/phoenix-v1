from commands2 import SubsystemBase, Command, RunCommand, WaitCommand
from wpilib import Timer


class AutonDrive(SubsystemBase):

    def __init__(self, drivetrain, drive):
        print(f"***** AUTON D I")
        super().__init__()
        self.drivetrain = drivetrain
        self.drive = drive


    # def drive_y(self, speed: float) -> Command:
    #     print(f"***** AUTON D Y I")
    #
    #     return RunCommand(
    #         lambda: self.debug_drive(speed),
    #         self.drivetrain  # Ensure it properly schedules
    #     )
    #
    # def debug_drive(self, speed):
    #     print(f"🔥 APPLYING DRIVE COMMAND with speed {speed}")  # Debug print
    #     self.drivetrain.apply_request(
    #         lambda: self.drive.with_rotational_rate(speed)
    #     )
    #
    #     # Print the drivetrain’s state to confirm if the request is applied
    #     current_state = self.drivetrain.  # Modify based on actual method
    #     print(f"🔄 DEBUG: Drivetrain state = {current_state}")
        # class DriveY(Command):
        #     def __init__(self, drive_y, _speed):
        #         super().__init__()
        #         self.drivetrain = drive_y.drivetrain
        #         self.drive = drive_y.drive
        #         self.speed = _speed
        #         self.addRequirements(self.drivetrain)
        #
        #         self.timer = Timer()
        #         self.voltage = 0
        #
        #
        #
        #     def initialize(self):
        #         print(f"***** AUTON D Y I")
        #         self.timer.reset()
        #         self.timer.start()
        #
        #
        #     def execute(self):
        #
        #         print(f"***** AUTON D Y Run")
        #
        #         return InstantCommand(
        #             lambda: self.drivetrain.apply_request(
        #                 lambda: self.drive.with_rotational_rate(speed)
        #             ),
        #             self.drivetrain  # Ensure it properly schedules
        #         )
        #
        #     def isFinished(self):
        #         return False
        #
        #     def end(self, interrupted):
        #         print(f"***** AUTON D Y E")
        #         self.timer.stop()
        #
        # return DriveY(self, speed)
