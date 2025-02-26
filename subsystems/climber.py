from phoenix6.hardware import TalonFX
from phoenix6.configs import TalonFXConfiguration, Slot0Configs
from commands2 import SubsystemBase, Command
from phoenix6.signals import NeutralModeValue
from phoenix6.controls import VelocityVoltage
from typing import Callable
from constants import MOTOR_IDS, CON_CLIMB

class Climber(SubsystemBase):

    def __init__(self, max_rpm: float = 2000):
        """Initialize the arm subsystem."""
        super().__init__()

        # Initialize motor
        self.motor = TalonFX(MOTOR_IDS["climber"])

        # Configure motor
        configs = TalonFXConfiguration()

        # Velocity control configuration
        slot0 = Slot0Configs()
        slot0.k_p = 0.05  # Velocity control gains
        slot0.k_i = 0.0
        slot0.k_d = 0.0
        slot0.k_v = 0.12  # Feed forward gain
        configs.slot0 = slot0

        # Set motor to coast mode when stopped
        configs.motor_output.neutral_mode = NeutralModeValue.BRAKE

        # Apply configurations
        self.motor.configurator.apply(configs)

        self.max_rpm = max_rpm
        self.velocity_request = VelocityVoltage(0)
        self.is_running = False

        # Current target angle and state tracking
        self.is_holding_position = False


    def get_current_position(self) -> float:
        motor_position = self.motor.get_position().value * -1
        print(f"///// CLIMBER CP: {motor_position}")
        return motor_position

    def at_target_position(self, target: float, tolerance: float = 0.2) -> bool:
        motor_position = (self.get_current_position())
        print(f"///// CLIMBER TP: {motor_position} / {target}")
        return abs(self.get_current_position() - target) <= tolerance

    def switch_survo(self) -> bool:
        if self.motor.get_position().value == 0:
            self.motor.set_position(1)
            return True
        else:
            self.motor.set_position(0)
            return False

    # def safety_stop(self):
    #     cp = self.get_current_position()
    #
    #     if cp <= CON_CLIMB["down"] + .3:
    #         print(f"///// CLIMBER SS: min: {CON_CLIMB["down"] + .3}")
    #         return "min"
    #     if cp >= CON_CLIMB["up"] - .3:
    #         print(f"///// CLIMBER SS: max: {CON_CLIMB["up"] - .3}")
    #         return "max"
    #
    #     return None

    # def go_to_position (self, position: float) -> Command:
    #
    #     class ClimberarmMoveCommand(Command):
    #         def __init__(self, climberarm, target_position):
    #             super().__init__()
    #             self.climberarm = climberarm
    #             self.target_position = min(max(target_position, CLIMBER_ARM["down"]), CLIMBER_ARM["up"])
    #             self.addRequirements(climberarm)
    #
    #         def initialize(self):
    #             print (f"///// CLIMBER GTP T: {self.target_position}")
    #             self.climberarm.target_position = self.target_position
    #
    #         def execute(self):
    #             cp = self.climberarm.get_current_position()
    #             error = self.target_position - cp
    #
    #             # Simple proportional control
    #             kP = 1  # Adjust this gain
    #             voltage = error * kP
    #
    #             # Limit voltage for safety
    #             voltage = min(max(voltage, -6), 6) * -1
    #             print(f"///// CLIMBER GTP V: {voltage}")
    #
    #             # Apply voltage to motor
    #             self.climberarm.motor.setVoltage(voltage)
    #
    #         def isFinished(self):
    #             cp = self.climberarm.get_current_position()
    #             return abs(cp - self.target_position) < 0.2
    #         def end(self, interrupted):
    #             self.climberarm.motor.setVoltage(0)
    #     return ClimberarmMoveCommand(self, position)

    def manual(self, percentage_func: Callable[[], float]) -> Command:

        class ManualRunCommand(Command):
            def __init__(self, climber, percentage_func: Callable[[], float]):
                super().__init__()
                self.climber = climber
                self.percentage_func = percentage_func
                self.addRequirements(climber)
                self.ss = None

            def execute(self):
                percentage = self.percentage_func()  # Call function to get live trigger value
                if abs(percentage) <= 0.1:  # Ignore small values
                    self.climber.stop()
                    return

                target_rps = (percentage * self.climber.max_rpm) / 60.0
                print(f"///// CLIMBER Man R: {target_rps}")
                self.climber.velocity_request.velocity = target_rps
                self.climber.motor.set_control(self.climber.velocity_request)
                self.climber.is_running = True

            def end(self, interrupted):

                if interrupted:
                    print(f"///// CLIMBER Man End: Interrupt")
                    self.climber.velocity_request.velocity = 0
                    self.climber.motor.set_control(self.climber.velocity_request)
                    self.climber.is_running = False

                else:
                    print(f"///// CLIMBER Man End: SS")
                    cp = self.climber.get_current_position()
                    sr = CON_CLIMB["safety_retreat"]

                    if self.ss == "min":
                        self.climber.go_to_position(cp + sr).schedule()
                    if self.ss == "max":
                        self.climber.go_to_position(cp - sr).schedule()

            def isFinished(self):
                # self.ss = self.climber.safety_stop()
                #
                # if self.ss is not None:
                #     print(f"///// CLIMBER Man SS: {self.ss}")
                #     return True
                return False

        return ManualRunCommand(self, percentage_func)

    def stop(self):
        """Stop the elevator motor."""
        self.motor.set(0)
        self.is_running = False
        cp = self.climber.get_current_position()
        self.motor.set_position(cp)
