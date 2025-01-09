from phoenix6.swerve import SwerveDrivetrain, SwerveDrivetrainConstants, SwerveModuleConstants
from phoenix6.hardware import  TalonFX, CANcoder

from commands2 import SubsystemBase, InstantCommand
from phoenix6 import utils
from wpimath.geometry import Rotation2d
from wpilib import Notifier, RobotController, DriverStation

class CommandSwerveDrivetrain(SwerveDrivetrain, SubsystemBase):
    """Extends Phoenix SwerveDrivetrain and implements Subsystem for command-based use."""

    kSimLoopPeriod = 0.005  # 5 ms simulation loop period
    drivetrain_constants = SwerveDrivetrainConstants()

    def __init__(self, drivetrain_constants, *modules):
        # Pass only supported arguments to SwerveDrivetrain
        SwerveDrivetrain.__init__(self,
                                  TalonFX,
                                  TalonFX,
                                  CANcoder,
                                  drivetrain_constants,
                                  list(modules[:4]))  # Limit to 4 modules
        SubsystemBase.__init__(self)  # Initialize SubsystemBase

        self.m_sim_notifier = None
        self.m_last_sim_time = utils.get_current_time_seconds()
        self.BlueAlliancePerspectiveRotation = Rotation2d.fromDegrees(0)
        self.RedAlliancePerspectiveRotation = Rotation2d.fromDegrees(180)
        self.has_applied_operator_perspective = False

        if utils.is_simulation():
            self.start_sim_thread()

    def apply_request(self, request_supplier):
        """
        Create a command to apply a control request.
        :param request_supplier: A callable that returns a phoenix6.swerve.requests.SwerveRequest
        :return: An InstantCommand to execute the request
        """
        return InstantCommand(lambda: self.set_control(request_supplier()), self)

    def start_sim_thread(self):
        """Start a thread for faster simulation updates."""
        self.m_sim_notifier = Notifier(self.simulation_task)
        self.m_sim_notifier.startPeriodic(self.kSimLoopPeriod)

    def simulation_task(self):
        """Simulation task to update the drivetrain's simulation state."""
        current_time = utils.get_current_time_seconds()
        delta_time = current_time - self.m_last_sim_time
        self.m_last_sim_time = current_time

        # Update simulation state using the measured time delta and battery voltage
        self.update_sim_state(delta_time, RobotController.getBatteryVoltage())

    def periodic(self):
        """Periodically apply operator perspective based on alliance color."""
        if not self.has_applied_operator_perspective or DriverStation.isDisabled():
            alliance_color = DriverStation.getAlliance()
            if alliance_color == DriverStation.Alliance.kRed:
                self.set_operator_perspective_forward(self.RedAlliancePerspectiveRotation)
            else:
                self.set_operator_perspective_forward(self.BlueAlliancePerspectiveRotation)
            self.has_applied_operator_perspective = True
