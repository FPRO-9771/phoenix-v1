from commands2 import SubsystemBase, Command
from wpilib import Timer
import math
from phoenix6.hardware import CANrange
from phoenix6.configs import TalonFXConfiguration, Slot0Configs, CANrangeConfiguration
from phoenix6.configs.config_groups import ToFParamsConfigs, FovParamsConfigs

from autonomous.auton_constants import DRIVING, LL_DATA_SETTINGS


class AutonDrive(SubsystemBase):

    def __init__(self, drivetrain, _drive, _max_speed, _max_angular_rate, limelight_handler):
        print(f"+++++ AUTON DR I")
        super().__init__()

        self._max_speed = _max_speed
        self._max_angular_rate = _max_angular_rate
        self._drive = _drive
        self.drivetrain = drivetrain

        self.limelight_handler = limelight_handler

    def approach_target(self) -> Command:
        """
        Creates a command that turns the robot until the simulated target distance is 1.0.
        """

        class VisionApproachCommand(Command):
            def __init__(self, outer_self):
                super().__init__()
                self.outer_self = outer_self
                # self.addRequirements(outer_self.drivetrain)

                # ToDo: simulation - comment out
                self.sim_timer = None
                self.sim_iterations = 0

                # Control variables
                self.kP = 0.5
                self.distance_threshold = 1.1

            def initialize(self):
                print(f"+++++ AUTON DR approach_target I")

                self.sim_timer = Timer()
                self.sim_timer.start()
                self.sim_iterations = 0

            def execute(self):

                # ToDo: simulation - comment out
                self.sim_iterations += 1
                current_time = self.sim_timer.get()
                distance = max(1.0, 5.0 - (1.5 * current_time))
                angle = max(1.0, 30.0 - (7 * current_time))
                speed_y = self.kP * (distance - 1.0) * self.outer_self._max_speed
                rotation = (angle / 45) * self.outer_self._max_angular_rate

                # # Log execution details
                print(
                    f"n{self.sim_iterations}, t: {current_time:.2f}s, d: {distance:.2f}, tx: {angle:.2f}, y: {speed_y:.2f}, r: {rotation:.2f}")

                self.outer_self._drive_robot(rotation, 0)

            def end(self, interrupted):

                # ToDo: simulation - comment out
                elapsed = 0
                if self.sim_timer:
                    elapsed = self.sim_timer.get()
                print(f"Command ending after {self.sim_iterations} iterations, {elapsed:.2f} seconds")
                print(f"Was interrupted: {interrupted}")

                # Stop the robot
                self.outer_self._drive_robot(0, 0)

                if interrupted:
                    print(f"+++++ AUTON DR approach_target Interrupted")
                else:
                    print(f"+++++ AUTON DR approach_target End")

            def isFinished(self):

                # ToDo: simulation - comment out
                if self.sim_timer is None:
                    return True
                elapsed = self.sim_timer.get()
                distance = max(1.0, 5.0 - (1.5 * elapsed))
                return distance <= self.distance_threshold or elapsed > 5.0

        # Create and return the command
        return VisionApproachCommand(self)

    def limelight_data(self, target_tag_id=None) -> Command:

        class LimelightCommand(Command):
            def __init__(self, outer_self, _target_tag_id):
                super().__init__()
                self.outer_self = outer_self
                self.target_tag_id = _target_tag_id
                self.on_target = False
                self.color = "red"
                self.distance = 0
                # self.addRequirements(outer_self.drivetrain)

            def initialize(self):
                print(f"+++++ AUTON DR limelight I")

            def execute(self):

                # print(f"+++++ AUTON DR limelight ::: Seeking")
                result = self.outer_self.limelight_handler.get_target_data(target_tag_id)
                if result:
                    # print(f"+++++ AUTON DR limelight ::: >> Found <<")
                    # print(f"+++++ AUTON DR limelight ::: >> ID  : {result["tag_id"]} "
                    #       f" Or Y: {result["yaw"]:.3f}  "
                    #       f" Mp Y: {result["mapped"]["yaw"]:.3f}  "
                    #       f" tx  : {result["tx"]:.3f}  "
                    #       f" Dist: {result["distance"]:.3f}   <<")

                    mapped = result["mapped"]

                    print(f"+++++ AUTON DR limel_map ::: // ID  : {result["tag_id"]} "
                          f" Or Y: {mapped["yaw"]:.3f}  "
                          f" tx  : {mapped["tx"]:.3f}  "
                          f" Dist: {mapped["distance"]:.3f}   //")

            def end(self, interrupted):
                if interrupted:
                    print(f"+++++ AUTON DR limelight Interrupted")
                else:
                    print(f"+++++ AUTON DR limelight End")

            def isFinished(self):
                return self.on_target

            def map_ll_data(self, result):

                def do_multiplier(v_type, v_input):
                    const = LL_DATA_SETTINGS[v_type]
                    if "multiplier" in const:
                        return v_input * const["multiplier"]
                    else:
                        return v_input

                return {
                    "yaw": do_multiplier("yaw", result["yaw"]),
                    "tx": do_multiplier("tx", result["tx"]),
                    "distance": do_multiplier("distance", result["distance"])
                }

        # Create and return the command
        return LimelightCommand(self, target_tag_id)

    def limelight(self, target_tag_id=None) -> Command:
        """
        Creates a command that turns the robot until the simulated target distance is 1.0.
        """

        class LimelightCommand(Command):
            def __init__(self, outer_self, _target_tag_id):
                super().__init__()
                self.outer_self = outer_self
                self.target_tag_id = _target_tag_id
                self.on_target = False
                self.color = "red"
                self.distance = None
                self.speed_x = None
                self.speed_y = None
                self.rotation = None
                # self.addRequirements(outer_self.drivetrain)

            def initialize(self):
                print(f"+++++ AUTON DR limelight I")

            def execute(self):

                # print(f"+++++ AUTON DR limelight ::: Seeking")
                result = self.outer_self.limelight_handler.get_target_data(target_tag_id)
                if result:
                    mapped = result["mapped"]
                    # print(f"+++++ AUTON DR limelight ::: >> Found <<")
                    # print(f"+++++ AUTON DR limelight ::: >> ID  : {result["tag_id"]} "
                    #       f" Or Y: {mapped["yaw"]:.3f}  "
                    #       f" tx  : {mapped["tx"]:.3f}  "
                    #       f" Dist: {mapped["distance"]:.3f}   <<")

                    self.distance = mapped["distance"]
                    # self.speed_x = 0
                    # self.speed_y = 0
                    # self.rotation = 0
                    self.speed_x = self.calculate_drive_variable("speed_x", mapped["distance"])
                    self.speed_y = self.calculate_drive_variable("speed_y", mapped["tx"])
                    self.rotation = self.calculate_drive_variable("rotation", mapped["yaw"])

                    print(f"+++++ AUTON DR move ::: >> "
                          f" D: {self.distance}  "
                          f" X: {mapped["distance"]:.3f} -> {self.speed_x:.3f}  "
                          f" Y: {mapped["tx"]:.3f} -> {self.speed_y:.3f}  "
                          f" R: {mapped["yaw"]:.3f} -> {self.rotation:.3f}   <<")

                    self.on_target = self.calculate_finished()

                    self.outer_self._drive_robot(self.rotation, self.speed_x, self.speed_y)
                else:
                    print(f"+++++ AUTON DR limelight LOST")
                    self.on_target = True

            def end(self, interrupted):
                if interrupted:
                    print(f"+++++ AUTON DR limelight Interrupted")
                else:
                    print(f"+++++ AUTON DR limelight End")

                self.outer_self._drive_robot(0, 0, 0)

            def isFinished(self):
                return self.on_target

            def calculate_drive_variable(self, v_type, v_input):
                const = DRIVING[v_type]
                if "engage_at_distance" in const:
                    if const["engage_at_distance"] < self.distance:
                        return 0
                if abs(v_input) < const["target_tolerance"]:
                    return 0

                v_max = const["max"]
                close_multiplier = 1
                if "reduce_when_close" in const:
                    if const["reduce_when_close"]["distance"] > self.distance:
                        if "multiplier" in const["reduce_when_close"]:
                            close_multiplier = const["reduce_when_close"]["multiplier"]
                        if "max" in const["reduce_when_close"]:
                            v_max = const["reduce_when_close"]["max"]

                v = v_input * const["multiplier"] * close_multiplier * const["inverter"][self.color]
                v_sign = math.copysign(1, v)
                v = v + (const["add_min"] * v_sign)
                if "max" in const:
                    # print(f"max - {v_type} {v}")
                    v = min(abs(v), abs(v_max)) * v_sign
                return v

            def calculate_finished(self):
                const = DRIVING
                print(f"FIN {self.speed_x} {self.speed_y} {self.rotation}")
                if (abs(self.speed_x) < const["speed_x"]["no_spin_power"]
                        and abs(self.speed_y) < const["speed_y"]["no_spin_power"]
                        and abs(self.rotation) < const["rotation"]["no_spin_power"]):
                    print(f"+++++ AUTON DR limelight ON TARGET")
                    return True
                else:
                    return False

        # Create and return the command
        return LimelightCommand(self, target_tag_id)

    def align_pipe(self, direction: str) -> Command:
        """
        Creates a command that turns the robot until the simulated target distance is 1.0.
        """

        class AlignPipeCommand(Command):
            def __init__(self, outer_self, _direction='left'):
                super().__init__()
                self.outer_self = outer_self
                self.direction = (1 if _direction == 'left' else -1)
                self.on_target = False
                self.color = "red"
                self.distance = 0
                self.periodic_counter = 0
                # self.addRequirements(outer_self.drivetrain)

                self.range_sensor = CANrange(41)

                # Configure range sensor
                range_config = CANrangeConfiguration()

                # Configure TOF (Time of Flight) parameters
                tof_params = ToFParamsConfigs()
                # You might need to adjust these based on your needs
                range_config.with_to_f_params(tof_params)

                # Configure FOV (Field of View) parameters
                fov_params = FovParamsConfigs()
                range_config.with_fov_params(fov_params)

                # Apply configuration
                self.range_sensor.configurator.apply(range_config)

                self.raw_distance = None

            def initialize(self):
                print(f"+++++ AUTON DR align I")

            def execute(self):

                self.periodic_counter += 1

                self.raw_distance = self.range_sensor.get_distance().value

                dead_zone = 0.02
                speed_y_base = 0.55 * self.direction

                self.error = self.raw_distance - 0.58
                print(f"+++++ AUTON DR align -- {self.raw_distance:.2f} ERR: {self.error}")

                if (self.error < .15):
                    print(f"+++++ AUTON DR bang bang")
                    speed_y = self.outer_self._bang_bang_control(self.periodic_counter, self.error, speed_y_base)
                else:
                    speed_y = speed_y_base

                self.outer_self._drive_robot(0, 0, speed_y)

            def end(self, interrupted):
                if interrupted:
                    print(f"+++++ AUTON DR align Interrupted")
                else:
                    print(f"+++++ AUTON DR align End")

                self.outer_self._drive_robot(0, 0, 0)

            def isFinished(self):
                return self.error <= 0

        # Create and return the command
        return AlignPipeCommand(self, direction)

    def _bang_bang_control(self, periodic_counter, error, speed_y_base):
        dead_zone = 0.02

        if abs(error) < dead_zone:
            return 0
        else:
            if periodic_counter % 5 < 2:
                return speed_y_base
            else:
                return 0

    def _drive_robot(self, rotation=0, x=0, y=0):

        """Helper method to apply drive commands."""
        # Directly use the drive request without creating a new command
        self.drivetrain.apply_request(lambda: (
            self._drive.with_rotational_rate(rotation).with_velocity_y(y).with_velocity_x(x)
        )).schedule()
