# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Robot Development Commands

### Environment Setup
```bash
# Create and activate virtual environment (.venv)
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
# OR install specific packages:
pip install wpilib robotpy phoenix6 robotpy[commands2] pynetworktables
```

### Running and Deployment
```bash
# Run robot simulation
robotpy sim

# Deploy to RoboRIO (skipping tests due to known issues)
robotpy deploy --skip-tests

# Sync packages to RoboRIO
robotpy sync

# Deploy with tests (may fail due to telemetry issues)
robotpy deploy
```

### Development and Debugging
```bash
# Run specific test
python -m pytest tests/test_placeholder.py

# Check Python version
python3 --version
```

## Code Architecture

### Core Structure
This is a **FIRST Robotics Competition (FRC) robot codebase** for robot "Ruby" using:
- **WPILib/RobotPy** framework for robot control
- **Phoenix 6** for CTRE motor controllers and swerve drive
- **Commands2** for command-based robot programming

### Main Components

**Entry Points:**
- `main.py` - Main robot entry point using RobotBase.startRobot()
- `robot.py` - Core robot class extending TimedRobot with mode-specific methods

**Robot Architecture:**
- `robot_container.py` - Central container managing subsystems, controllers, and command bindings
- `constants.py` - Hardware configuration constants (motor IDs, mechanism limits)
- `generated/tuner_constants.py` - Auto-generated Phoenix Tuner X constants for drivetrain

**Subsystems** (`subsystems/`):
- `command_swerve_drivetrain.py` - Swerve drive implementation using Phoenix 6
- `arm.py` - Robotic arm subsystem for coral manipulation
- `elevator.py` - Vertical elevator mechanism
- `shooter.py` - Coral shooting mechanism
- `climber.py` - End-game climbing mechanism

**Autonomous** (`autonomous/`):
- `auton_operator.py` - High-level autonomous command sequences
- `auton_mode_selector.py` - Autonomous mode selection system
- `auton_modes.py` - Individual autonomous routines
- Command-based architecture with complex multi-subsystem sequences

**Handlers:**
- `limelight_handler.py` - Vision processing integration
- `telemetry.py` - Robot telemetry and logging system

### Key Dependencies
- **robotpy_version**: 2025.3.1.1
- **phoenix6**: 25.2.2 (CTRE Phoenix 6 for swerve drive)
- **wpilib**: 2025.3.1.1
- **limelightlib-python**: Vision processing
- **pynetworktables**: NetworkTables communication

### Hardware Configuration
**Motors** (constants.py):
- Elevator: Motors 20, 21
- Arm/Wrist: Motor 22
- Shooter: Motor 25
- Climber: Motor 26
- Swerve drive modules configured via Phoenix Tuner

**Control Systems:**
- Dual Xbox controllers (driver: port 0, operator: port 1)
- Field-centric swerve drive with speed/rotation limiting
- Position-based control for arm and elevator mechanisms

### Known Issues
- Telemetry error: `Translation2d` object missing `minus` attribute (telemetry.py:52)
- Tests may require `--skip-tests` flag for successful deployment
- Some autonomous commands may have debug print statements that should be cleaned up

### Development Notes
- Robot designed for 2025 FRC season (Reefscape game)
- Mechanisms designed for coral manipulation and reef scoring
- Uses Phoenix 6 swerve implementation with advanced features like SysId
- Command-based architecture allows complex autonomous sequences
- Simulation support included for development without hardware