from commands2 import SubsystemBase, Command
from wpilib import Timer
import math


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
                # self.addRequirements(outer_self.drivetrain)

            def initialize(self):
                print(f"+++++ AUTON DR limelight I")


            def execute(self):

                print(f"+++++ AUTON DR limelight ::: Seeking")
                result = self.outer_self.limelight_handler.get_target_data(target_tag_id)
                if result:
                    print(f"+++++ AUTON DR limelight ::: >> Found <<")
                    print(f"+++++ AUTON DR limelight ::: >> ID  : {result.tag_id}     <<")
                    print(f"+++++ AUTON DR limelight ::: >> Or Y: {result.yaw} .... P: {result.pitch}, R: {result.roll} <<")
                    print(f"+++++ AUTON DR limelight ::: >> XPos: {result.x_pos}     <<")
                    print(f"+++++ AUTON DR limelight ::: >> Dist: {result.distance}     <<")

                # ToDo: I think that the LL variables should move the robot like this:
                # result.distance controls Y
                # result.x_pos controls X
                # result.yaw controls rotation

                # self.outer_self._drive_robot(rotation, 0)

            def end(self, interrupted):
                if interrupted:
                    print(f"+++++ AUTON DR limelight Interrupted")
                else:
                    print(f"+++++ AUTON DR limelight End")

            def isFinished(self):
                False

        # Create and return the command
        return LimelightCommand(self, target_tag_id)

    def _drive_robot(self, rotation=0, x=0, y=0):

        """Helper method to apply drive commands."""
        # Directly use the drive request without creating a new command
        self.drivetrain.apply_request(lambda: (
            self._drive.with_rotational_rate(rotation).with_velocity_y(y).with_velocity_x(x)
        )).schedule()
