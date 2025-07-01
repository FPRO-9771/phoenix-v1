from commands2 import SubsystemBase, Command, CommandScheduler, WaitCommand, SequentialCommandGroup, InstantCommand, \
    ParallelCommandGroup

from autonomous.auton_constants import INSTRUCTIONS_A, INSTRUCTIONS_MOVES


class AutonModes(SubsystemBase):

    def __init__(self, auton_drive, auton_operator):
        print(f"***** AUTON M I")
        super().__init__()

        self.auton_drive = auton_drive
        self.auton_operator = auton_operator

    def seek_and_shoot(self, target_tag_id=None, direction="left") -> Command:
        class AutoSequence(SequentialCommandGroup):
            def __init__(self, auton_drive, auton_operator, _target_tag_id, _direction):
                super().__init__()

                self.auton_drive = auton_drive
                self.auton_operator = auton_operator

                get_ready_to_shoot = ParallelCommandGroup(
                    auton_drive.align_pipe(direction, True),
                    auton_operator.shoot(4, False)
                )

                full_cmd_set = [
                    auton_drive.limelight(_target_tag_id),
                    get_ready_to_shoot,
                    auton_operator.shoot(4, True, False),
                    # auton_operator.intake()
                ]

                self.addCommands(*full_cmd_set)

        return AutoSequence(self.auton_drive, self.auton_operator, target_tag_id, direction)

    def full_auton(self, setting) -> Command:
        class AutoSequence(SequentialCommandGroup):
            def __init__(self, auton_drive, auton_operator):
                super().__init__()

                self.auton_drive = auton_drive
                self.auton_operator = auton_operator

                leave = None
                move_towards_intake_drive = None

                const = INSTRUCTIONS_A[setting]

                moves = INSTRUCTIONS_MOVES[const["moves"]]

                if "move0" in moves:
                    moves0 = moves['move0']
                    leave = auton_drive.drive_with_instructions(
                        moves0['speed_x'], moves0['speed_y'], moves0['rotation'],
                        moves0['time'], None
                    )

                if "move1" in moves and "move2" in moves:
                    moves1 = moves['move1']
                    moves2 = moves['move2']

                    move_towards_intake_drive = SequentialCommandGroup(
                        auton_drive.drive_with_instructions(
                            moves1['speed_x'], moves1['speed_y'], moves1['rotation'], moves1['time'], None
                        ),
                        auton_drive.drive_with_instructions(
                            moves2['speed_x'], moves2['speed_y'], moves2['rotation'], moves2['time'], None
                        ),
                    )

                appr_in = INSTRUCTIONS_MOVES["approach"]["in"]
                # appr_in_2 = INSTRUCTIONS_MOVES["approach"]["in2"]
                appr_in_3 = INSTRUCTIONS_MOVES["approach"]["in3"]
                appr_out1 = INSTRUCTIONS_MOVES["approach"]["out1"]
                appr_out2 = INSTRUCTIONS_MOVES["approach"]["out2"]



                move_towards_intake = ParallelCommandGroup(
                    auton_operator.intake(),
                    move_towards_intake_drive
                )

                drive_to_intake = ParallelCommandGroup(
                    auton_drive.drive_with_instructions(
                        appr_in["speed_x"], appr_in["speed_y"], appr_in["rotation"], appr_in["time"],
                        appr_in["sensor_stop_distance"]
                    ),
                    auton_operator.hard_hold(),
                )

                leave_intake = ParallelCommandGroup(
                    auton_operator.hard_hold(),
                    auton_drive.drive_with_instructions(
                        appr_out1["speed_x"], appr_out1["speed_y"], appr_out1["rotation"], appr_out1["time"],
                        appr_out1["sensor_stop_distance"]
                    ),
                )

                get_ready_to_shoot = ParallelCommandGroup(
                    auton_drive.align_pipe('left'),
                    auton_operator.shoot(4, False)
                )

                shot_1_cmd_set = [
                    leave,
                    auton_drive.limelight(const["shot1"]),
                    get_ready_to_shoot,
                    auton_operator.shoot(4, True, False),
                ]

                full_cmd_set = shot_1_cmd_set.copy()

                # Conditionally add the following command set if "intake" exists in const
                if "intake" in const:
                    following_cmd_set = [
                        move_towards_intake,
                        auton_drive.limelight(const["intake"], True),
                        drive_to_intake,
                        auton_drive.drive_with_instructions(
                            appr_in_3["speed_x"], appr_in_3["speed_y"], appr_in_3["rotation"], appr_in_3["time"],
                            appr_in_3["sensor_stop_distance"]
                        ),
                        auton_operator.intake_with_shooter(),
                        # leave_intake,
                        # auton_drive.drive_with_instructions(
                        #     appr_out2["speed_x"], appr_out2["speed_y"], appr_out2["rotation"], appr_out2["time"],
                        #     appr_out2["sensor_stop_distance"]
                        # ),
                        # auton_drive.limelight(const["shot2"]),
                        # get_ready_to_shoot,
                        # auton_operator.shoot(4, True, False),
                    ]

                    full_cmd_set.extend(following_cmd_set)

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
