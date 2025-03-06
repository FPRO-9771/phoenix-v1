# Copyright (c) FIRST and other WPILib contributors.
# Open Source Software; you can modify and/or share it under the terms of
# the WPILib BSD license file in the root directory of this project.

import wpilib
from commands2 import CommandScheduler
from robot_container import RobotContainer

class Robot(wpilib.TimedRobot):
    def robotInit(self):
        """Initialize the robot."""
        print("Robot Initialized!")
        self.m_robotContainer = RobotContainer()
        self.m_autonomousCommand = None

    def robotPeriodic(self):
        """Run code that should execute regardless of the robot's mode."""
        CommandScheduler.getInstance().run()
        wpilib.SmartDashboard.putData("Autonomous Mode", self.m_robotContainer.chooser)

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
        print("##### AO I")
        # Get the selected autonomous command factory function
        auto_command_factory = self.m_robotContainer.get_autonomous_command()

        # Create a fresh command instance and schedule it
        if auto_command_factory is not None:
            self.m_autonomousCommand = auto_command_factory()
            self.m_autonomousCommand.schedule()

    def autonomousPeriodic(self):
        pass

    def autonomousExit(self):
        # Cancel all active commands
        scheduler = CommandScheduler.getInstance()
        scheduler.cancelAll()

    def teleopInit(self):
        """Run once when the robot enters Teleoperated mode."""
        print("##### TO I")

        # Ensure driver controls are set up in teleop mode only
        self.m_robotContainer.setup_teleop()

        # If an autonomous command was running, cancel it
        if hasattr(self, 'm_autonomousCommand') and self.m_autonomousCommand is not None:
            print("##### AM Cancel")
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


if __name__ == "__main__":
    wpilib.run(Robot)
