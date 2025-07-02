from commands2 import SubsystemBase, Command
from phoenix6.hardware import TalonFX
from phoenix6.configs import TalonFXConfiguration, Slot0Configs
from phoenix6.signals import NeutralModeValue, InvertedValue
from phoenix6.controls import VelocityVoltage, DutyCycleOut
from typing import Callable
from constants import MOTOR_IDS, CON_SHOOT_PARADE
from wpilib import Timer

class ShooterParade(SubsystemBase):

    def __init__(self):
        """Initialize the parade shooter subsystem with two Kraken X44 motors."""
        super().__init__()
        
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
        """Run motors at maximum RPM for set duration."""
        
        class FireCommand(Command):
            def __init__(self, shooter):
                super().__init__()
                self.shooter = shooter
                self.addRequirements(shooter)
                self.timer = Timer()

            def initialize(self):
                print(">>>>> FIRE STARTING - NEW VERSION WITH 12V! <<<<<")
                self.timer.reset()
                self.timer.start()

            def execute(self):
                # Use maximum voltage for blazing fast fire speed
                fire_voltage = CON_SHOOT_PARADE["fire_voltage"]
                print(f"   Fire voltage: {fire_voltage}V (MAXIMUM SPEED)")
                
                # Apply maximum voltage directly to both motors
                self.shooter.motor_left.setVoltage(fire_voltage)
                self.shooter.motor_right.setVoltage(fire_voltage)
                self.shooter.is_running = True

            def isFinished(self):
                time_elapsed = self.timer.get()
                return time_elapsed >= CON_SHOOT_PARADE["fire_duration"]

            def end(self, interrupted):
                # Stop motors with voltage control
                self.shooter.motor_left.setVoltage(0.0)
                self.shooter.motor_right.setVoltage(0.0)
                self.shooter.is_running = False
                self.timer.stop()
                print(f"///// PARADE SHOOTER FIRE END (duration: {self.timer.get():.2f}s)")

        return FireCommand(self)

    def stop(self):
        """Stop both motors."""
        self.motor_left.setVoltage(0.0)
        self.motor_right.setVoltage(0.0)
        self.is_running = False

    def periodic(self):
        """Periodic update function."""
        pass