from commands2 import Command
from phoenix6.swerve.requests import FieldCentric
from generated import tuner_constants
import math
from generated.tuner_constants import TunerConstants
import time

class DriveToAprilTagTest(Command):
    def __init__(self, drivetrain, speed):
        super().__init__()
        self.drivetrain = drivetrain  # Use drivetrain, not FieldCentric drive request
        self.speed = speed
        self.addRequirements(drivetrain)  # Ensure the command requires the drivetrain

    def initialize(self):
        print(f"🚀 DriveToAprilTag initialized with speed {self.speed}")

    def execute(self):
        # Apply a velocity in the Y direction (sideways movement)
        drive_request = self.drivetrain.drive.with_velocity_y(self.speed)  # Use drivetrain.drive
        self.drivetrain.apply_request(drive_request)

    def end(self, interrupted):
        print(f"🛑 DriveToAprilTag ended {'(interrupted)' if interrupted else ''}")
        # Stop the drivetrain when the command ends
        stop_request = self.drivetrain.drive.with_velocity_y(0)
        self.drivetrain.apply_request(stop_request)

    def isFinished(self):
        return False  # Keep running while the button is held

class RotateToAprilTag(Command):
# class RotateToAprilTag():
    def __init__(self, drive, limelight_handler, max_angular_rate):
        print("rotate_to_april_tag init")
        super().__init__()
        self.drivetrain = TunerConstants.create_drivetrain()
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
    def __init__(self, drivetrain, drive, limelight_handler, max_speed, max_angular_rate):
        print("drive_to_april_tag init")
        super().__init__()
        self.drivetrain = TunerConstants.create_drivetrain()
        self.drive = drive
        self.limelight_handler = limelight_handler
        self.max_speed = max_speed
        self.max_angular_rate = max_angular_rate
        self.target_acquired = False
        self.desired_distance = 2.0  # Desired distance in meters from April tag
        self.distance_threshold = 0.1  # How close we need to be to target distance (meters)
        self.angle_threshold = 1.0  # How centered we need to be (degrees)
        self.arrived_target = 0.22

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
            # tx = result.fiducialResults[0].target_x_degrees
            # print("-----1 Target: tx:", tx)
            # tx = result.fiducialResults[0].target_x_pixels
            # print("-----2 Target: tx:", tx)
            # tx = result.fiducialResults[0].target_y_degrees
            # print("-----3 Target: tx:", tx)
            # tx = result.fiducialResults[0].target_y_pixels
            # print("-----4 Target: tx:", tx)
            # tx = result.fiducialResults[0].target_area
            # print("-----5 Target: tx:", tx)
            # tx = result.fiducialResults[0].target_pose_robot_space
            # print("-----6 Target: tx:", tx)
            # tx = result.fiducialResults[0].target_pose_camera_space
            # print("-----7 Target: tx:", tx)
            # tx = result.fiducialResults[0].robot_pose_target_space
            # print("-----8 Target: tx:", tx)
            # tx = result.fiducialResults[0].robot_pose_field_space
            # print("-----9Target: tx:", tx)
            # tx = result.fiducialResults[0].camera_pose_target_space
            # print("-----10 Target: tx:", tx)
            # tx = result.fiducialResults[0].skew
            # print("-----11 Target: tx:", tx)
            # tx = result.fiducialResults[0].points
            # print("-----12 Target: tx:", tx)
            # tx = result.fiducialResults[0].family
            # print("-----13 Target: tx:", tx)
            # tx = result.fiducialResults[0].fiducial_id
            # print("-----14 Target: tx:", tx)

            print(f"-------")
            print(f"-------")

            # Get distance to target (in meters)
            target_area = result.fiducialResults[0].target_area
            print(f"------- t: {target_area}")

        #     target_pose = result.fiducialResults[0].robot_pose_target_space
        #     print(f"{result}")
        #     print(f"L O OO  K K  RI GHT T HERE RERE NOW OW{result.fiducialResults}")
        #     print(f"L O OO  K K  RI GHT T HERE RERE NOW OW{target_pose=}")
            arrived = target_area / self.arrived_target
            print(f"------- A: {arrived}")

        #
        #     # Calculate rotation rate
        #     rotation_rate = 0
        #     if abs(tx) > self.angle_threshold:
        #         scaled_rotation = tx / 45
        #         rotation_rate = -scaled_rotation * self.max_angular_rate
        #         print("----- Rotation Rate:", rotation_rate)
        #
            # Calculate forward speed
            forward_speed = 0
            distance_error = 1- arrived
            print(f"------- e: {distance_error}")
            if abs(distance_error) > 0:
                # Scale speed based on distance error, max out at max_speed
                # scaled_speed = min(abs(distance_error) / 2.0, 1.0)  # Divide by 2.0 to smooth approach
                forward_speed = distance_error * self.max_speed
                print(f"------- S: {forward_speed}")
            if abs(distance_error ) <= 0:
                forward_speed = 0
                print(f"You made it")

        #
            # Create and apply drive request
            # drive_request = (
            #     self.drive
            #     .with_velocity_x(-forward_speed)  # Negative because forward is negative in this system
            #     # .with_rotational_rate(rotation_rate)
            #     .build()
            # )
            print("----- Applying drive request")
            # self.drivetrain.apply_request(drive_request)

            # rotation_request = self.drive.with_rotational_rate(forward_speed)
            # print("----- Applying rotation request:", rotation_request)
            #
            # # Apply request directly to drivetrain
            # self.drivetrain.apply_request(rotation_request)

            print(f"Drive Object: {self.drive}")
            print(f"Drivetrain Object: {self.drivetrain}")


            self.drivetrain.apply_request(lambda: self.drive.with_velocity_y(3))

        #
        #     # Check if we've reached target
        #     if abs(distance_error) <= self.distance_threshold and abs(tx) <= self.angle_threshold:
        #         self.target_acquired = True
        #         print("----- Target Position Reached!")
        # else:
        #     print('----- Target: None Found')
        print(f"-------")
        print(f"-------")

    def isFinished(self):
        """Keep running until interrupted (button release)."""
        return False  # Never finish automatically, only stop on interruption

    def end(self, interrupted):
        """Called once the command ends or is interrupted."""
        print(f"drive_to_april_tag ended, interrupted={interrupted}")
        # Stop all movement
        stop_request = self.drive.with_velocity_x(0).with_rotational_rate(0)
        self.drivetrain.apply_request(stop_request)