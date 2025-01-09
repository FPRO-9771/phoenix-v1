from commands2 import Command
from generated import tuner_constants

class RotateToAprilTag(Command):
# class RotateToAprilTag():
    def __init__(self, drive, limelight_handler, max_angular_rate):
        print("rotate_to_april_tag init")
        super().__init__()
        self.drivetrain = tuner_constants.DriveTrain
        self.drive = drive
        self.limelight_handler = limelight_handler
        self.max_angular_rate = max_angular_rate
        self.target_acquired = False

        # Declare subsystem dependencies
        self.addRequirements(self.drive)

    def initialize(self):
        """Called when the command is initially scheduled."""
        self.target_acquired = False
        print("rotate_to_april_tag initialized")

    def execute(self):
        """Called repeatedly when the command is scheduled."""
        result = self.limelight_handler.read_results()
        if result and result.validity:
            print("----- Target: Acquired")
            tx = result.fiducialResults[0].target_x_degrees
            print("----- Target: tx:", tx)
            
            if abs(tx) > 1.0:
                scaled_rotation = tx / 45
                rotation_rate = -scaled_rotation * self.max_angular_rate
                print("----- Scaled Rotation:", scaled_rotation)
                print("----- Rotation Rate:", rotation_rate)
                
                # Debug rotation request
                rotation_request = self.drive.with_rotational_rate(rotation_rate)
                print("----- Applying rotation request:", rotation_request)
                
                # Apply request directly to drivetrain
                self.drivetrain.apply_request(rotation_request)
                
            else:
                self.target_acquired = True
        else:
            print('----- Target: None Found')

    def isFinished(self):
        """Keep running until interrupted (button release)."""
        return False  # Never finish automatically, only stop on interruption

    def end(self, interrupted):
        """Called once the command ends or is interrupted."""
        print(f"rotate_to_april_tag ended, interrupted={interrupted}")
        self.drive.with_rotational_rate(0)  # Stop the drivetrain
