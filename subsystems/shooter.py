from commands2 import SubsystemBase, Command
from phoenix6.hardware import TalonFX
from phoenix6.configs import TalonFXConfiguration, Slot0Configs
from phoenix6.signals import NeutralModeValue
from phoenix6.controls import VelocityVoltage
from wpilib import XboxController
from typing import Callable
from constants import MOTOR_IDS

class Shooter(SubsystemBase):
    """
    Shooter subsystem that controls a motor to launch PVC pipe sections.
    Uses velocity control for consistent shooting power.
    """
    
    def __init__(self, max_rpm: float = 2000):
        """Initialize the shooter subsystem."""
        super().__init__()
        
        # Initialize motor
        self.motor = TalonFX(MOTOR_IDS["shooter"])
        
        # Configure motor
        configs = TalonFXConfiguration()
        #
        # # Velocity control configuration
        # slot0 = Slot0Configs()
        # slot0.k_p = 0.05    # Velocity control gains
        # slot0.k_i = 0.0
        # slot0.k_d = 0.0
        # slot0.k_v = 0.12    # Feed forward gain
        # configs.slot0 = slot0
        #
        # # Set motor to coast mode when stopped
        # configs.motor_output.neutral_mode = NeutralModeValue.COAST
        #
        # # Apply configurations
        # self.motor.configurator.apply(configs)
        #
        # # Constants
        self.max_rpm = max_rpm
        self.default_speed_percentage = 0.75  # 75% of max speed by default
        #
        # # Create velocity control request
        self.velocity_request = VelocityVoltage(0)
        #
        # # Current state
        self.is_running = False
        
    def set_speed_percentage(self, percentage: float):
        """Set the shooter speed as a percentage of max RPM."""
        self.default_speed_percentage = max(0.0, min(1.0, percentage))

    def get_current_rpm(self) -> float:
        """Get the current motor RPM."""
        return self.motor.get_velocity().value * 60.0  # Convert RPS to RPM

    def manual(self, percentage_func: Callable[[], float]) -> Command:
        """Create a command that continuously updates shooter speed based on a trigger input."""

        class ManualRunCommand(Command):
            def __init__(self, shooter, percentage_func: Callable[[], float]):
                super().__init__()
                self.shooter = shooter
                self.percentage_func = percentage_func  # Store function instead of static value
                self.addRequirements(shooter)

            def initialize(self):
                print("Shooter command started")

            def execute(self):
                percentage = self.percentage_func()  # Call function to get live trigger value
                if abs(percentage) <= 0.05:  # Ignore small values
                    self.shooter.stop()
                    return

                target_rps = (percentage * self.shooter.max_rpm) / 60.0
                self.shooter.velocity_request.velocity = target_rps
                self.shooter.motor.set_control(self.shooter.velocity_request)
                self.shooter.is_running = True
                print(f"Shooter running at {percentage * 100:.1f}% speed (RPM: {target_rps * 60:.0f})")

            def end(self, interrupted):
                print("Stopping shooter")
                self.shooter.velocity_request.velocity = 0
                self.shooter.motor.set_control(self.shooter.velocity_request)
                self.shooter.is_running = False

            def isFinished(self):
                return False  # Runs continuously while trigger is held

        return ManualRunCommand(self, percentage_func)

    def stop(self):
        """Stop the shooter motor."""
        self.velocity_request.velocity = 0
        self.motor.set_control(self.velocity_request)
        self.is_running = False

    def periodic(self):
        """Periodic update function."""
        if self.is_running:
            current_rpm = self.get_current_rpm()
            print(f"Shooter RPM: {current_rpm:.0f}")

    def test_motor(self):
        """Run the shooter motor at 25% power for testing."""
        print("Testing Minion motor...")
        from phoenix6.controls import DutyCycleOut

        self.motor.set_control(DutyCycleOut(0.25))  # Set to 25% power