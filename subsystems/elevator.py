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
    Elevator subsystem that controls vertical movement using a TalonFX motor.
    Uses CANrange sensor for height measurement.
    """
    
    def __init__(self, motor_id: int, follower_motor_id: int, range_sensor_id: int):
        """Initialize the elevator subsystem.
        
        Args:
            motor_id: CAN ID of the TalonFX motor
            range_sensor_id: CAN ID of the CANRange sensor
        """
        super().__init__()
        
        # Initialize motor
        self.motor = TalonFX(motor_id)
        self.follower_motor = TalonFX(follower_motor_id)

        # Set follower motor to follow the main motor in reverse
        self.follower_motor.set_control(Follower(motor_id, oppose_master_direction=True))

        # Initialize range sensor
        self.range_sensor = CANrange(range_sensor_id)
        
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

        self.max_rpm = 5000
        self.velocity_request = VelocityVoltage(0)

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
        
        # Height limits (in meters)
        self.MIN_HEIGHT = 0.0
        self.MAX_HEIGHT = 1.5  # Adjust based on your elevator's max height
        
        # Preset heights in meters
        self.preset_heights = {
            XboxController.Button.kA: 0.0,    # Ground position
            XboxController.Button.kB: 0.5,    # Mid position
            XboxController.Button.kX: 1.0,    # High position
            XboxController.Button.kY: 1.5     # Maximum height
        }
        
        # State tracking
        self.target_height = 0.0
        self.last_reported_height = None
        self.report_threshold = 0.02  # Only report changes larger than 2cm
        
        # Offset from range sensor to actual elevator height
        # This is the distance from the sensor to the ground when elevator is at zero position
        self.SENSOR_OFFSET = 0.1  # Adjust based on your mounting position
        
    def get_current_height(self) -> float:
        """Get the current height of the elevator in meters."""
        # Get raw distance from sensor
        raw_distance = self.range_sensor.get_distance().value
        # Subtract offset to get actual elevator height
        # Note: Depending on sensor mounting, you might need to invert this
        return raw_distance - self.SENSOR_OFFSET
        
    def go_to_height(self, height: float) -> Command:
        """Create a command to move the elevator to a specific height."""
        class ElevatorMoveCommand(Command):
            def __init__(self, elevator, target_height):
                super().__init__()
                self.elevator = elevator
                # Clamp target height to safe range
                self.target_height = min(max(target_height, 
                                       elevator.MIN_HEIGHT), 
                                       elevator.MAX_HEIGHT)
                self.addRequirements(elevator)
                
            def initialize(self):
                print(f"Moving elevator to height: {self.target_height:.2f}m")
                self.elevator.target_height = self.target_height
                
            def execute(self):
                current_height = self.elevator.get_current_height()
                error = self.target_height - current_height
                
                # Simple proportional control
                kP = 4.0  # Adjust this gain
                voltage = error * kP
                
                # Limit voltage for safety
                voltage = min(max(voltage, -6), 6)
                
                # Apply voltage to motor
                self.elevator.motor.set_voltage(voltage)
                
                # Safety check
                if current_height < self.elevator.MIN_HEIGHT - 0.1 or \
                   current_height > self.elevator.MAX_HEIGHT + 0.1:
                    self.elevator.motor.set_voltage(0)
                    print(f"SAFETY STOP: Height {current_height:.2f}m outside safe range!")
                
            def isFinished(self):
                current_height = self.elevator.get_current_height()
                return abs(current_height - self.target_height) < 0.02  # 2cm tolerance
                
            def end(self, interrupted):
                self.elevator.motor.set_voltage(0)
                if interrupted:
                    print("Elevator movement interrupted")
                else:
                    print(f"Elevator reached target height: {self.target_height:.2f}m")
                    
        return ElevatorMoveCommand(self, height)

    def manual(self, percentage_func: Callable[[], float]) -> Command:

        class ManualRunCommand(Command):
            def __init__(self, elevator, percentage_func: Callable[[], float]):
                super().__init__()
                self.elevator = elevator
                self.percentage_func = percentage_func  # Store function instead of static value
                self.addRequirements(elevator)

            def initialize(self):
                print("Elevator manual command started")

            def execute(self):
                percentage = self.percentage_func()  # Call function to get live trigger value
                if abs(percentage) <= 0.1:  # Ignore small values
                    self.elevator.stop()
                    return
                #
                target_rps = (percentage * self.elevator.max_rpm) / 60.0
                self.elevator.velocity_request.velocity = target_rps
                self.elevator.motor.set_control(self.elevator.velocity_request)
                self.elevator.is_running = True
                print(f"Elevator running at {percentage * 100:.1f}% speed (RPM: {target_rps * 60:.0f})")

            def end(self, interrupted):
                print("Stopping elevator")
                self.elevator.velocity_request.velocity = 0
                self.elevator.motor.set_control(self.elevator.velocity_request)
                self.elevator.is_running = False

            def isFinished(self):
                return False  # Runs continuously while trigger is held

        return ManualRunCommand(self, percentage_func)

    def stop(self):
        """Stop the elevator motor."""
        self.motor.set(0)

    def periodic(self):
        """Periodic update function for telemetry and monitoring."""
        current_height = self.get_current_height()
        
        # Only report if height has changed significantly
        if (self.last_reported_height is None or 
            abs(current_height - self.last_reported_height) >= self.report_threshold):
            print(f"Elevator Height: {current_height:.2f}m")
            print(f"Raw Range Reading: {self.range_sensor.get_distance().value:.2f}m")
            self.last_reported_height = current_height
            
        # Check if height is within safe limits
        # if current_height < self.MIN_HEIGHT or current_height > self.MAX_HEIGHT:
        #     print(f"WARNING: Elevator height {current_height:.2f}m outside safe range!")