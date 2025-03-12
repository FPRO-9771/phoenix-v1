from commands2 import SubsystemBase, Command
from wpilib import Timer
import math
from phoenix6.hardware import CANrange
from phoenix6.configs import TalonFXConfiguration, Slot0Configs, CANrangeConfiguration
from phoenix6.configs.config_groups import ToFParamsConfigs, FovParamsConfigs

from autonomous.auton_constants import DRIVING, LL_DATA_SETTINGS, CANRANGE


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
                result = self.outer_self.limelight_handler.get_target_data(self.target_tag_id)
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
                          f" Dist: {mapped["distance"]:.3f}   "
                          f" Targ: {self.target_tag_id}//")

                    if self.target_tag_id is not None and mapped["id"] != self.target_tag_id:
                        self.on_target = True

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
                result = self.outer_self.limelight_handler.get_target_data(self.target_tag_id)
                if result:

                    mapped = result["mapped"]
                    # print(f"+++++ AUTON DR limelight ::: >> Found <<")
                    # print(f"+++++ AUTON DR limelight ::: >> ID  : {result["tag_id"]} "
                    #       f" Or Y: {mapped["yaw"]:.3f}  "
                    #       f" tx  : {mapped["tx"]:.3f}  "
                    #       f" Dist: {mapped["distance"]:.3f}   <<")

                    if self.target_tag_id is not None and mapped["id"] != self.target_tag_id:
                        self.on_target = True
                        return

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

    def align_pipe(self, direction='left', move=True) -> Command:
        """
        Creates a command that turns the robot until the simulated target distance is 1.0.
        """

        class AlignPipeCommand(Command):
            def __init__(self, outer_self, _direction, _move):
                super().__init__()
                self.outer_self = outer_self
                self.on_target = False
                self.color = "red"
                self.distance = 0
                self.periodic_counter = 0

                direction_opp = ('right' if _direction == 'left' else 'left')
                self.direction = _direction
                self.direction_multiplier = (1 if _direction == 'left' else -1)
                self.move = _move

                self.sensors = {
                    "right": {
                        "device": CANrange(42)
                    },
                    "left": {
                        "device": CANrange(41)
                    }
                }

                range_config = CANrangeConfiguration()
                tof_params = ToFParamsConfigs()
                range_config.with_to_f_params(tof_params)
                fov_params = FovParamsConfigs()
                fov_params.with_fov_range_x(7)
                fov_params.with_fov_range_y(7)
                range_config.with_fov_params(fov_params)

                # Apply configuration
                self.sensors["right"]["device"].configurator.apply(range_config)
                self.sensors["left"]["device"].configurator.apply(range_config)

                self.sensor = self.sensors[direction_opp]

                self.raw_distance = None

            def initialize(self):
                print(f"+++++ AUTON DR align I")

            def execute(self):

                self.periodic_counter += 1

                d_raw = self.sensor["device"].get_distance().value
                d_avg = self.getAvgReading(d_raw)

                speed_y_base = CANRANGE["speed"] * self.direction_multiplier

                self.error = d_avg - CANRANGE[self.direction]["target"]
                print(f"+++++ AUTON DR align -- Dir: {self.direction}   ERR: {self.error:.2f}   "
                      f"Bang: {self.error < CANRANGE[self.direction]["bang"]}   Raw:  {d_raw:.2f}   Avg: {d_avg:.2f}")

                if self.move is True:
                    if self.error < CANRANGE[self.direction]["bang"]:
                        # print(f"+++++ AUTON DR bang bang")
                        speed_y = self.outer_self._bang_bang_control(self.periodic_counter, self.error, speed_y_base)
                    else:
                        speed_y = speed_y_base

                    print(f"self.periodic_counter - {self.periodic_counter}")

                    self.outer_self._drive_robot(0, 0, speed_y)

            def end(self, interrupted):
                if interrupted:
                    print(f"+++++ AUTON DR align Interrupted")
                else:
                    print(f"+++++ AUTON DR align End")

                self.outer_self._drive_robot(0, 0, 0)

            def isFinished(self):
                if self.move is True:
                    return self.error <= 0 or self.periodic_counter > CANRANGE[self.direction]["max_time"]
                else:
                    return False

            def getAvgReading(self, new_range):
                if "d_range" not in self.sensor: self.sensor["d_range"] = []
                self.sensor["d_range"].append(new_range)
                if len(self.sensor["d_range"]) > 3:
                    self.sensor["d_range"].pop(0)
                return sum(self.sensor["d_range"]) / len(self.sensor["d_range"])

        # Create and return the command
        return AlignPipeCommand(self, direction, move)

    def _bang_bang_control(self, periodic_counter, error, speed_y_base):

        if periodic_counter % 4 == 1:
            return speed_y_base
        else:
            return 0

    def back_and_rotate(self, rotation_speed:float) -> Command:
        """
        Creates a command that turns the robot until the simulated target distance is 1.0.
        """

        class BackAndRotateCommand(Command):
            def __init__(self, outer_self, _rotation_speed):
                super().__init__()
                self.outer_self = outer_self
                self.rotation_speed = _rotation_speed
                self.periodic_counter = 0
                self.speed_x = -1
                self.speed_y = 0
                self.rotation = _rotation_speed
                # self.addRequirements(outer_self.drivetrain)

            def initialize(self):
                print(f"+++++ AUTON DR limelight I")

            def execute(self):

                self.periodic_counter += 1
                self.outer_self._drive_robot(self.rotation, self.speed_x, self.speed_y)

            def end(self, interrupted):
                if interrupted:
                    print(f"+++++ AUTON DR back_and_rotate Interrupted")
                else:
                    print(f"+++++ AUTON DR back_and_rotate End")

                self.outer_self._drive_robot(0, 0, 0)

            def isFinished(self):
                return self.periodic_counter > 20

        # Create and return the command
        return BackAndRotateCommand(self, rotation_speed)

    def _drive_robot(self, rotation=0, x=0, y=0):

        """Helper method to apply drive commands."""
        # Directly use the drive request without creating a new command
        self.drivetrain.apply_request(lambda: (
            self._drive.with_rotational_rate(rotation).with_velocity_y(y).with_velocity_x(x)
        )).schedule()
