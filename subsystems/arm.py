import wpilib
from commands2 import SubsystemBase, Command
from phoenix6.hardware import TalonFX
from phoenix6.configs import TalonFXConfiguration, Slot0Configs
from phoenix6.signals import NeutralModeValue
from phoenix6.controls import VelocityVoltage, PositionVoltage, VoltageOut
from typing import Callable
from constants import MOTOR_IDS, CON_ARM

# for testing
# from wpilib import Timer

class Arm(SubsystemBase):

    def __init__(self):
        """Initialize the arm subsystem."""
        super().__init__()

        # Initialize motor
        self.motor = TalonFX(MOTOR_IDS["wrist"])

        self.lock_servo = wpilib.Servo(0)

        # Configure motor
        configs = TalonFXConfiguration()

        # Velocity control configuration
        slot0 = Slot0Configs()
        slot0.k_p = 0.05  # Velocity control gains
        slot0.k_i = 0.0
        slot0.k_d = 0.0
        slot0.k_v = 0.12  # Feed forward gain
        configs.slot0 = slot0

        self.voltage_request = VoltageOut(0)

        # Set motor to coast mode when stopped
        configs.motor_output.neutral_mode = NeutralModeValue.BRAKE

        # Apply configurations
        self.motor.configurator.apply(configs)

        self.velocity_request = VelocityVoltage(0)
        self.is_running = False

        # Current target angle and state tracking
        self.is_holding_position = False

        # for testing
        # self.sim_timer = Timer()

    def get_current_position(self) -> float:
        motor_position = self.motor.get_position().value * -1

        # # for testing
        # elapsed_time = self.sim_timer.get()
        # motor_position = elapsed_time * 1

        print(f"///// ARM CP: {motor_position}")
        return motor_position

    def at_target_position(self, target: float, tolerance: float = CON_ARM["target_position_tolerance"]) -> bool:
        motor_position = (self.get_current_position())
        print(f"///// ARM TP: {motor_position} / {target}")
        return abs(self.get_current_position() - target) <= tolerance

    def safety_stop(self, towards_min):
        cp = self.get_current_position()

        if towards_min is True and cp <= CON_ARM["min"] + CON_ARM["min_max_tolerance"]:
            print(f"///// ARM SS: min: {CON_ARM['min'] + CON_ARM['min_max_tolerance']}")
            return "min"
        if towards_min is False and cp >= CON_ARM["max"] - CON_ARM["min_max_tolerance"]:
            print(f"///// ARM SS: max: {CON_ARM['max'] - CON_ARM['min_max_tolerance']}")
            return "max"

        return None

    def go_to_position(self, position: float, ignore_min = False, kp = 1) -> Command:

        class ArmMoveCommand(Command):
            def __init__(self, arm, target_position, _ignore_min, _kp):
                super().__init__()
                self.arm = arm
                self.ignore_min = _ignore_min
                if self.ignore_min:
                    self.target_position = target_position
                else:
                    self.target_position = min(max(target_position, CON_ARM["min"]), CON_ARM["max"])
                self.kP = max(_kp, 1)
                self.addRequirements(arm)

                # for testing
                # self.arm.sim_timer.start()

            def initialize(self):
                # if not self.arm.is_holding_position:  # Only print when not holding
                print(f"///// ARM GTP T: {self.target_position}")
                self.arm.target_position = self.target_position

            def execute(self):
                # use function to get accelerated and decelerated voltage
                voltage = self.get_voltage() * -1
                print(f"///// ELEV GTP V: {voltage}")

                self.arm.voltage_request.output = voltage

                # Apply using control request - this explicitly sets voltage control mode
                self.arm.motor.set_control(self.arm.voltage_request)


            def isFinished(self):
                print(f"///// ARM GTP T: {self.target_position} --FINISH--")
                return self.arm.at_target_position(self.target_position)

            def end(self, interrupted):
                if interrupted:
                    print(f"///// ARM GTP T: {self.target_position} --CANCEL--")
                self.arm.motor.setVoltage(0)

                # for testing
                # self.arm.sim_timer.reset()

            def get_voltage(self):
                const = CON_ARM["speed"]
                cp = self.arm.get_current_position()
                tp = self.target_position
                v_min = const["v_min"]
                v_max = const["v_max"]
                pa_ratio = const["cp_to_acceleration_ratio"]
                dist_from_target = abs(tp - cp)
                t_dir = 1
                if cp > tp:
                    t_dir = -1
                a = max(v_min, cp * pa_ratio)
                b = max(v_min, dist_from_target * pa_ratio)
                return min(a, b, v_max) * const["v_calc_to_limit_ratio"] * t_dir

        return ArmMoveCommand(self, position, ignore_min, kp)


    def lock(self, lock = False) -> Command:

        class ArmLockCommand(Command):
            def __init__(self, arm, lock):
                super().__init__()
                self.arm = arm
                self.timer = wpilib.Timer()

                self.target_angle = CON_ARM["lock"]["open"]

                print(f"///// ARM LOCK T: {lock}")
                if lock is True:
                    self.target_angle = CON_ARM["lock"]["closed"]
                self.addRequirements(arm)

            def initialize(self):
                # if not self.arm.is_holding_position:  # Only print when not holding
                print(f"///// ARM LOCK T: {self.target_angle}")
                self.arm.lock_servo.setAngle(self.target_angle)

                self.timer.reset()
                self.timer.start()

            def execute(self):
               pass


            def isFinished(self):
                return self.timer.hasElapsed(CON_ARM["lock"]["time_delay"])

            def end(self, interrupted):
               self.timer.stop()

        return ArmLockCommand(self, lock)

    def manual(self, percentage_func: Callable[[], float], max_rpm: float = 300) -> Command:

        class ManualRunCommand(Command):
            def __init__(self, arm, percentage_func: Callable[[], float]):
                super().__init__()
                self.arm = arm
                self.percentage_func = percentage_func  # Store function instead of static value
                self.max_rpm = max_rpm
                self.addRequirements(arm)
                self.ss = None

            def execute(self):
                percentage = self.percentage_func()  # Call function to get live trigger value
                if abs(percentage) <= 0.1:  # Ignore small values
                    self.arm.stop()
                    return
                #
                target_rps = (percentage * self.max_rpm) / 60.0
                print(f"///// ARM Man R: {target_rps}")
                self.arm.velocity_request.velocity = target_rps
                self.arm.motor.set_control(self.arm.velocity_request)
                self.arm.is_running = True

            def end(self, interrupted):

                if interrupted:
                    print(f"///// ARM Man End: Interrupt")
                    self.arm.velocity_request.velocity = 0
                    self.arm.motor.set_control(self.arm.velocity_request)
                    self.arm.is_running = False

                else:
                    print(f"///// ARM Man End: SS")
                    cp = self.arm.get_current_position()
                    sr = CON_ARM["safety_retreat"]

                    if self.ss == "min":
                        self.arm.go_to_position(cp + sr).schedule()
                    if self.ss == "max":
                        self.arm.go_to_position(cp - sr).schedule()

            def isFinished(self):
                towards_min = self.percentage_func() > 0
                self.ss = self.arm.safety_stop(towards_min)

                if self.ss is not None:
                    print(f"///// ARM Man SS: {self.ss}")
                    return True

        return ManualRunCommand(self, percentage_func)

    def stop(self):
        """Stop the arm motor."""
        self.motor.set(0)
        self.is_running = False
        cp = self.arm.get_current_position()
        self.motor.set_position(cp)

    # def hold_position(self) -> Command:
    #     """Command to hold the current position."""
    #     class HoldPositionCommand(Command):
    #         def __init__(self, arm):
    #             super().__init__()
    #             self.arm = arm
    #             self.addRequirements(arm)
    #
    #         def initialize(self):
    #             self.arm.is_holding_position = True
    #             cr = self.arm.get_current_rotation()
    #             print(f"cr {cr}")
    #             if self.arm.last_target_rotation is None:
    #                 self.arm.last_target_rotation = cr
    #                 self.arm.motor.set_position(self.arm.angle_to_motor_rotations(cr))
    #
    #         def execute(self):
    #             # Only update position if there's significant drift
    #             cr = self.arm.get_current_rotation()
    #             if abs(cr - self.arm.last_target_rotation) > 5.0:  # 5 degree threshold
    #                 self.arm.last_target_rotation = cr
    #                 self.arm.motor.set_position(self.arm.angle_to_motor_rotations(cr))
    #
    #         def end(self, interrupted):
    #             self.arm.is_holding_position = False
    #             self.arm.last_target_rotation = None
    #
    #     return HoldPositionCommand(self)

    def periodic(self):
        """Periodic update function."""
        pass
        # cr = self.get_current_rotation()
        # if cr < self.MIN_ANGLE or cr > self.MAX_ANGLE:
        #     print(f"WARNING: Arm angle {cr} outside safe range!")
