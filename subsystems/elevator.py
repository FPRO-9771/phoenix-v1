from commands2 import SubsystemBase, Command
from phoenix6.hardware import TalonFX
from phoenix6.configs import TalonFXConfiguration
from phoenix6.signals import NeutralModeValue
from phoenix6.hardware import CANrange
from wpilib import SmartDashboard
from typing import Dict
from commands2 import SubsystemBase, Command
from phoenix6.hardware import TalonFX, CANrange
from phoenix6.configs import TalonFXConfiguration, Slot0Configs, CANrangeConfiguration
from phoenix6.configs.config_groups import ToFParamsConfigs, FovParamsConfigs
from phoenix6.signals import NeutralModeValue
from phoenix6.controls import VelocityVoltage, Follower
from wpilib import XboxController
from typing import Callable

class Elevator(SubsystemBase):
    """
    Elevator subsystem using TalonFX motors and CANrange sensor for height measurement.
    """
    
    # Define preset heights (in centimeters)
    PRESET_HEIGHTS = {
        'ZERO': 0.0,
        'LOW': 30.0,
        'MEDIUM': 90.0,
        'HIGH': 150.0,
        'MAX': 180.0  # Maximum safe height
    }

    def __init__(self, motor_id: int, follower_motor_id: int, range_sensor_id: int):
        """Initialize elevator with motor controllers and range sensor."""
        super().__init__()

        # Constants
        self.MIN_HEIGHT = 0.0  # Minimum height in cm
        self.MAX_HEIGHT = self.PRESET_HEIGHTS['MAX']  # Maximum height in cm
        self.TOLERANCE = 1.0  # Position tolerance in cm
        self.MAX_SPEED = 0.7  # Maximum motor speed (0 to 1)
        self.MIN_SPEED = 0.1  # Minimum motor speed to overcome friction
        self.REPORT_THRESHOLD = 0.5  # Minimum change in height to report (cm)

        # Motors
        self.motor = TalonFX(motor_id)
        self.follower_motor = TalonFX(follower_motor_id)
        
        # Configure follower
        self.follower_motor.set_control(self.motor)
        
        # Range Sensor
        self.range_sensor = CANrange(range_sensor_id)
        self.range_sensor = CANrange(range_sensor_id)

        # Configure range sensor
        range_config = CANrangeConfiguration()

        # Configure TOF (Time of Flight) parameters
        tof_params = ToFParamsConfigs()

        tof_params = ToFParamsConfigs()
        tof_params.min_distance = 0.05  # Set the minimum measurable distance (5cm)
        tof_params.max_distance = 2.0  # Set max limit (e.g., 2 meters)
        range_config.with_to_f_params(tof_params)
        # You might need to adjust these based on your needs
        range_config.with_to_f_params(tof_params)

        # Configure FOV (Field of View) parameters
        fov_params = FovParamsConfigs()
        range_config.with_fov_params(fov_params)
        # Motor configuration
        configs = TalonFXConfiguration()
        configs.motor_output.neutral_mode = NeutralModeValue.BRAKE
        self.motor.configurator.apply(configs)

        # Control variables
        self.target_height = None
        self.last_reported_height = None
        
        # Xbox controller button mappings for preset heights
        self.preset_heights = {
            1: self.PRESET_HEIGHTS['ZERO'],    # A button
            2: self.PRESET_HEIGHTS['LOW'],     # B button
            3: self.PRESET_HEIGHTS['MEDIUM'],  # X button
            4: self.PRESET_HEIGHTS['HIGH']     # Y button
        }

    def get_current_height(self) -> float:
        """Returns the elevator's current height in centimeters."""
        return self.range_sensor.get_distance().value * 100  # Convert meters to cm

    def go_to_height(self, target_height: float) -> Command:
        """
        Command to move elevator to a specific height.
        Returns a Command object that can be used by the command scheduler.
        """
        target = max(self.MIN_HEIGHT, min(target_height, self.MAX_HEIGHT))
        
        def initialize():
            self.target_height = target
            print(f"Moving elevator to height: {target:.1f} cm")
            
        def execute():
            current_height = self.get_current_height()
            error = self.target_height - current_height
            
            # Calculate proportional control with minimum speed
            raw_speed = error * 0.02  # Proportional gain
            if abs(raw_speed) > 0:
                speed = max(min(abs(raw_speed), self.MAX_SPEED), self.MIN_SPEED)
                speed *= -1 if raw_speed < 0 else 1
            else:
                speed = 0
                
            self.motor.set(speed)
            
        def isFinished() -> bool:
            return abs(self.get_current_height() - self.target_height) < self.TOLERANCE
            
        def end(interrupted: bool):
            self.motor.set(0)
            self.target_height = None
            if not interrupted:
                print(f"Reached target height: {self.get_current_height():.1f} cm")
                
        return Command(
            initialize_routine=initialize,
            execute_routine=execute,
            is_finished_routine=isFinished,
            end_routine=end,
            requirements=[self]
        )

    def stop(self):
        """Stops the elevator motors."""
        self.motor.set(0)
        self.target_height = None

    def periodic(self):
        """Periodic update function for telemetry and monitoring."""
        current_height = self.get_current_height()
        
        # Update dashboard with current height
        SmartDashboard.putNumber("Elevator Height (cm)", current_height)
        SmartDashboard.putNumber("Elevator Target Height (cm)", 
                                self.target_height if self.target_height is not None else -1)
        
        # Only report if height has changed significantly
        if (self.last_reported_height is None or 
            abs(current_height - self.last_reported_height) >= self.REPORT_THRESHOLD):
            print(f"Elevator Height: {current_height:.1f} cm")
            self.last_reported_height = current_height
            
        # Check if height is within safe limits
        if current_height < self.MIN_HEIGHT or current_height > self.MAX_HEIGHT:
            print(f"WARNING: Elevator height {current_height:.1f} cm outside safe range!")

    def get_preset_heights(self) -> Dict[int, float]:
        """Returns the mapping of controller buttons to preset heights."""
        return self.preset_heights.copy()