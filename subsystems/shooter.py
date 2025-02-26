from commands2 import SubsystemBase, Command
from phoenix6.hardware import TalonFXS
from phoenix6.configs import TalonFXSConfiguration, Slot0Configs
from phoenix6.signals import NeutralModeValue, MotorArrangementValue
from phoenix6.controls import VelocityVoltage, DutyCycleOut
from typing import Callable
from constants import MOTOR_IDS, CON_SHOOT
from wpilib import Timer

class Shooter(SubsystemBase):

    def __init__(self, max_rpm: float = 2000):
        """Initialize the shooter subsystem."""
        super().__init__()
        
        # Initialize motor
        self.motor = TalonFXS(MOTOR_IDS["shooter"])
        
        # Configure motor
        configs = TalonFXSConfiguration()

        configs.commutation.motor_arrangement = MotorArrangementValue.MINION_JST

        # Velocity control configuration
        slot0 = Slot0Configs()
        slot0.k_p = 0.1    # Velocity control gains
        slot0.k_i = 0.0
        slot0.k_d = 0.0
        slot0.k_v = 0.12    # Feed forward gain
        configs.slot0 = slot0

        # Set motor to coast mode when stopped
        configs.motor_output.neutral_mode = NeutralModeValue.BRAKE

        # Apply configurations
        self.motor.configurator.apply(configs)

        self.max_rpm = max_rpm
        self.velocity_request = VelocityVoltage(0)
        self.is_running = False
        # self.default_speed_percentage = 1  # 75% of max speed by default

    # def set_speed_percentage(self, percentage: float):
    #     """Set the shooter speed as a percentage of max RPM."""
    #     self.default_speed_percentage = max(0.0, min(1.0, percentage))

    # def get_current_rpm(self) -> float:
    #     """Get the current motor RPM."""
    #     return self.motor.get_velocity().value * 60.0  # Convert RPS to RPM

    def shoot(self, strength: int, action = 'shoot', stop_condition: Callable[[], bool] = None) -> Command:

        class ShooterShootCommand(Command):
            def __init__(self, shooter, _strength, _action, _stop_condition):
                super().__init__()
                self.shooter = shooter
                self.addRequirements(shooter)
                self.timer = Timer()
                self.voltage = 0
                self.strength = _strength
                self.action = _action
                self.stop_condition = _stop_condition


            def initialize(self):
                print(f"///// SHOOTER SHOOT")
                self.timer.reset()
                self.timer.start()

            def execute(self):

                voltage = self.strength
                if self.action == 'hold':
                    voltage = voltage * -1
                voltage = min(max(voltage, -2), 2) * -1
                # print(f"///// SHOOTER SHOOT V: {voltage}")

                # Apply voltage to motor
                self.shooter.motor.setVoltage(voltage)

            def isFinished(self):
                if self.action == "hold" and self.stop_condition and self.stop_condition():
                    print(f"///// SHOOTER {self.action.upper()} STOPPING")
                    return True

                if self.action == "shoot":
                    time_elapsed = self.timer.get()
                    print(f"///// SHOOTER {self.action.upper()} TIMER: {time_elapsed:.2f}s")
                    if time_elapsed >= CON_SHOOT["shoot_duration"]:  # ✅ 'shoot' runs for 0.25 seconds
                        print(f"///// SHOOTER {self.action.upper()} FINISHED")
                        return True

                return False

            def end(self, interrupted):
                    self.shooter.motor.setVoltage(0)
                    self.timer.stop()

        return ShooterShootCommand(self, strength, action, stop_condition)

    def manual(self, percentage_func: Callable[[], float]) -> Command:

        class ManualRunCommand(Command):
            def __init__(self, shooter, percentage_func: Callable[[], float]):
                super().__init__()
                self.shooter = shooter
                self.percentage_func = percentage_func  # Store function instead of static value
                self.addRequirements(shooter)

            # def initialize(self):

            def execute(self):
                percentage = self.percentage_func()  # Call function to get live trigger value
                if abs(percentage) <= 0.1:  # Ignore small values
                    self.shooter.stop()
                    return

                target_rps = (percentage * self.shooter.max_rpm) / 60.0
                self.shooter.velocity_request.velocity = target_rps
                self.shooter.motor.set_control(self.shooter.velocity_request)
                self.shooter.is_running = True

            def end(self, interrupted):
                self.shooter.motor.set_control(DutyCycleOut(0))
                self.shooter.is_running = False

            def isFinished(self):
                return False  # Runs continuously while trigger is held

        return ManualRunCommand(self, percentage_func)

    def stop(self):
        """Stop the shooter motor."""
        self.motor.set(0)
        self.is_running = False

    # def periodic(self):
    #     """Periodic update function."""
        # if self.is_running:
        #     current_rpm = self.get_current_rpm()
        #     print(f"Shooter RPM: {current_rpm:.0f}")
