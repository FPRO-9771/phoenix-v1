import commands2
import commands2.button
from commands2.button import Trigger
import commands2.cmd
from commands2.sysid import SysIdRoutine

from generated.tuner_constants import TunerConstants
from telemetry import Telemetry

from phoenix6 import swerve
from wpimath.geometry import Rotation2d
from wpimath.units import rotationsToRadians

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
from generated.tuner_constants import TunerConstants
from commands2.button import JoystickButton
from subsystems.rotate_to_april_tag import RotateToAprilTag
from subsystems.drive_to_april_tag import DriveToAprilTag  # Add this import
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
        super().__init__()
        
        # Initialize speeds
        self._max_speed = TunerConstants.speed_at_12_volts
        self._max_angular_rate = rotationsToRadians(0.75)
        
        try:
            # Initialize controllers
            self.controller_driver = commands2.button.CommandXboxController(0)
            self.controller_operator = commands2.button.CommandXboxController(1)
        except Exception as e:
            print(f"Warning: Error initializing controllers: {e}")
            print("Make sure controllers are connected before starting the robot.")
            # Create dummy controllers to prevent crashes
            self.controller_driver = None
            self.controller_operator = None

        # Initialize subsystems
        self.limelight_handler = LimelightHandler(debug=True)
        self.elevator = Elevator(motor_id=20, follower_motor_id=21, range_sensor_id=41)
        self.arm = Arm(22)
        self.shooter = Shooter(23)

        # Initialize drive controls
        self._drive = (
            swerve.requests.FieldCentric()
            .with_deadband(self._max_speed * 0.1)
            .with_rotational_deadband(self._max_angular_rate * 0.1)
            .with_drive_request_type(swerve.SwerveModule.DriveRequestType.OPEN_LOOP_VOLTAGE)
        )
        self._brake = swerve.requests.SwerveDriveBrake()
        self._point = swerve.requests.PointWheelsAt()

        self._logger = Telemetry(self._max_speed)
        self.drivetrain = TunerConstants.create_drivetrain()

        # Configure bindings if controllers are available
        if self.controller_driver and self.controller_operator:
            self.configure_bindings()

    def configure_bindings(self):
        """Configure button-to-command mappings."""
        self.configure_driver_controls()
        self.configure_operator_controls()

    def configure_driver_controls(self):
        """Configure driver controller bindings (driving and vision)."""
        try:
            # Drivetrain default command
            self.drivetrain.setDefaultCommand(
                self.drivetrain.apply_request(
                    lambda: (
                        self._drive.with_velocity_x(
                            -self.controller_driver.getLeftY() * self._max_speed
                        )
                        .with_velocity_y(
                            -self.controller_driver.getLeftX() * self._max_speed
                        )
                        .with_rotational_rate(
                            -self.controller_driver.getRightX() * self._max_angular_rate
                        )
                    )
                )
            )

            # Basic drivetrain controls
            self.controller_driver.a().whileTrue(
                self.drivetrain.apply_request(lambda: self._brake)
            )
            self.controller_driver.b().whileTrue(
                self.drivetrain.apply_request(
                    lambda: self._point.with_module_direction(
                        Rotation2d(-self.controller_driver.getLeftY(), -self.controller_driver.getLeftX())
                    )
                )
            )

            # Reset field-centric heading
            self.controller_driver.leftBumper().onTrue(
                self.drivetrain.runOnce(lambda: self.drivetrain.seed_field_centric())
            )

            # Driver buttons for April Tag functionality
            x_button_driver = self.controller_driver.x()
            y_button_driver = self.controller_driver.y()
            
            # X button rotates to face April tag
            x_button_driver.whileTrue(
                RotateToAprilTag(self._drive, self.limelight_handler, self._max_angular_rate)
            )
            
            # Y button drives to April tag
            y_button_driver.whileTrue(
                DriveToAprilTag(self._drive, self.limelight_handler, self._max_speed, self._max_angular_rate)
            )

            # SysId routines
            (self.controller_driver.back() & self.controller_driver.y()).whileTrue(
                self.drivetrain.sys_id_dynamic(SysIdRoutine.Direction.kForward)
            )
            (self.controller_driver.back() & self.controller_driver.x()).whileTrue(
                self.drivetrain.sys_id_dynamic(SysIdRoutine.Direction.kReverse)
            )
            (self.controller_driver.start() & self.controller_driver.y()).whileTrue(
                self.drivetrain.sys_id_quasistatic(SysIdRoutine.Direction.kForward)
            )
            (self.controller_driver.start() & self.controller_driver.x()).whileTrue(
                self.drivetrain.sys_id_quasistatic(SysIdRoutine.Direction.kReverse)
            )

        except Exception as e:
            print(f"Warning: Error configuring driver controls: {e}")
            print("Make sure all controllers are properly connected.")

    def configure_operator_controls(self):
        """Configure operator controller bindings (mechanisms)."""
        try:
            # Elevator preset height buttons
            a_button = self.controller_operator.a()
            b_button = self.controller_operator.b()
            x_button = self.controller_operator.x()
            y_button = self.controller_operator.y()

            # Map buttons to preset heights
            a_button.onTrue(self.elevator.go_to_height(self.elevator.PRESET_HEIGHTS['ZERO']))
            b_button.onTrue(self.elevator.go_to_height(self.elevator.PRESET_HEIGHTS['LOW']))
            x_button.onTrue(self.elevator.go_to_height(self.elevator.PRESET_HEIGHTS['MEDIUM']))
            y_button.onTrue(self.elevator.go_to_height(self.elevator.PRESET_HEIGHTS['HIGH']))

            # Manual elevator control using left stick Y-axis
            Trigger(lambda: abs(self.controller_operator.getLeftY()) > 0.1).whileTrue(
                RunCommand(
                    lambda: self.elevator.motor.set(-self.controller_operator.getLeftY() * 0.5),
                    self.elevator
                ).beforeEnd(lambda: self.elevator.stop())
            )

            # Emergency stop for elevator
            self.controller_operator.leftBumper().onTrue(
                InstantCommand(lambda: self.elevator.stop(), self.elevator)
            )

        except Exception as e:
            print(f"Warning: Error configuring operator controls: {e}")
            print("Make sure all controllers are properly connected.")

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