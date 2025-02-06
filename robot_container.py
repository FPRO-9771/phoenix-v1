import math
from commands2 import InstantCommand, PrintCommand, Command, CommandScheduler, SequentialCommandGroup, RunCommand
from commands2.button import Trigger
from wpilib import XboxController
from wpilib.event import EventLoop
from wpimath.geometry import Pose2d, Rotation2d, Translation2d
from phoenix6 import utils
from phoenix6.swerve import requests, swerve_module
from subsystems.arm import Arm
from subsystems.command_swerve_drivetrain import CommandSwerveDrivetrain
from subsystems.elevator import Elevator
from subsystems.shooter import Shooter
from telemetry import Telemetry
from generated import tuner_constants
from commands2.button import JoystickButton
from subsystems.rotate_to_april_tag import RotateToAprilTag
from handlers.limelight_handler import LimelightHandler
from commands2 import (
    CommandScheduler, 
    InstantCommand, 
    SequentialCommandGroup,
    WaitCommand,
    RepeatCommand,
    PrintCommand
)
import time

class RobotContainer:

    def __init__(self):
        """Initialize the RobotContainer and configure bindings."""
        self.max_speed = tuner_constants.k_speed_at_12_volts_mps  # Top speed
        self.max_angular_rate = 1.5 * math.pi  # Max angular velocity (3/4 rotation per second)
        self.last_rotation_time = 0

        # Initialize two controllers
        self.controller_driver = XboxController(0)    # Driver controller for driving/vision
        self.controller_operator = XboxController(1)  # Operator controller for mechanisms

        # Initialize subsystems
        self.drivetrain = tuner_constants.DriveTrain
        self.limelight_handler = LimelightHandler(debug=True)
        self.elevator = Elevator(motor_id=15, range_sensor_id=20)  # Use your actual CAN IDs
        self.arm = Arm(16)
        self.shooter = Shooter(17)

        # Swerve requests
        self.drive = requests.FieldCentric() \
            .with_deadband(self.max_speed * 0.1) \
            .with_rotational_deadband(self.max_angular_rate * 0.1) \
            .with_drive_request_type(swerve_module.SwerveModule.DriveRequestType.OPEN_LOOP_VOLTAGE)

        self.brake = requests.SwerveDriveBrake()
        self.point = requests.PointWheelsAt()

        # Telemetry
        self.logger = Telemetry(self.max_speed)
        self.event_loop = EventLoop()

        # Speed ratio for drivetrain
        self.speed_ratio = 1

        # If in simulation, seed_field_centric position
        if utils.is_simulation():
            self.drivetrain.seed_field_centric()

        # Register telemetry
        self.drivetrain.register_telemetry(self.logger.telemeterize)

        self.configure_bindings()

    def configure_bindings(self):
        """Configure button-to-command mappings."""
        self.configure_driver_controls()
        self.configure_operator_controls()

    def configure_driver_controls(self):
        """Configure driver controller bindings (driving and vision)."""
        # Drivetrain default command
        self.drivetrain.setDefaultCommand(
            self.drivetrain.apply_request(lambda: self.drive
                .with_velocity_x(-self.controller_driver.getLeftY() * self.max_speed * self.speed_ratio)
                .with_velocity_y(-self.controller_driver.getLeftX() * self.max_speed * self.speed_ratio)
            )
        )

        # Driver buttons
        x_button_driver = JoystickButton(self.controller_driver, XboxController.Button.kX)
        left_bumper_driver = JoystickButton(self.controller_driver, XboxController.Button.kLeftBumper)
        b_button_driver = JoystickButton(self.controller_driver, XboxController.Button.kB)
        a_button_driver = JoystickButton(self.controller_driver, XboxController.Button.kA)

        # Driver controls
        x_button_driver.whileTrue(RotateToAprilTag(self.drive, self.limelight_handler, self.max_angular_rate))
        left_bumper_driver.onTrue(InstantCommand(lambda: self.drivetrain.seed_field_centric()))
        b_button_driver.onTrue(InstantCommand(lambda: self.set_speed_ratio(0.25)))
        b_button_driver.onFalse(InstantCommand(lambda: self.set_speed_ratio(1)))
        a_button_driver.whileTrue(
            InstantCommand(
                lambda: self.drivetrain.apply_request(
                    lambda: self.drive.with_rotational_rate(.5 * self.max_angular_rate)
                )
            )
        )

    def configure_operator_controls(self):
        """Configure operator controller bindings (mechanisms)."""
        # Elevator buttons
        x_button = JoystickButton(self.controller_operator, XboxController.Button.kX)
        y_button = JoystickButton(self.controller_operator, XboxController.Button.kY)
        a_button = JoystickButton(self.controller_operator, XboxController.Button.kA)
        b_button = JoystickButton(self.controller_operator, XboxController.Button.kB)

        # Elevator controls
        x_button.onTrue(self.elevator.go_to_height(self.elevator.preset_heights[XboxController.Button.kX]))
        y_button.onTrue(self.elevator.go_to_height(self.elevator.preset_heights[XboxController.Button.kY]))
        a_button.onTrue(self.elevator.go_to_height(self.elevator.preset_heights[XboxController.Button.kA]))
        b_button.onTrue(self.elevator.go_to_height(self.elevator.preset_heights[XboxController.Button.kB]))

        # Arm controls
        left_bumper = JoystickButton(self.controller_operator, XboxController.Button.kLeftBumper)
        right_bumper = JoystickButton(self.controller_operator, XboxController.Button.kRightBumper)
        left_trigger = Trigger(lambda: self.controller_operator.getLeftTriggerAxis() > 0.5)
        right_trigger = Trigger(lambda: self.controller_operator.getRightTriggerAxis() > 0.5)

        left_bumper.onTrue(self.arm.go_to_angle(self.arm.preset_angles[XboxController.Button.kLeftBumper]))
        right_bumper.onTrue(self.arm.go_to_angle(self.arm.preset_angles[XboxController.Button.kRightBumper]))
        left_trigger.onTrue(self.arm.go_to_angle(45.0))
        right_trigger.onTrue(self.arm.go_to_angle(135.0))

        # Shooter controls
        back_button = JoystickButton(self.controller_operator, XboxController.Button.kBack)
        self.shooter.set_speed_percentage(0.75)
        back_button.whileTrue(self.shooter.shoot())  # Moved shooter to back button

        # Default commands
        self.arm.setDefaultCommand(self.arm.hold_position())

    def set_speed_ratio(self, ratio):
        """Sets the speed ratio based on button press/release."""
        self.speed_ratio = ratio

    def get_autonomous_command(self) -> Command:
        """Return the autonomous command."""
        return RepeatCommand(
            SequentialCommandGroup(
                WaitCommand(10),
                InstantCommand(self.rotate_drivetrain),
                WaitCommand(1)
            )
        )

    def rotate_drivetrain(self):
        """Helper method to rotate the drivetrain."""
        rotation_request = self.drive.with_rotational_rate(.5 * self.max_angular_rate)
        self.drivetrain.apply_request(rotation_request)