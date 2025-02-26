from commands2 import SubsystemBase, Command
from phoenix6.hardware import TalonFX
from phoenix6.configs import TalonFXConfiguration, Slot0Configs
from phoenix6.signals import NeutralModeValue
from phoenix6.controls import VelocityVoltage, Follower
from typing import Callable
from constants import MOTOR_IDS, ELEVATOR_ROTATIONS, ARM_ROTATIONS


class Elevator(SubsystemBase):

    def __init__(self, max_rpm: float = 2000):
        super().__init__()

        # Initialize motor
        self.motor = TalonFX(MOTOR_IDS["elevator_right"])
        self.follower_motor = TalonFX(MOTOR_IDS["elevator_left"])

        # Set follower motor to follow the main motor in reverse
        self.follower_motor.set_control(Follower(MOTOR_IDS["elevator_right"], oppose_master_direction=True))

        # Configure motor
        motor_configs = TalonFXConfiguration()

        # PID configuration for position control
        slot0 = Slot0Configs()
        slot0.k_p = 0.1  # Adjust these PID values based on testing
        slot0.k_i = 0.0
        slot0.k_d = 0.0
        slot0.k_v = 0.12  # Feedforward gain
        motor_configs.slot0 = slot0

        # Set motor to brake mode when stopped
        motor_configs.motor_output.neutral_mode = NeutralModeValue.BRAKE

        # Apply motor configurations
        self.motor.configurator.apply(motor_configs)

        self.max_rpm = max_rpm
        self.velocity_request = VelocityVoltage(0)
        self.is_running = False

        # Current target angle and state tracking
        self.is_holding_position = False

    def get_current_position(self) -> float:
        motor_position = self.motor.get_position().value * -1
        print(f"///// ELEV CP: {motor_position}")
        return motor_position

    def at_target_position(self, target: float, tolerance: float = ELEVATOR_ROTATIONS["target_position_tolerance"]) -> bool:
        motor_position = (self.get_current_position())
        print(f"///// ELEV TP: {motor_position} / {target}")
        return abs(self.get_current_position() - target) <= tolerance

    def safety_stop(self, direction_up):
        cp = self.get_current_position()

        if direction_up is False and cp <= ELEVATOR_ROTATIONS["min"] + ELEVATOR_ROTATIONS["min_max_tolerance"]:
            print(f"///// ELEV SS: min: {ELEVATOR_ROTATIONS['min'] + ELEVATOR_ROTATIONS['min_max_tolerance']}")
            return "min"
        if direction_up is True and cp >= ELEVATOR_ROTATIONS["max"] - ELEVATOR_ROTATIONS["min_max_tolerance"]:
            print(f"///// ELEV SS: max: {ELEVATOR_ROTATIONS['max'] - ELEVATOR_ROTATIONS['min_max_tolerance']}")
            return "max"

        return None

    def go_to_position(self, position: float) -> Command:

        class ElevatorMoveCommand(Command):
            def __init__(self, elevator, target_position):
                super().__init__()
                self.elevator = elevator
                self.target_position = min(max(target_position, ELEVATOR_ROTATIONS["min"]), ELEVATOR_ROTATIONS["max"])
                self.addRequirements(elevator)

            def initialize(self):
                print(f"///// ELEV GTP T: {self.target_position}")
                self.elevator.target_position = self.target_position

            def execute(self):
                cp = self.elevator.get_current_position()
                error = self.target_position - cp

                # Simple proportional control
                kP = 1  # Adjust this gain
                voltage = error * kP

                # Limit voltage for safety
                voltage = min(max(voltage, - ELEVATOR_ROTATIONS["voltage_limit"]), ELEVATOR_ROTATIONS["voltage_limit"]) * -1
                print(f"///// ELEV GTP V: {voltage}")

                # Apply voltage to motor
                self.elevator.motor.setVoltage(voltage)

            def isFinished(self):
                cp = self.elevator.get_current_position()
                return abs(cp - self.target_position)

            def end(self, interrupted):
                self.elevator.motor.setVoltage(0)

        return ElevatorMoveCommand(self, position)

    def manual(self, percentage_func: Callable[[], float]) -> Command:

        class ManualRunCommand(Command):
            def __init__(self, elevator, percentage_func: Callable[[], float]):
                super().__init__()
                self.elevator = elevator
                self.percentage_func = percentage_func  # Store function instead of static value
                self.addRequirements(elevator)
                self.ss = None

            # def initialize(self):

            def execute(self):
                percentage = self.percentage_func()  # Call function to get live trigger value
                print(f"///// ELEV Man P: {percentage}")
                if abs(percentage) <= 0.1:  # Ignore small values
                    self.elevator.stop()
                    return
                #
                target_rps = (percentage * self.elevator.max_rpm) / 60.0
                # print(f"///// ELEV Man R: {target_rps}")
                self.elevator.velocity_request.velocity = target_rps
                self.elevator.motor.set_control(self.elevator.velocity_request)
                self.elevator.is_running = True

            def end(self, interrupted):
                if interrupted:
                    print(f"///// ARM Man End: Interrupt")
                    self.elevator.velocity_request.velocity = 0
                    self.elevator.motor.set_control(self.elevator.velocity_request)
                    self.elevator.is_running = False

                else:
                    print(f"///// ARM Man End: SS")
                    cp = self.elevator.get_current_position()
                    sr = ELEVATOR_ROTATIONS["safety_retreat"]

                    if self.ss == "min":
                        self.elevator.go_to_position(cp + sr).schedule()
                    if self.ss == "max":
                        self.elevator.go_to_position(cp - sr).schedule()

            def isFinished(self):
                direction_up = self.percentage_func() < 0
                self.ss = self.elevator.safety_stop(direction_up)

                if self.ss is not None:
                    print(f"///// ELEV Man SS: {self.ss}")
                    return True

        return ManualRunCommand(self, percentage_func)

    def stop(self):
        """Stop the elevator motor."""
        self.motor.set(0)
        self.is_running = False
        cp = self.elevator.get_current_position()
        self.motor.set_position(cp)

    def periodic(self):
        """Periodic update function for telemetry and monitoring."""
        # current_height = self.get_current_height()
        #
        # # Only report if height has changed significantly
        # if (self.last_reported_height is None or
        #         abs(current_height - self.last_reported_height) >= self.report_threshold):
        #     # print(f"Elevator Height: {current_height:.2f}m")
        #     # print(f"Raw Range Reading: {self.range_sensor.get_distance().value:.2f}m")
        #     self.last_reported_height = current_height

        # Check if height is within safe limits
        # if current_height < self.MIN_HEIGHT or current_height > self.MAX_HEIGHT:
        #     print(f"WARNING: Elevator height {current_height:.2f}m outside safe range!")
