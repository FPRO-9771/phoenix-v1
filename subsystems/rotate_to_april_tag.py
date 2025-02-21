from commands2 import Command
from generated import tuner_constants
import math

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


class DriveToAprilTag(Command):
    def __init__(self, drive, limelight_handler, max_speed, max_angular_rate):
        print("drive_to_april_tag init")
        super().__init__()
        self.drivetrain = tuner_constants.DriveTrain
        self.drive = drive
        self.limelight_handler = limelight_handler
        self.max_speed = max_speed
        self.max_angular_rate = max_angular_rate
        self.target_acquired = False
        self.desired_distance = 2.0  # Desired distance in meters from April tag
        self.distance_threshold = 0.1  # How close we need to be to target distance (meters)
        self.angle_threshold = 1.0  # How centered we need to be (degrees)

        # Declare subsystem dependencies
        self.addRequirements(self.drive)

    def initialize(self):
        """Called when the command is initially scheduled."""
        self.target_acquired = False
        print("drive_to_april_tag initialized")

    def execute(self):
        """Called repeatedly when the command is scheduled."""
        result = self.limelight_handler.read_results()
        if result and result.validity and result.fiducialResults:
            print("----- Target: Acquired")
            
            # Get horizontal angle to target
            tx = result.fiducialResults[0].target_x_degrees
            print("----- Target: tx:", tx)
            
            # Get distance to target (in meters)
            target_pose = result.fiducialResults[0].robot_pose_target_space
            current_distance = math.sqrt(target_pose[0]**2 + target_pose[2]**2)  # Using X and Z components
            print("----- Target: distance:", current_distance)
            
            # Calculate rotation rate
            rotation_rate = 0
            if abs(tx) > self.angle_threshold:
                scaled_rotation = tx / 45
                rotation_rate = -scaled_rotation * self.max_angular_rate
                print("----- Rotation Rate:", rotation_rate)
            
            # Calculate forward speed
            forward_speed = 0
            distance_error = current_distance - self.desired_distance
            if abs(distance_error) > self.distance_threshold:
                # Scale speed based on distance error, max out at max_speed
                scaled_speed = min(abs(distance_error) / 2.0, 1.0)  # Divide by 2.0 to smooth approach
                forward_speed = math.copysign(scaled_speed * self.max_speed, distance_error)
                print("----- Forward Speed:", forward_speed)
            
            # Create and apply drive request
            drive_request = (
                self.drive
                .with_velocity_x(-forward_speed)  # Negative because forward is negative in this system
                .with_rotational_rate(rotation_rate)
            )
            print("----- Applying drive request")
            self.drivetrain.apply_request(drive_request)
            
            # Check if we've reached target
            if abs(distance_error) <= self.distance_threshold and abs(tx) <= self.angle_threshold:
                self.target_acquired = True
                print("----- Target Position Reached!")
        else:
            print('----- Target: None Found')

    def isFinished(self):
        """Keep running until interrupted (button release)."""
        return False  # Never finish automatically, only stop on interruption

    def end(self, interrupted):
        """Called once the command ends or is interrupted."""
        print(f"drive_to_april_tag ended, interrupted={interrupted}")
        # Stop all movement
        stop_request = self.drive.with_velocity_x(0).with_rotational_rate(0)
        self.drivetrain.apply_request(stop_request)