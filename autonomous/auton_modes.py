from commands2 import SubsystemBase, Command, CommandScheduler, WaitCommand, SequentialCommandGroup, ParallelRaceGroup

class AutonModes(SubsystemBase):

    def __init__(self, auton_drive, auton_operator):
        print(f"***** AUTON M I")
        super().__init__()

        self.auton_drive = auton_drive
        self.auton_operator = auton_operator

    def test_timer_auto(self) -> Command:

        class AutoSequence(SequentialCommandGroup):
            def __init__(self, auton_drive, auton_operator):
                super().__init__()

                self.auton_drive = auton_drive
                self.auton_operator = auton_operator

                full_cmd_set = [
                    auton_drive.approach_target(),
                    WaitCommand(1),
                    auton_operator.shoot(3)
                ]

                self.addCommands(*full_cmd_set)

        return AutoSequence(self.auton_drive, self.auton_operator)

    def test_ll_data(self) -> Command:

        class AutoSequence(SequentialCommandGroup):
            def __init__(self, auton_drive, auton_operator):
                super().__init__()

                self.auton_drive = auton_drive
                self.auton_operator = auton_operator

                full_cmd_set = [
                    auton_drive.limelight_data()
                ]

                self.addCommands(*full_cmd_set)

        return AutoSequence(self.auton_drive, self.auton_operator)


    def test_ll_auto(self) -> Command:

        class AutoSequence(SequentialCommandGroup):
            def __init__(self, auton_drive, auton_operator):
                super().__init__()

                self.auton_drive = auton_drive
                self.auton_operator = auton_operator

                get_ready_to_shoot = ParallelRaceGroup(
                    auton_drive.align_pipe('left'),
                    auton_operator.shoot(4, False)
                )

                full_cmd_set = [
                    auton_drive.limelight(),
                    get_ready_to_shoot,
                    auton_operator.shoot(4, True, False)
                ]

                self.addCommands(*full_cmd_set)

        return AutoSequence(self.auton_drive, self.auton_operator)


    def test_pa_auto(self) -> Command:

        class AutoSequence(SequentialCommandGroup):
            def __init__(self, auton_drive, auton_operator):
                super().__init__()

                self.auton_drive = auton_drive
                self.auton_operator = auton_operator

                full_cmd_set = [
                    auton_drive.align_pipe('left')
                ]

                self.addCommands(*full_cmd_set)

        return AutoSequence(self.auton_drive, self.auton_operator)

    def test_servo(self) -> Command:

        class AutoSequence(SequentialCommandGroup):
            def __init__(self, auton_drive, auton_operator):
                super().__init__()

                self.auton_drive = auton_drive
                self.auton_operator = auton_operator

                full_cmd_set = [
                    auton_operator.hard_hold(),
                    auton_operator.shooter_lock()
                ]

                self.addCommands(*full_cmd_set)

        return AutoSequence(self.auton_drive, self.auton_operator)

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