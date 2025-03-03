from wpilib.event import EventLoop
from wpilib import SmartDashboard, SendableChooser, DriverStation

from commands2 import Command, InstantCommand, CommandScheduler
from commands2.button import Trigger
from commands2.button import CommandXboxController
from commands2.sysid import SysIdRoutine

from phoenix6 import swerve, utils

from wpimath.units import rotationsToRadians
from wpimath.geometry import Rotation2d

from telemetry import Telemetry
from generated.tuner_constants import TunerConstants

from subsystems.arm import Arm
from subsystems.elevator import Elevator
from subsystems.shooter import Shooter
from subsystems.climber import Climber

from autonomous.auton_operator import AutonOperator

from autonomous.auton_mode_selector import create_auton_chooser

from handlers.limelight_handler import LimelightHandler



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
        self.controller_driver = CommandXboxController(0)  # Driver controller for driving/vision
        self.controller_operator = CommandXboxController(1)  # Operator controller for mechanisms

        # Initialize subsystems
        self.limelight_handler = LimelightHandler(debug=True)
        self.elevator = Elevator(1000)  # Use your actual CAN IDs
        self.arm = Arm(300)
        self.shooter = Shooter()
        self.climber = Climber()

        self.auton_operator = AutonOperator()

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

        self.drivetrain = TunerConstants.create_drivetrain()

        # Telemetry
        self.event_loop = EventLoop()

        # Speed ratio for drivetrain
        self.speed_ratio = 1
        self.rotation_ratio = 1

        # If in simulation, seed_field_centric position
        if utils.is_simulation():
            self.drivetrain.seed_field_centric()

        # Register telemetry
        self.drivetrain.register_telemetry(self._logger.telemeterize)

        self.configure_bindings()

        # Auton functions
        self.chooser = SendableChooser()

        # Autonomous command chooser
        self.chooser = create_auton_chooser(self.drivetrain, self._drive, self._max_angular_rate, self.shooter)

    def configure_bindings(self):
        """Configure button-to-command mappings."""
        self.configure_driver_controls()
        self.configure_operator_controls()

        #ToDo: This is just for testing on sim, delete later
        # shooter_command = self.shooter.shoot(3, 'hold')
        # CommandScheduler.getInstance().schedule(shooter_command)


    # def get_speed_multiplier(self):
    #     "returns the current speed multiplier"

    def configure_driver_controls(self):
        """Configure driver controller bindings (driving and vision)."""

        ctrl = self.controller_driver

        # Drivetrain default command
        self.drivetrain.setDefaultCommand(
            # Drivetrain will execute this command periodically
            self.drivetrain.apply_request(
                lambda: (
                    self._drive.with_velocity_x(
                        -ctrl.getLeftY() * self._max_speed * self.speed_ratio
                    )  # Drive forward with negative Y (forward)
                    .with_velocity_y(
                        -ctrl.getLeftX() * self._max_speed * self.speed_ratio
                    )  # Drive left with negative X (left)
                    .with_rotational_rate(
                        -ctrl.getRightX() * self._max_angular_rate * self.rotation_ratio
                    )  # Drive counterclockwise with negative X (left)
                )
            )
        )

        ctrl.a().whileTrue(self.drivetrain.apply_request(lambda: self._brake))
        ctrl.b().whileTrue(
            self.drivetrain.apply_request(
                lambda: self._point.with_module_direction(
                    Rotation2d(-ctrl.getLeftY(), -ctrl.getLeftX())
                )
            )
        )

        # Run SysId routines when holding back/start and X/Y.
        # Note that each routine should be run exactly once in a single log.
        (ctrl.back() & ctrl.y()).whileTrue(
            self.drivetrain.sys_id_dynamic(SysIdRoutine.Direction.kForward)
        )
        (ctrl.back() & ctrl.x()).whileTrue(
            self.drivetrain.sys_id_dynamic(SysIdRoutine.Direction.kReverse)
        )
        (ctrl.start() & ctrl.y()).whileTrue(
            self.drivetrain.sys_id_quasistatic(SysIdRoutine.Direction.kForward)
        )
        (ctrl.start() & ctrl.x()).whileTrue(
            self.drivetrain.sys_id_quasistatic(SysIdRoutine.Direction.kReverse)
        )

        # reset the field-centric heading on left bumper press
        ctrl.leftBumper().onTrue(
            self.drivetrain.runOnce(lambda: self.drivetrain.seed_field_centric())
        )

        self.drivetrain.register_telemetry(
            lambda state: self._logger.telemeterize(state)
        )

        # slow mode with buttons
        ctrl.rightBumper().onTrue(
            InstantCommand(lambda: self.set_speed_ratio(0.2))
        )
        ctrl.rightBumper().onFalse(
            InstantCommand(lambda: self.set_speed_ratio(1))
        )

        # trying to do some autonomy
        # ctrl.y().onTrue(
        #     # self.drivetrain.apply_request(
        #     #     lambda: self._drive.with_velocity_y(-3)  # Adjust speed if needed
        #     # )
        #     self.auton.drive(self.drivetrain, self._drive, self._max_angular_rate)
        # )
        #
        # ctrl.y().onFalse(
        #     self.drivetrain.apply_request(lambda: self._drive.with_rotational_rate(0))
        # )

    def configure_operator_controls(self):
        """Configure operator controller bindings (mechanisms)."""

        ctrl = self.controller_operator

        ctrl.rightBumper().onTrue(InstantCommand(lambda: CommandScheduler.getInstance().cancelAll()))

        # Automated controls
        ctrl.a().onTrue(self.auton_operator.shoot(2))
        ctrl.x().onTrue(self.auton_operator.shoot(3))
        ctrl.y().onTrue(self.auton_operator.shoot(4))
        ctrl.b().onTrue(self.auton_operator.intake())

        ctrl.back().whileTrue(self.climber.manual(lambda: 0.2))
        ctrl.start().whileTrue(self.climber.manual(lambda: -0.2))

        # Manual controls with buttons
        Trigger(lambda: abs(ctrl.getHID().getLeftY()) > 0.1).whileTrue(
            self.elevator.manual(lambda: ctrl.getHID().getLeftY())
        )

        Trigger(lambda: abs(ctrl.getHID().getRightY()) > 0.1).whileTrue(
            self.arm.manual(lambda: ctrl.getHID().getRightY() * -1)
        )

        Trigger(lambda: ctrl.getHID().getLeftTriggerAxis() > 0.05).whileTrue(
            self.shooter.manual(lambda: ctrl.getHID().getLeftTriggerAxis())
        )

        Trigger(lambda: ctrl.getHID().getRightTriggerAxis() > 0.05).whileTrue(
            self.shooter.manual(lambda: ctrl.getHID().getRightTriggerAxis() * -1)
        )

        ctrl.back().whileTrue(self.climber.manual(lambda: 0.25))
        ctrl.start().whileTrue(self.climber.manual(lambda: -0.25))

        # Default commands
        # self.arm.setDefaultCommand(self.arm.hold_position())

    def set_speed_ratio(self, ratio):
        """Sets the speed ratio based on button press/release."""
        self.speed_ratio = ratio
        self.rotation_ratio = min(1, ratio * 1.5)

    def get_autonomous_command(self):
        selected_command = self.chooser.getSelected()
        return selected_command

    #
    # def rotate_drivetrain(self):
    #     """Helper method to rotate the drivetrain."""
    #     rotation_request = self.drive.with_rotational_rate(.5 * self.max_angular_rate)
    #     self.drivetrain.apply_request(rotation_request)
