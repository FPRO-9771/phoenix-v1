from commands2 import Command, CommandScheduler, WaitCommand, SequentialCommandGroup, StartEndCommand, RunCommand, \
    InstantCommand
from constants import CON_ELEV, CON_ARM, CON_SHOOT
from autonomous.auton_constants import INSTRUCTIONS
from autonomous.auton_drive import AutonDrive

from generated.tuner_constants import TunerConstants
from phoenix6 import swerve
from wpilib import Timer

# from subsystems.shooter import Shooter

class Leave(SequentialCommandGroup):


    def __init__(self, drivetrain, drive):

        super().__init__(
            drivetrain.seed_field_centric(),
            WaitCommand(0.5),
            drivetrain.apply_request(
                lambda: (
                    drive
                    .with_velocity_x(
                        INSTRUCTIONS["leave"]["drive1_v_x"]
                    )
                )
            ).withTimeout(INSTRUCTIONS["leave"]["drive1_timeout"]),
            drivetrain.apply_request(
                lambda: (
                    drive
                    .with_velocity_x(
                        0
                    )
                )
            ).withTimeout(0)
        )

    def end(self, interrupted):
        print(f"***** AUTON LEAVE End")

class ShootSides(SequentialCommandGroup):

    def __init__(self, drivetrain, drive, auton_operator):

        super().__init__(
            drivetrain.seed_field_centric(),
            WaitCommand(0.5),
            auton_operator.auton_simple_1(),
            drivetrain.apply_request(
                lambda: (
                    drive
                    .with_velocity_x(
                        INSTRUCTIONS["shoot_sides"]["drive1_v_x"]
                    )
                )
            ).withTimeout(INSTRUCTIONS["shoot_sides"]["drive1_timeout"]),
            drivetrain.apply_request(
                lambda: (
                    drive
                    .with_velocity_x(
                        0
                    )
                )
            ).withTimeout(0),
            WaitCommand(1.0),
            auton_operator.auton_simple_2(),
            WaitCommand(1.0)
        )

    def end(self, interrupted):
        print(f"***** AUTON SHOOT Left End")

class ShootCenter(SequentialCommandGroup):
    DEFAULT = True

    def __init__(self, drivetrain, drive, auton_operator):

        super().__init__(
            drivetrain.seed_field_centric(),
            WaitCommand(0.5),
            auton_operator.auton_simple_1(),
            drivetrain.apply_request(
                lambda: (
                    drive
                    .with_velocity_x(
                        INSTRUCTIONS["shoot_center"]["drive1_v_x"]
                    )
                )
            ).withTimeout(INSTRUCTIONS["shoot_center"]["drive1_timeout"]),
            drivetrain.apply_request(
                lambda: (
                    drive
                    .with_velocity_x(
                        0
                    )
                )
            ).withTimeout(0),
            WaitCommand(1.0),
            drivetrain.apply_request(
                lambda: (
                    drive
                    .with_velocity_y(
                        INSTRUCTIONS["shoot_center"]["drive2_v_y"]
                    )
                )
            ).withTimeout(INSTRUCTIONS["shoot_center"]["drive2_timeout"]),
            drivetrain.apply_request(
                lambda: (
                    drive
                    .with_velocity_y(
                        0
                    )
                )
            ).withTimeout(0),
            WaitCommand(0.5),
            auton_operator.auton_simple_2(),
            WaitCommand(1.0),
        )

    def end(self, interrupted):
        print(f"***** AUTON SHOOT Center End")



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
