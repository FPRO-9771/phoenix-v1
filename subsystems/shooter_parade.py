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

        # Velocity control configuration
        slot0 = Slot0Configs()
        slot0.k_p = 0.1    # Velocity control gains
        slot0.k_i = 0.0
        slot0.k_d = 0.0
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
                print("///// PARADE SHOOTER PULL BACK START")

            def execute(self):
                # Convert RPM to RPS and make negative for pull-back
                target_rps = -CON_SHOOT_PARADE["low_rpm"] / 60.0
                
                # Set both motors to same velocity (inversion handled in config)
                self.shooter.velocity_request_left.velocity = target_rps
                self.shooter.velocity_request_right.velocity = target_rps
                
                self.shooter.motor_left.set_control(self.shooter.velocity_request_left)
                self.shooter.motor_right.set_control(self.shooter.velocity_request_right)
                self.shooter.is_running = True

            def isFinished(self):
                return self.stop_condition and self.stop_condition()

            def end(self, interrupted):
                self.shooter.stop()
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
                print("///// PARADE SHOOTER FIRE START")
                self.timer.reset()
                self.timer.start()

            def execute(self):
                # Convert RPM to RPS for firing
                target_rps = CON_SHOOT_PARADE["max_rpm"] / 60.0
                
                # Set both motors to same velocity (inversion handled in config)
                self.shooter.velocity_request_left.velocity = target_rps
                self.shooter.velocity_request_right.velocity = target_rps
                
                self.shooter.motor_left.set_control(self.shooter.velocity_request_left)
                self.shooter.motor_right.set_control(self.shooter.velocity_request_right)
                self.shooter.is_running = True

            def isFinished(self):
                time_elapsed = self.timer.get()
                return time_elapsed >= CON_SHOOT_PARADE["fire_duration"]

            def end(self, interrupted):
                self.shooter.stop()
                self.timer.stop()
                print(f"///// PARADE SHOOTER FIRE END (duration: {self.timer.get():.2f}s)")

        return FireCommand(self)

    def stop(self):
        """Stop both motors."""
        self.motor_left.set_control(DutyCycleOut(0))
        self.motor_right.set_control(DutyCycleOut(0))
        self.is_running = False

    def periodic(self):
        """Periodic update function."""
        pass