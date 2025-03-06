from commands2 import SubsystemBase, Command, CommandScheduler, WaitCommand, SequentialCommandGroup, StartEndCommand, RunCommand, InstantCommand

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

    def test_ll_auto(self) -> Command:

        class AutoSequence(SequentialCommandGroup):
            def __init__(self, auton_drive, auton_operator):
                super().__init__()

                self.auton_drive = auton_drive
                self.auton_operator = auton_operator

                full_cmd_set = [
                    auton_drive.limelight(),
                    WaitCommand(1),
                    auton_operator.shoot(3)
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