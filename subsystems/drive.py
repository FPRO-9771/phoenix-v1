from commands2 import Command
from handlers.limelight_handler import LimelightHandler
from wpilib import Timer


class Drive(Command):
    def __init__(self, drivetrain, drive, max_angular_rate):
        super().__init__()

        self.drivetrain = drivetrain
        self.drive = drive
        self.max_angular_rate = max_angular_rate
        self.addRequirements(self.drivetrain)  # Ensure drivetrain ownership
        self.apply_request_command = None  # Store the command

        self.limelight_handler = LimelightHandler(debug=True)
        self.arrived_target = 0.22

    def initialize(self):
        """Called once when the command is scheduled."""
        print("Initializing DriveCommand...")

    def execute(self):
        result = self.limelight_handler.read_results()
        if result and result.validity and result.fiducialResults:
            print(f"-------")
            print(f"-------")
            print("----- Target: Acquired")
            target_area = result.fiducialResults[0].target_area
            tx = result.fiducialResults[0].target_x_degrees
            print(f"------- ta: {target_area}")
            print(f"------- tx: {tx}")

            # if tx:
            #     self.apply_request_command = self.drivetrain.apply_request(lambda: self.drive.with_rotational_rate(tx * 0.05))
            #     self.apply_request_command.schedule()  # Schedule it to actually run

            if abs(tx) > 1.0:
                scaled_rotation = tx / 45
                rotation_rate = -scaled_rotation * self.max_angular_rate
                print("----- Scaled Rotation:", scaled_rotation)
                print("----- Rotation Rate:", rotation_rate)

                # Debug rotation request
                self.apply_request_command = self.drivetrain.apply_request(
                    lambda: self.drive.with_rotational_rate(rotation_rate)
                )
                self.apply_request_command.schedule()  # Schedule it to actually run


def end(self, interrupted):
    print("Stopping DriveCommand...")


def isFinished(self):
    """Return True if the command should end immediately."""
    return False  # Keep running until interrupted
