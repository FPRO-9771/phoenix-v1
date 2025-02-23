# Copyright (c) FIRST and other WPILib contributors.
# Open Source Software; you can modify and/or share it under the terms of
# the WPILib BSD license file in the root directory of this project.

import os

# Delete old log files at startup
for log_file in ["profiling_log.txt", "atexit_log.txt", "robot_profile.prof"]:
    if os.path.exists(log_file):
        os.remove(log_file)
        print(f"🗑 Deleted old log file: {log_file}")

import cProfile
import pstats
import io
import time
import atexit

import wpilib
from commands2 import CommandScheduler
from robot_container import RobotContainer

class Robot(wpilib.TimedRobot):
    profiler = cProfile.Profile()

    def __init__(self):
        """Robot constructor: Ensure attributes always exist."""
        super().__init__()
        self.m_robotContainer = None
        self.m_autonomousCommand = None
        self.last_log_time = time.time()

    def robotInit(self):
        """Initialize the robot."""
        print("Robot Initialized!")
        self.m_robotContainer = RobotContainer()
        self.m_autonomousCommand = None
        self.profiler.enable()


    def robotPeriodic(self):
        """Run code that should execute regardless of the robot's mode."""
        CommandScheduler.getInstance().run()

        # Print stats every 5 seconds, not every loop
        if time.time() - self.last_log_time > 5:
            self.last_log_time = time.time()
            with open("profiling_log.txt", "a") as log_file:
                stream = io.StringIO()
                stats = pstats.Stats(self.profiler, stream=stream)
                stats.strip_dirs().sort_stats("time").print_stats(10)  # Top 10 slowest functions

                log_file.write(f"\n----- Profiling Log at {time.strftime('%H:%M:%S')} -----\n")
                log_file.write(stream.getvalue())
                log_file.flush()  # Ensure immediate writing

    def disabledInit(self):
        """Run once when the robot enters Disabled mode."""
        pass

    def disabledPeriodic(self):
        """Run periodically while the robot is in Disabled mode."""
        pass

    def disabledExit(self):
        """Run once when the robot exits Disabled mode."""
        pass

    def autonomousInit(self):
        """Run once when the robot enters Autonomous mode."""
        self.m_autonomousCommand = self.m_robotContainer.get_autonomous_command()

        if self.m_autonomousCommand is not None:
            self.m_autonomousCommand.schedule()

    def autonomousPeriodic(self):
        """Run periodically during Autonomous mode."""
        pass

    def autonomousExit(self):
        """Run once when the robot exits Autonomous mode."""
        pass

    def teleopInit(self):
        """Run once when the robot enters Teleoperated mode."""
        if self.m_autonomousCommand is not None:
            self.m_autonomousCommand.cancel()

    def teleopPeriodic(self):
        """Run periodically during Teleoperated mode."""
        pass

    def teleopExit(self):
        """Run once when the robot exits Teleoperated mode."""
        pass

    def testInit(self):
        """Run once when the robot enters Test mode."""
        CommandScheduler.getInstance().cancelAll()

    def testPeriodic(self):
        """Run periodically during Test mode."""
        pass

    def testExit(self):
        """Run once when the robot exits Test mode."""
        pass

    def simulationPeriodic(self):
        """Run periodically in simulation."""
        pass

    @staticmethod
    def save_profile_data():
        """Ensure profiling data is saved when the program exits."""
        log_filename = "atexit_log.txt"

        with open(log_filename, "a") as log_file:
            log_file.write(f"\n[{time.strftime('%H:%M:%S')}] atexit triggered!\n")

        print("⏹ Stopping profiling and saving to robot_profile.prof...")

        # ✅ Use the class-level `Robot.profiler` directly
        if hasattr(Robot, "profiler"):
            Robot.profiler.disable()
            Robot.profiler.dump_stats("robot_profile.prof")

            with open(log_filename, "a") as log_file:
                log_file.write(f"[{time.strftime('%H:%M:%S')}] Profiling data saved to robot_profile.prof\n")

            print("📊 Profiling data successfully saved to robot_profile.prof")
        else:
            print("⚠️ Warning: Profiler not found, skipping save.")

# Ensure profiling is saved when the program exits
atexit.register(Robot.save_profile_data)


if __name__ == "__main__":
    wpilib.run(Robot)
