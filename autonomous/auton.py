from commands2 import Command

class AutonBlueLeft(Command):

    def __init__(self):
        super().__init__()
        # Add subsystem dependencies here if needed

    def initialize(self):
        print("Starting Auto B L")

    def execute(self):
        # Add movement logic (e.g., drive forward, turn, etc.)
        pass

    def isFinished(self):
        return True  # Modify based on your sequence duration

    def end(self, interrupted):
        print("Auto B L ended")


class AutonBlueRight(Command):

    def __init__(self, drivetrain, drive, max_angular_rate, shooter):
        super().__init__()
        self.drivetrain = drivetrain
        self.drive = drive
        self.max_angular_rate = max_angular_rate
        self.addRequirements(self.drivetrain)
        self.shooter = shooter

    def initialize(self):
        print(f"***** ABR I")

    def execute(self):
        print(f"***** ABR Executing")
        return self.shooter.shoot(1, 'shoot')

        # # Create a new drive request with a rotation rate
        # updated_drive_request = self.drive.with_rotational_rate(-0.3 * self.max_angular_rate)
        #
        # # Print the applied rotation rate
        # print(f"***** ABR Drive Request: Rotational Rate = {-0.3 * self.max_angular_rate}")
        #
        # # Debug: Check if the updated_drive_request actually contains the rate
        # print(f"***** Updated Drive Request: {updated_drive_request.__dict__}")
        #
        # # Apply the request to the drivetrain
        # self.drivetrain.apply_request(updated_drive_request)

    def isFinished(self):
        return False

    def end(self, interrupted):
        print("Auto B R ended")
