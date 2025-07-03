from commands2 import SubsystemBase, Command
from phoenix6.hardware import TalonFX
from phoenix6.configs import TalonFXConfiguration, Slot0Configs
from phoenix6.signals import NeutralModeValue, InvertedValue
from phoenix6.controls import VelocityVoltage, DutyCycleOut
from typing import Callable
from constants import MOTOR_IDS, CON_SHOOT_PARADE
from wpilib import Timer

class ShooterParade(SubsystemBase):

    def __init__(self, max_rpm: float = 2000):
        """Initialize the parade shooter subsystem with two Kraken X44 motors."""
        super().__init__()
        self.max_rpm = max_rpm
        
        # Initialize motors
        self.motor_left = TalonFX(MOTOR_IDS["shooter_parade_left"])
        self.motor_right = TalonFX(MOTOR_IDS["shooter_parade_right"])
        
        # Configure motors
        self._configure_motors()
        
        # Control requests
        self.velocity_request_left = VelocityVoltage(0)
        self.velocity_request_right = VelocityVoltage(0)
        self.is_running = False

    def _configure_motors(self):
        """Configure both motors with appropriate settings."""
        config = TalonFXConfiguration()

        # Velocity control configuration - tuned for Kraken motors
        slot0 = Slot0Configs()
        slot0.k_p = 0.25   # Higher P gain for faster response
        slot0.k_i = 0.0
        slot0.k_d = 0.01   # Small D gain for stability  
        slot0.k_v = 0.12   # Feed forward gain
        config.slot0 = slot0

        # Set motor to brake mode when stopped
        config.motor_output.neutral_mode = NeutralModeValue.BRAKE

        # Configure left motor (normal direction)
        config.motor_output.inverted = InvertedValue.COUNTER_CLOCKWISE_POSITIVE
        self.motor_left.configurator.apply(config)

        # Configure right motor (inverted)
        config.motor_output.inverted = InvertedValue.CLOCKWISE_POSITIVE
        self.motor_right.configurator.apply(config)

    def pull_back(self, stop_condition: Callable[[], bool] = None) -> Command:
        """Run motors at low RPM in negative direction while button is pressed."""
        
        class PullBackCommand(Command):
            def __init__(self, shooter, _stop_condition):
                super().__init__()
                self.shooter = shooter
                self.stop_condition = _stop_condition
                self.addRequirements(shooter)

            def initialize(self):
                print(">>>>> PULL-BACK STARTING - NEW VOLTAGE VERSION! <<<<<")

            def execute(self):
                # Use low voltage for slow pull-back speed
                pullback_voltage = -CON_SHOOT_PARADE["pullback_voltage"]  # Negative for reverse
                print(f"   Pull-back voltage: {pullback_voltage}V (SLOW SPEED)")
                
                # Apply low voltage directly to both motors (negative for pull-back)
                self.shooter.motor_left.setVoltage(pullback_voltage)
                self.shooter.motor_right.setVoltage(pullback_voltage)
                self.shooter.is_running = True

            def isFinished(self):
                return self.stop_condition and self.stop_condition()

            def end(self, interrupted):
                # Stop motors with voltage control
                self.shooter.motor_left.setVoltage(0.0)
                self.shooter.motor_right.setVoltage(0.0)
                self.shooter.is_running = False
                print("///// PARADE SHOOTER PULL BACK END")

        return PullBackCommand(self, stop_condition)

    def fire(self) -> Command:
        """Run motors at maximum RPM for 4 rotations."""
        
        class FireCommand(Command):
            def __init__(self, shooter):
                super().__init__()
                self.shooter = shooter
                self.addRequirements(shooter)
                self.start_position_left = 0
                self.start_position_right = 0
                self.target_rotations = 4

            def initialize(self):
                print(">>>>> FIRE STARTING - NEW VERSION WITH 12V FOR 4 ROTATIONS! <<<<<")
                # Record starting positions
                self.start_position_left = self.shooter.motor_left.get_position().value
                self.start_position_right = self.shooter.motor_right.get_position().value
                print(f"   Starting positions - Left: {self.start_position_left:.2f}, Right: {self.start_position_right:.2f}")

            def execute(self):
                # Use maximum voltage for blazing fast fire speed
                fire_voltage = CON_SHOOT_PARADE["fire_voltage"]
                
                # Apply maximum voltage directly to both motors
                self.shooter.motor_left.setVoltage(fire_voltage)
                self.shooter.motor_right.setVoltage(fire_voltage)
                self.shooter.is_running = True

            def isFinished(self):
                # Get current positions
                current_left = self.shooter.motor_left.get_position().value
                current_right = self.shooter.motor_right.get_position().value
                
                # Calculate rotations completed
                rotations_left = abs(current_left - self.start_position_left)
                rotations_right = abs(current_right - self.start_position_right)
                
                # Use the average of both motors to determine completion
                avg_rotations = (rotations_left + rotations_right) / 2
                
                return avg_rotations >= self.target_rotations

            def end(self, interrupted):
                # Stop motors with voltage control
                self.shooter.motor_left.setVoltage(0.0)
                self.shooter.motor_right.setVoltage(0.0)
                self.shooter.is_running = False
                
                # Log final positions
                final_left = self.shooter.motor_left.get_position().value
                final_right = self.shooter.motor_right.get_position().value
                rotations_left = abs(final_left - self.start_position_left)
                rotations_right = abs(final_right - self.start_position_right)
                avg_rotations = (rotations_left + rotations_right) / 2
                
                print(f"///// PARADE SHOOTER FIRE END - Completed {avg_rotations:.2f} rotations")
                print(f"   Left motor: {rotations_left:.2f} rotations, Right motor: {rotations_right:.2f} rotations")

        return FireCommand(self)

    def stop(self):
        """Stop both motors."""
        self.motor_left.setVoltage(0.0)
        self.motor_right.setVoltage(0.0)
        self.is_running = False

    def periodic(self):
        """Periodic update function."""
        pass

    # Compatibility methods to match Shooter interface
    def shoot(self, strength: int, action='shoot', stop_condition: Callable[[], bool] = None, duration="shoot_duration") -> Command:
        """Compatibility method to match original Shooter interface."""
        if action == 'hold':
            # For 'hold' action, use pull_back method
            return self.pull_back(stop_condition)
        else:
            # For 'shoot' action, use fire method
            return self.fire()

    def manual(self, percentage_func: Callable[[], float]) -> Command:
        """Compatibility method for manual control - currently not implemented for parade shooter."""
        
        class ManualRunCommand(Command):
            def __init__(self, shooter, percentage_func: Callable[[], float]):
                super().__init__()
                self.shooter = shooter
                self.percentage_func = percentage_func
                self.addRequirements(shooter)

            def execute(self):
                # For now, just stop the shooter during manual control
                percentage = self.percentage_func()
                if abs(percentage) <= 0.1:
                    self.shooter.stop()

            def end(self, interrupted):
                self.shooter.stop()

            def isFinished(self):
                return False

        return ManualRunCommand(self, percentage_func)