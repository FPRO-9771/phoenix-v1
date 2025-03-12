from commands2 import SubsystemBase, Command, CommandScheduler, WaitCommand, SequentialCommandGroup, InstantCommand, \
    ParallelCommandGroup

from autonomous.auton_constants import INSTRUCTIONS_A

class AutonModes(SubsystemBase):

    def __init__(self, auton_drive, auton_operator):
        print(f"***** AUTON M I")
        super().__init__()

        self.auton_drive = auton_drive
        self.auton_operator = auton_operator

    def seek_and_shoot(self, target_tag_id=None) -> Command:
        class AutoSequence(SequentialCommandGroup):
            def __init__(self, auton_drive, auton_operator, _target_tag_id):
                super().__init__()

                self.auton_drive = auton_drive
                self.auton_operator = auton_operator

                get_ready_to_shoot = ParallelCommandGroup(
                    auton_drive.align_pipe('left'),
                    auton_operator.shoot(4, False)
                )

                full_cmd_set = [
                    auton_drive.limelight(_target_tag_id),
                    get_ready_to_shoot,
                    auton_operator.shoot(4, True, False),
                    # auton_operator.intake()
                ]

                self.addCommands(*full_cmd_set)

        return AutoSequence(self.auton_drive, self.auton_operator, target_tag_id)


    def full_auton(self, setting) -> Command:
        class AutoSequence(SequentialCommandGroup):
            def __init__(self, auton_drive, auton_operator):
                super().__init__()

                const = INSTRUCTIONS_A[setting]

                self.auton_drive = auton_drive
                self.auton_operator = auton_operator

                get_ready_to_shoot = ParallelCommandGroup(
                    auton_drive.align_pipe('left'),
                    auton_operator.shoot(4, False)
                )

                back_away_1 = ParallelCommandGroup(
                    auton_operator.intake(),
                    auton_drive.back_and_rotate(const["rotate1"])
                )

                full_cmd_set = [
                    auton_drive.limelight(const["shot1"]),
                    get_ready_to_shoot,
                    auton_operator.shoot(4, True, False),
                    back_away_1
                ]

                self.addCommands(*full_cmd_set)

        return AutoSequence(self.auton_drive, self.auton_operator)


    def align_pipe_debug(self, move=False, direction='left') -> Command:

        class AutoSequence(ParallelCommandGroup):
            def __init__(self, auton_drive, auton_operator, _move, _direction):
                super().__init__()

                self.auton_drive = auton_drive
                self.auton_operator = auton_operator

                if _move is False:
                    full_cmd_set = [
                        auton_drive.align_pipe("left", False),
                        auton_drive.align_pipe("right", False)
                    ]
                else:
                    full_cmd_set = [auton_drive.align_pipe(direction, True)]

                self.addCommands(*full_cmd_set)

        return AutoSequence(self.auton_drive, self.auton_operator, move, direction)

    def test_servo(self) -> Command:

        class AutoSequence(SequentialCommandGroup):
            def __init__(self, auton_drive, auton_operator):
                super().__init__()

                self.auton_drive = auton_drive
                self.auton_operator = auton_operator

                full_cmd_set = [
                    # auton_operator.hard_hold(),
                    auton_operator.shooter_lock()
                ]

                self.addCommands(*full_cmd_set)

        return AutoSequence(self.auton_drive, self.auton_operator)

    def test_auton(self) -> Command:

        class AutoSequence(SequentialCommandGroup):
            def __init__(self, auton_drive, auton_operator):
                super().__init__()

                self.auton_drive = auton_drive
                self.auton_operator = auton_operator

                full_cmd_set = [
                    # auton_operator.hard_hold(),
                    auton_drive.back_and_rotate(3.5)
                ]

                self.addCommands(*full_cmd_set)

        return AutoSequence(self.auton_drive, self.auton_operator)

    # def test_timer_auto(self) -> Command:
    #
    #     class AutoSequence(SequentialCommandGroup):
    #         def __init__(self, auton_drive, auton_operator):
    #             super().__init__()
    #
    #             self.auton_drive = auton_drive
    #             self.auton_operator = auton_operator
    #
    #             full_cmd_set = [
    #                 auton_drive.approach_target(),
    #                 WaitCommand(1),
    #                 auton_operator.shoot(3)
    #             ]
    #
    #             self.addCommands(*full_cmd_set)
    #
    #     return AutoSequence(self.auton_drive, self.auton_operator)
    #
    def test_ll_data(self, target_tag_id=None) -> Command:

        class AutoSequence(SequentialCommandGroup):
            def __init__(self, auton_drive, auton_operator, _target_tag_id):
                super().__init__()

                self.auton_drive = auton_drive
                self.auton_operator = auton_operator

                full_cmd_set = [
                    auton_drive.limelight_data(_target_tag_id)
                ]

                self.addCommands(*full_cmd_set)

        return AutoSequence(self.auton_drive, self.auton_operator, target_tag_id)

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
