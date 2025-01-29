from commands2 import SubsystemBase, Command
from phoenix6.hardware import TalonFX
from phoenix6.configs import TalonFXConfiguration, Slot0Configs
from phoenix6.signals import NeutralModeValue
from wpilib import XboxController

class Shooter(SubsystemBase):
    """
    Shooter subsystem that controls a motor to launch PVC pipe sections.
    Uses velocity control for consistent shooting power.
    """
    
    def __init__(self, motor_id: int, max_rpm: float = 6000):
        """Initialize the shooter subsystem.
        
        Args:
            motor_id: CAN ID of the TalonFX motor
            max_rpm: Maximum motor RPM
        """
        super().__init__()
        
        # Initialize motor
        self.motor = TalonFX(motor_id)
        
        # Configure motor
        configs = TalonFXConfiguration()
        
        # Velocity control configuration
        slot0 = Slot0Configs()
        slot0.k_p = 0.05    # Velocity control gains
        slot0.k_i = 0.0
        slot0.k_d = 0.0
        slot0.k_v = 0.12    # Feed forward gain
        configs.slot0 = slot0
        
        # Set motor to coast mode when stopped (less wear on mechanism)
        configs.motor_output.neutral_mode = NeutralModeValue.COAST
        
        # Apply configurations
        self.motor.configurator.apply(configs)
        
        # Constants
        self.max_rpm = max_rpm
        self.default_speed_percentage = 0.75  # 75% of max speed by default
        
        # Current state
        self.is_running = False
        
    def set_speed_percentage(self, percentage: float):
        """Set the shooter speed as a percentage of max RPM.
        
        Args:
            percentage: Speed percentage (0.0 to 1.0)
        """
        self.default_speed_percentage = max(0.0, min(1.0, percentage))
        
    def get_current_rpm(self) -> float:
        """Get the current motor RPM."""
        return self.motor.get_velocity().value * 60.0  # Convert RPS to RPM
        
    def shoot(self) -> Command:
        """Create a command to activate the shooter.
        Returns a command that runs the shooter at the default speed.
        """
        class ShooterCommand(Command):
            def __init__(self, shooter):
                super().__init__()
                self.shooter = shooter
                self.addRequirements(shooter)
                
            def initialize(self):
                print(f"Starting shooter at {self.shooter.default_speed_percentage * 100}% speed")
                target_rps = (self.shooter.default_speed_percentage * self.shooter.max_rpm) / 60.0
                self.shooter.motor.set_velocity(target_rps)
                self.shooter.is_running = True
                
            def execute(self):
                # Could add monitoring/adjustment logic here if needed
                current_rpm = self.shooter.get_current_rpm()
                if abs(current_rpm - (self.shooter.default_speed_percentage * self.shooter.max_rpm)) > 100:
                    print(f"Warning: Shooter speed ({current_rpm} RPM) not at target")
                
            def end(self, interrupted):
                print("Stopping shooter")
                self.shooter.motor.set_velocity(0)
                self.shooter.is_running = False
                
            def isFinished(self):
                # Run until interrupted
                return False
                
        return ShooterCommand(self)
    
    def stop(self):
        """Stop the shooter motor."""
        self.motor.set_velocity(0)
        self.is_running = False
        
    def periodic(self):
        """Periodic update function."""
        # Add any telemetry or monitoring here
        if self.is_running:
            current_rpm = self.get_current_rpm()
            # Log speed for debugging/monitoring
            print(f"Shooter RPM: {current_rpm:.0f}")