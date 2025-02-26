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

# SAVE!! THIS WORKS AND SPINS THE MOTORS!
class AutonBlueRight(SequentialCommandGroup):
    DEFAULT = True

    def __init__(self, drivetrain, drive, max_angular_rate, auton_operator, elevator, arm, shooter):

        super().__init__(
            auton_operator.auton_simple_1(),
            drivetrain.apply_request(
                lambda: (
                    drive
                    .with_velocity_x(
                        -0.7
                    )
                )
            ).withTimeout(2),
            drivetrain.apply_request(
                lambda: (
                    drive
                    .with_velocity_x(
                        0
                    )
                )
            ).withTimeout(0),
            WaitCommand(1.0),
            auton_operator.auton_simple_2()
        )

    def end(self, interrupted):
        print(f"***** AUTON ABR End")

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
