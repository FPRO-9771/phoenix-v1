from commands2 import Command, CommandScheduler, WaitCommand, SequentialCommandGroup, StartEndCommand, RunCommand, InstantCommand
from constants import CON_ELEV, CON_ARM, CON_SHOOT
from autonomous.auton_constants import INSTRUCTIONS
from autonomous.auton_drive import AutonDrive

from generated.tuner_constants import TunerConstants
from phoenix6 import swerve

from wpilib import Timer

# from subsystems.shooter import Shooter

class AutonBlueLeft(Command):

    def __init__(self):
        super().__init__()
        # Add subsystem dependencies here if needed

    def initialize(self):
        print(f"***** AUTON ABR I")

    def execute(self):
        # Add movement logic (e.g., drive forward, turn, etc.)
        pass

    def isFinished(self):
        return True  # Modify based on your sequence duration

    def end(self, interrupted):
        print(f"***** AUTON ABL End")


def create_blue_right_auto(drivetrain, drive, max_angular_rate, auton_operator, elevator, arm, shooter):
    """Factory function that returns a new command group for blue right autonomous"""

    # Create a new command group with fresh command instances
    commands = []

    # Add your sequence of commands
    commands.append(DriveForwardCommand(drivetrain, drive, -1, 1))
    commands.append(WaitCommand(1.0))

    return SequentialCommandGroup(*commands)


# Create a separate command class for your drive movement
class DriveForwardCommand(Command):
    def __init__(self, drivetrain, drive, speed, timeout_seconds):
        super().__init__()
        self.drivetrain = drivetrain
        self.drive = drive
        self.speed = speed
        self.timeout_seconds = timeout_seconds
        self.addRequirements(drivetrain)

        # Create the request command when initialized
        self.request_command = None
        self.timer = Timer()  # Use WPILib's Timer class

    def initialize(self):
        print(f"Starting drive forward at speed {self.speed}")

        # Reset and start the timer
        self.timer.reset()
        self.timer.start()

        # Create and schedule the request command
        return self.drivetrain.apply_request(
            lambda: (
                self.drive
                .with_velocity_x(self.speed)
            )
        )



    def execute(self):
        # The request_command is handling the motor control
        # Add debug printing for the timer
        if self.timer.hasElapsed(0.5):  # Print every half second
            print(f"Timer: {self.timer.get()} / {self.timeout_seconds}")

    def end(self, interrupted):
        print(f"Drive command ended, interrupted: {interrupted}")

        # Stop the timer
        self.timer.stop()

        # Cancel the request command
        if self.request_command is not None:
            self.request_command.cancel()

        # Create and schedule a stop command
        stop_command = self.drivetrain.apply_request(
            lambda: (
                self.drive
                .with_velocity_x(0)
            )
        )
        stop_command.schedule()

    def isFinished(self):
        # Check if timeout has elapsed using the WPILib Timer
        finished = self.timer.hasElapsed(self.timeout_seconds)
        if finished:
            print(f"Command timed out after {self.timer.get()} seconds")
        return finished

# # SAVE!! THIS WORKS AND SPINS THE MOTORS!
# class AutonBlueRight(SequentialCommandGroup):
#     DEFAULT = True
#
#     def __init__(self, drivetrain, drive, max_angular_rate, shooter):
#         super().__init__(
#             shooter.shoot(CON_SHOOT["high"], 'shoot'),  # ✅ Start shooter
#             WaitCommand(1.0),
#             drivetrain.apply_request(
#                 lambda: (
#                     drive
#                     .with_rotational_rate(
#                         0.9
#                     )  # Drive counterclockwise with negative X (left)
#                 )
#             ).withTimeout(3)
#
#         )
#
#     def end(self, interrupted):
#         print(f"***** AUTON ABR End")
