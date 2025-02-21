
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
# from subsystems.shooter import Shooter
from subsystems.auton import Auton
from telemetry import Telemetry
from generated.tuner_constants import TunerConstants
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
        self._max_speed = (
            TunerConstants.speed_at_12_volts
        )  # speed_at_12_volts desired top speed
        self._max_angular_rate = rotationsToRadians(
            0.75
        )  # 3/4 of a rotation per second max angular velocity

        # Initialize two controllers
        self.controller_driver = commands2.button.CommandXboxController(0)    # Driver controller for driving/vision
        self.controller_operator = commands2.button.CommandXboxController(1)  # Operator controller for mechanisms

        # Initialize subsystems
        self.limelight_handler = LimelightHandler(debug=True)
        self.elevator = Elevator()  # Use your actual CAN IDs
        self.arm = Arm(22, 50, 300)
        # self.shooter = Shooter(300)
        self.auton = Auton()

        # Setting up bindings for necessary control of the swerve drive platform
        self._drive = (
            swerve.requests.FieldCentric()
            .with_deadband(self._max_speed * 0.1)
            .with_rotational_deadband(
                self._max_angular_rate * 0.1
            )  # Add a 10% deadband
            .with_drive_request_type(
                swerve.SwerveModule.DriveRequestType.OPEN_LOOP_VOLTAGE
            )  # Use open-loop control for drive motors
        )
        self._brake = swerve.requests.SwerveDriveBrake()
        self._point = swerve.requests.PointWheelsAt()

        self._logger = Telemetry(self._max_speed)

        # self._joystick = commands2.button.CommandXboxController(0)

        self.drivetrain = TunerConstants.create_drivetrain()


        # Telemetry
        self.event_loop = EventLoop()

        # Speed ratio for drivetrain
        self.speed_ratio = 1

        # If in simulation, seed_field_centric position
        if utils.is_simulation():
            self.drivetrain.seed_field_centric()

        # Register telemetry
        self.drivetrain.register_telemetry(self._logger.telemeterize)

        self.configure_bindings()

        # self.shooter.test_motor()

    def configure_bindings(self):
        """Configure button-to-command mappings."""
        self.configure_driver_controls()
        self.configure_operator_controls()

    def configure_driver_controls(self):
        """Configure driver controller bindings (driving and vision)."""
        # Drivetrain default command
        self.drivetrain.setDefaultCommand(
            # Drivetrain will execute this command periodically
            self.drivetrain.apply_request(
                lambda: (
                    self._drive.with_velocity_x(
                        -self.controller_driver.getLeftY() * self._max_speed
                    )  # Drive forward with negative Y (forward)
                    .with_velocity_y(
                        -self.controller_driver.getLeftX() * self._max_speed
                    )  # Drive left with negative X (left)
                    .with_rotational_rate(
                        -self.controller_driver.getRightX() * self._max_angular_rate
                    )  # Drive counterclockwise with negative X (left)
                )
            )
        )

        self.controller_driver.a().whileTrue(self.drivetrain.apply_request(lambda: self._brake))
        self.controller_driver.b().whileTrue(
            self.drivetrain.apply_request(
                lambda: self._point.with_module_direction(
                    Rotation2d(-self.controller_driver.getLeftY(), -self.controller_driver.getLeftX())
                )
            )
        )

        # Run SysId routines when holding back/start and X/Y.
        # Note that each routine should be run exactly once in a single log.
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

        # reset the field-centric heading on left bumper press
        self.controller_driver.leftBumper().onTrue(
            self.drivetrain.runOnce(lambda: self.drivetrain.seed_field_centric())
        )

        self.drivetrain.register_telemetry(
            lambda state: self._logger.telemeterize(state)
        )
        #
        # # Driver buttons
        # x_button_driver = JoystickButton(self.controller_driver, XboxController.Button.kX)
        # left_bumper_driver = JoystickButton(self.controller_driver, XboxController.Button.kLeftBumper)
        # b_button_driver = JoystickButton(self.controller_driver, XboxController.Button.kB)
        # a_button_driver = JoystickButton(self.controller_driver, XboxController.Button.kA)
        #
        # # Driver controls
        # x_button_driver.whileTrue(RotateToAprilTag(self.drive, self.limelight_handler, self.max_angular_rate))
        # left_bumper_driver.onTrue(InstantCommand(lambda: self.drivetrain.seed_field_centric()))
        # b_button_driver.onTrue(InstantCommand(lambda: self.set_speed_ratio(0.25)))
        # b_button_driver.onFalse(InstantCommand(lambda: self.set_speed_ratio(1)))
        # a_button_driver.whileTrue(
        #     InstantCommand(
        #         lambda: self.drivetrain.apply_request(
        #             lambda: self.drive.with_rotational_rate(.5 * self.max_angular_rate)
        #         )
        #     )
        # )

    def configure_operator_controls(self):
        """Configure operator controller bindings (mechanisms)."""
        # Elevator buttons
        # x_button = JoystickButton(self.controller_operator, XboxController.Button.kX)
        # y_button = JoystickButton(self.controller_operator, XboxController.Button.kY)
        # a_button = JoystickButton(self.controller_operator, XboxController.Button.kA)
        # b_button = JoystickButton(self.controller_operator, XboxController.Button.kB)

        # Elevator controls
        self.controller_operator.a().onTrue(self.auton.shoot(2))
        self.controller_operator.x().onTrue(self.auton.shoot(3))
        self.controller_operator.y().onTrue(self.auton.shoot(4))
        # self.controller_operator.x().onTrue(self.elevator.go_to_height(self.elevator.preset_rotations[XboxController.Button.kX]))
        # self.controller_operator.y().onTrue(self.elevator.go_to_height(self.elevator.preset_rotations[XboxController.Button.kY]))
        # self.controller_operator.a().onTrue(self.elevator.go_to_height(self.elevator.preset_rotations[XboxController.Button.kA]))
        self.controller_operator.b().onTrue(self.elevator.go_to_height(self.elevator.preset_rotations["intake"]))

        # Arm controls
        # left_bumper = JoystickButton(self.controller_operator, XboxController.Button.kLeftBumper)
        # right_bumper = JoystickButton(self.controller_operator, XboxController.Button.kRightBumper)
        # left_trigger = Trigger(lambda: self.controller_operator.getLeftTriggerAxis() > 0.5)
        # right_trigger = Trigger(lambda: self.controller_operator.getRightTriggerAxis() > 0.5)
        #
        # left_bumper.onTrue(self.arm.go_to_angle(self.arm.preset_angles[XboxController.Button.kLeftBumper]))
        # right_bumper.onTrue(self.arm.go_to_angle(self.arm.preset_angles[XboxController.Button.kRightBumper]))
        # left_trigger.onTrue(self.arm.go_to_angle(45.0))
        # right_trigger.onTrue(self.arm.go_to_angle(135.0))

        Trigger(lambda: abs(self.controller_operator.getHID().getLeftY()) > 0.1).whileTrue(
            self.elevator.manual(lambda: self.controller_operator.getHID().getLeftY() * -1)
        )

        Trigger(lambda: abs(self.controller_operator.getHID().getRightY()) > 0.1).whileTrue(
            self.arm.manual(lambda: self.controller_operator.getHID().getRightY() * -1)
        )

        # Trigger(lambda: self.controller_operator.getHID().getLeftTriggerAxis() > 0.05).whileTrue(
        #     self.shooter.manual(lambda: self.controller_operator.getHID().getLeftTriggerAxis())
        # )
        #
        # Trigger(lambda: self.controller_operator.getHID().getRightTriggerAxis() > 0.05).whileTrue(
        #     self.shooter.manual(lambda: self.controller_operator.getHID().getRightTriggerAxis() * -1 * .1)
        # )

        # back_button.whileTrue(self.shooter.shoot())  # Moved shooter to back button

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