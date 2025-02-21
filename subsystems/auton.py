from commands2 import SubsystemBase, Command, SequentialCommandGroup, InstantCommand
from wpilib import XboxController
from subsystems.elevator import Elevator

class Auton(SubsystemBase):
    """
    Elevator subsystem that controls vertical movement using a TalonFX motor.
    Uses CANrange sensor for height measurement.
    """
    
    def __init__(self):
        super().__init__()

    def shoot(self, level: int) -> Command:
        """Create a sequence to move elevator, turn wrist, and shoot piece."""

        class ShootSequence(SequentialCommandGroup):
            def __init__(self, level):
                super().__init__()

                self.elevator = Elevator()

                # Determine the correct height based on level
                if level == 2:
                    target_height = self.elevator.preset_rotations["level_2"]
                elif level == 3:
                    target_height = self.elevator.preset_rotations["level_3"]
                elif level == 4:
                    target_height = self.elevator.preset_rotations["level_4"]
                else:
                    print("Invalid input. Expected 2, 3, or 4.")
                    return

                # Create commands
                go_to_height_cmd = self.elevator.go_to_height(target_height)  # Move elevator
                turn_wrist_cmd = self.turn_wrist()  # Turn wrist
                shoot_piece_cmd = self.shoot_piece()  # Shoot piece

                # Run commands in sequence
                self.addCommands(
                    go_to_height_cmd,  # 1. Move elevator
                    # turn_wrist_cmd,  # 2. Turn wrist
                    # shoot_piece_cmd  # 3. Shoot piece
                )

            def turn_wrist(self):
                """Example wrist turning command."""
                return InstantCommand(lambda: print("Turning wrist..."), self)

            def shoot_piece(self):
                """Example shooting command."""
                return InstantCommand(lambda: print("Shooting piece..."), self)

        return ShootSequence(level)

    def periodic(self):
        """Periodic update function for telemetry and monitoring."""
