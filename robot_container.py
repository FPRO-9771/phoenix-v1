import math
from commands2 import InstantCommand, PrintCommand, Command, CommandScheduler, SequentialCommandGroup, RunCommand
from commands2.button import Trigger
from wpilib import XboxController
from wpilib.event import EventLoop
from wpimath.geometry import Pose2d, Rotation2d, Translation2d
from phoenix6 import utils
from phoenix6.swerve import requests, swerve_module
from subsystems.command_swerve_drivetrain import CommandSwerveDrivetrain
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

        # Joystick and drivetrain initialization
        self.joystick = XboxController(0)
        self.drivetrain = tuner_constants.DriveTrain

        self.limelight_handler = LimelightHandler(debug=True)

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

        # Configure button bindings
        self.configure_bindings()

        # If in simulation, seed_field_centric position
        if utils.is_simulation():
            self.drivetrain.seed_field_centric()

        # Register telemetry
        self.drivetrain.register_telemetry(self.logger.telemeterize)

    def apply_drivetrain_request(self, request):
        """Helper function to apply requests to drivetrain.
        Args:
            request: The request to apply to the drivetrain
        """
        self.drivetrain.apply_request(request)

    def apply_rotation(self):
        """Apply rotation to the drivetrain with rate limiting."""
        current_time = time.time()
        if current_time - self.last_rotation_time >= 0.5:  # 500ms delay
            print("Rotation command triggered")
            rotation_request = self.drive.with_rotational_rate(.5 * self.max_angular_rate)
            self.drivetrain.apply_request(rotation_request)
            self.last_rotation_time = current_time

    def configure_bindings(self):
        """Configure button-to-command mappings."""
        # Default drivetrain command
        self.drivetrain.setDefaultCommand(
            self.drivetrain.apply_request(lambda: self.drive
                                          .with_velocity_x(-self.joystick.getLeftY() * self.max_speed)
                                          .with_velocity_y(-self.joystick.getLeftX() * self.max_speed)
                                          # .with_rotational_rate(-self.joystick.getRightX() * self.max_angular_rate)
                                          )
        )

        # Ensure you have a default EventLoop from the CommandScheduler
        default_loop = CommandScheduler.getInstance().getDefaultButtonLoop()

        a_button = JoystickButton(self.joystick, self.joystick.Button.kA)
        b_button = JoystickButton(self.joystick, self.joystick.Button.kB)
        x_button = JoystickButton(self.joystick, self.joystick.Button.kX)
        left_bumper_button = JoystickButton(self.joystick, self.joystick.Button.kLeftBumper)

        def print_action(button_name):
            print(f"Button: {button_name}")

        a_button_command = SequentialCommandGroup(
            InstantCommand(lambda: print_action("A")),
            InstantCommand(lambda: self.drivetrain.apply_request(lambda: self.brake))  # Apply the brake
        )

        b_button_command = SequentialCommandGroup(
            InstantCommand(lambda: print_action("B")),
            InstantCommand(
                lambda: self.drivetrain.apply_request(
                    lambda: self.point.with_module_direction(
                        Rotation2d(-self.joystick.getLeftY(), -self.joystick.getLeftX())
                    )
                )
            )
        )

        lb_button_command = SequentialCommandGroup(
            InstantCommand(lambda: print_action("LB")),
            InstantCommand(lambda: self.drivetrain.seed_field_centric())
        )


        # Original button bindings remain unchanged
        # a_button.whileTrue(InstantCommand(lambda: CommandScheduler.getInstance().schedule(a_button_command)))
        b_button.onTrue(InstantCommand(lambda: CommandScheduler.getInstance().schedule(b_button_command)))
        left_bumper_button.onTrue(InstantCommand(lambda: CommandScheduler.getInstance().schedule(lb_button_command)))



        x_button.whileTrue(RotateToAprilTag(self.drive, self.limelight_handler, self.max_angular_rate))
        # x_button.whileTrue(InstantCommand(
        #     lambda: self.drivetrain.apply_request(
        #         lambda: self.drive.with_rotational_rate(.5 * self.max_angular_rate)
        #     )))
        # x_button.whileTrue(InstantCommand(self.apply_rotation))
            # Create rotation command
        # rotation_command = InstantCommand(
        #     self.apply_rotation,
        #     name="Rotation Command"  # Named for debugging
        # )
        rotation_command = RunCommand(
            self.apply_rotation,
            # name="Rotation Command"
        )
        # a_button.whileTrue(InstantCommand(self.apply_rotation))
        a_button.onTrue(rotation_command)



    def rotate_drivetrain(self):
        """Helper method to rotate the drivetrain."""
        rotation_request = self.drive.with_rotational_rate(.5 * self.max_angular_rate)
        self.drivetrain.apply_request(rotation_request)


    def get_autonomous_command(self) -> Command:
        time.sleep(10)
        """Return the autonomous command."""
        return RepeatCommand(
            SequentialCommandGroup(
                WaitCommand(10),  # Wait 10 seconds
                InstantCommand(self.rotate_drivetrain),
                WaitCommand(1)  # Rotate for 1 second
            )
        )
