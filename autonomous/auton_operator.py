from commands2 import SubsystemBase, Command, SequentialCommandGroup, ParallelRaceGroup, ConditionalCommand, \
    InstantCommand, WaitCommand, ParallelCommandGroup
from constants import CON_ELEV, CON_ARM, CON_SHOOT


class AutonOperator(SubsystemBase):

    def __init__(self, elevator, arm, shooter, climber):
        print(f"***** AUTON OP I")
        super().__init__()

        self.elevator = elevator
        self.arm = arm
        self.shooter = shooter

    def shoot(self, level: int) -> Command:

        class ShootSequence(SequentialCommandGroup):
            def __init__(self, level, elevator, arm, shooter):
                print(f"***** AUTON OP SHOOT: {level}")
                super().__init__()

                # Cancel any commands currently scheduled for these subsystems
                self.addRequirements(elevator, arm, shooter)

                self.elevator = elevator
                self.arm = arm
                self.shooter = shooter

                arm_safe_pos = CON_ARM["move"]
                arm_rotate_safe_cmd = self.arm.go_to_position(arm_safe_pos)
                hold_strength = CON_SHOOT["low"]

                flip_angle = None

                # Determine the correct height based on level
                if level == 2:
                    target_height = CON_ELEV["level_2"]
                    target_angle = CON_ARM["level_23"]
                    shot_strength = CON_SHOOT["high"]
                elif level == 3:
                    target_height = CON_ELEV["level_3"]
                    target_angle = CON_ARM["level_23"]
                    shot_strength = CON_SHOOT["high"]
                elif level == 4:
                    target_height = CON_ELEV["level_4"]
                    target_angle = CON_ARM["level_4"]
                    shot_strength = CON_SHOOT["high"]
                else:
                    print("Invalid input. Expected 2, 3, or 4.")
                    return

                # Create commands
                elev_up_cmd = self.elevator.go_to_position(target_height)  # Move elevator
                arm_rotate_shot_cmd = self.arm.go_to_position(target_angle)  # Turn wrist

                def stop_shooter_condition():
                    return self.elevator.at_target_position(target_height) and self.arm.at_target_position(target_angle)

                hold_piece_cmd = self.shooter.shoot(hold_strength, 'hold',
                                                    stop_condition=stop_shooter_condition)  # Shoot piece
                shoot_piece_cmd = self.shooter.shoot(shot_strength, 'shoot')

                move_up_cmd_set = SequentialCommandGroup(
                    arm_rotate_safe_cmd,
                    elev_up_cmd,
                    arm_rotate_shot_cmd
                )

                move_elevator_and_arm = ParallelRaceGroup(
                    # hold_piece_cmd,
                    move_up_cmd_set
                )

                full_cmd_set = [
                    move_elevator_and_arm,
                    shoot_piece_cmd
                ]

                if flip_angle is not None:
                    arm_flip_cmd = self.arm.go_to_position(flip_angle)
                    full_cmd_set.append(arm_flip_cmd)

                    # Run commands in sequence
                self.addCommands(*full_cmd_set)

        return ShootSequence(level, self.elevator, self.arm, self.shooter)

    def intake(self) -> Command:

        class IntakeSequence(SequentialCommandGroup):
            def __init__(self, elevator, arm):
                super().__init__()

                self.elevator = elevator
                self.arm = arm

                arm_safe_pos = CON_ARM["move"]
                arm_rotate_safe_cmd = self.arm.go_to_position(arm_safe_pos)

                target_height = CON_ELEV["intake"]
                target_angle = CON_ARM["intake"]

                # Create commands
                elev_up_cmd = self.elevator.go_to_position(target_height)  # Move elevator
                arm_rotate_receive_cmd = self.arm.go_to_position(target_angle)  # Turn wrist

                # Run commands in sequence
                self.addCommands(
                    arm_rotate_safe_cmd,
                    elev_up_cmd,
                    arm_rotate_receive_cmd
                )

        return IntakeSequence(self.elevator, self.arm)

    def hard_hold(self) -> Command:

        class HardHoldSequence(SequentialCommandGroup):
            def __init__(self, elevator, arm):
                super().__init__()

                self.elevator = elevator
                self.arm = arm

                arm_safe_pos = CON_ARM["move"]
                arm_rotate_safe_cmd = self.arm.go_to_position(arm_safe_pos)
                arm_hard_hold_pos = CON_ARM["hard_hold"]
                arm_hard_hold_kP = CON_ARM["hard_hold_kP"]
                arm_hard_hold_cmd = self.arm.go_to_position(arm_hard_hold_pos, arm_hard_hold_kP)

                target_height = CON_ELEV["min"]
                elev_up_cmd = self.elevator.go_to_position(target_height)  # Move elevator

                move_elevator_and_arm = ParallelRaceGroup(
                    elev_up_cmd,
                    arm_rotate_safe_cmd
                )

                # Run commands in sequence
                self.addCommands(
                    move_elevator_and_arm,
                    arm_hard_hold_cmd
                )

        return HardHoldSequence(self.elevator, self.arm)

    def auton_simple_1(self) -> Command:

        class AutonSimple1Sequence(ParallelRaceGroup):
            def __init__(self, arm, shooter):
                super().__init__()

                self.arm = arm
                self.shooter = shooter

                arm_pos = CON_ARM["level_1"]
                arm_rotate_cmd = self.arm.go_to_position(arm_pos)
                hold_strength = CON_SHOOT["low"]

                hold_piece_cmd = self.shooter.shoot(hold_strength, 'hold')

                self.addCommands(
                    arm_rotate_cmd,
                    hold_piece_cmd
                )

        return AutonSimple1Sequence(self.arm, self.shooter)

    def auton_simple_2(self) -> Command:

        class AutonSimple2Sequence(SequentialCommandGroup):
            def __init__(self, arm, shooter):
                super().__init__()

                self.arm = arm
                self.shooter = shooter

                arm_pos = CON_ARM["level_1"]
                arm_rotate_cmd = self.arm.go_to_position(arm_pos)
                flip_angle = CON_ARM["level_1_flip"]
                arm_flip_cmd = self.arm.go_to_position(flip_angle)
                shot_strength = CON_SHOOT["very_low"]

                # Shoot piece
                shoot_piece_cmd = self.shooter.shoot(shot_strength, 'shoot', None, "shoot_duration_long")

                self.addCommands(
                    arm_rotate_cmd,
                    shoot_piece_cmd,
                    WaitCommand(0.5),
                    arm_flip_cmd
                )

        return AutonSimple2Sequence(self.arm, self.shooter)


def periodic(self):
    """Periodic update function for telemetry and monitoring."""
