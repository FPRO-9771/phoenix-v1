from commands2 import SubsystemBase, Command
from wpilib import Timer
import math
from autonomous.auton_constants import DRIVING

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
                speed_y = self.kP * (distance - 1.0)* self.outer_self._max_speed
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
                self.distance = 0
                # self.addRequirements(outer_self.drivetrain)

            def initialize(self):
                print(f"+++++ AUTON DR limelight I")


            def execute(self):

                # print(f"+++++ AUTON DR limelight ::: Seeking")
                result = self.outer_self.limelight_handler.get_target_data(target_tag_id)
                if result:
                    # print(f"+++++ AUTON DR limelight ::: >> Found <<")
                    print(f"+++++ AUTON DR limelight ::: >> ID  : {result["tag_id"]} "
                          f" Or Y: {result["yaw"]:.3f}  "
                          f" XPos: {result["x_pos"]:.3f}  "
                          f" Dist: {result["distance"]:.3f}   <<")

                    self.distance = result["distance"]
                    speed_x = 0
                    speed_y = 0
                    rotation = 0
                    speed_x = self.calculate_drive_variable("speed_x", result["distance"])
                    speed_y = self.calculate_drive_variable("speed_y", result["x_pos"])
                    rotation = self.calculate_drive_variable("rotation", result["yaw"])

                    print(f"+++++ AUTON DR move ::: >> "
                          f" X: {speed_x:.3f}  "
                          f" Y: {speed_y:.3f}  "
                          f" R: {rotation:.3f}   <<")

                    self.outer_self._drive_robot(rotation, speed_x, speed_y)
                else:
                    self.outer_self._drive_robot(0, 0, 0)

            def end(self, interrupted):
                if interrupted:
                    print(f"+++++ AUTON DR limelight Interrupted")
                else:
                    print(f"+++++ AUTON DR limelight End")

            def isFinished(self):
                return self.on_target

            def calculate_drive_variable(self, v_type, v_input):
                const = DRIVING[v_type]
                if "engage_at_distance" in const:
                    if const["engage_at_distance"] < self.distance:
                        return 0
                if abs(v_input) < const["tolerance"]:
                    return 0
                v = v_input * const["multiplier"] * const["inverter"][self.color]
                v_sign = math.copysign(1, v)
                if "max" in const:
                    v = min(abs(v), abs(const["max"])) * v_sign
                return v + (const["add_min"] * v_sign)

        # Create and return the command
        return LimelightCommand(self, target_tag_id)

    def _drive_robot(self, rotation=0, x=0, y=0):

        """Helper method to apply drive commands."""
        # Directly use the drive request without creating a new command
        self.drivetrain.apply_request(lambda: (
            self._drive.with_rotational_rate(rotation).with_velocity_y(y).with_velocity_x(x)
        )).schedule()
