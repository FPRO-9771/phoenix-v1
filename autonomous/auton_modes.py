from commands2 import Command, CommandScheduler, WaitCommand, SequentialCommandGroup, StartEndCommand, RunCommand, InstantCommand
from constants import ELEVATOR_ROTATIONS, ARM_ROTATIONS, SHOOTER_STRENGTH


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


class AutonBlueRight(SequentialCommandGroup):
    DEFAULT = True

    def __init__(self, drivetrain, drive, max_angular_rate, shooter):

        # hold_piece_cmd = shooter.shoot(2, 'hold', stop_condition=stop_shooter_condition)  # Shoot piece
        # shoot_piece_cmd = shooter.shoot(2, 'shoot')

        super().__init__(
            shooter.shoot(SHOOTER_STRENGTH["high"], 'shoot'),  # ✅ Start shooter
            WaitCommand(1.0),
            drivetrain.apply_request(
                lambda: (
                    drive
                    .with_rotational_rate(
                        0.9
                    )  # Drive counterclockwise with negative X (left)
                )
            )

        )

    def end(self, interrupted):
        print(f"***** AUTON ABR End")
