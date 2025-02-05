from commands2 import SubsystemBase, Command
from phoenix6.hardware import TalonFX
from phoenix6.configs import TalonFXConfiguration, Slot0Configs
from phoenix6.signals import NeutralModeValue
from wpilib import XboxController, DigitalInput
from wpimath.controller import PIDController

class Elevator(SubsystemBase):
    """
    Elevator subsystem that controls vertical movement using a TalonFX motor.
    Supports preset heights mapped to Xbox controller buttons.
    """
    
    def __init__(self, motor_id: int, limit_switch_port: int = 0, gear_ratio: float = 10.0):
        """Initialize the elevator subsystem.
        
        Args:
            motor_id: CAN ID of the TalonFX motor
            limit_switch_port: DIO port for the bottom limit switch
            gear_ratio: Gear ratio between motor and elevator drum
        """
        super().__init__()
        
        # Initialize motor
        self.motor = TalonFX(motor_id)
        
        # Initialize limit switch
        self.limit_switch = DigitalInput(limit_switch_port)
        
        # Configure motor
        configs = TalonFXConfiguration()
        
        # PID configuration for position control
        slot0 = Slot0Configs()
        slot0.k_p = 0.1  # Adjust these PID values based on testing
        slot0.k_i = 0.0
        slot0.k_d = 0.0
        slot0.k_v = 0.12  # Feedforward gain
        configs.slot0 = slot0
        
        # Set motor to brake mode when stopped
        configs.motor_output.neutral_mode = NeutralModeValue.BRAKE
        
        # Apply configurations
        self.motor.configurator.apply(configs)
        
        # Constants
        self.gear_ratio = gear_ratio
        self.drum_circumference = 0.1  # meters, adjust based on your drum size
        
        # Height limits
        self.MIN_HEIGHT = 0.0  # meters
        self.MAX_HEIGHT = 1.5  # meters, adjust based on your elevator
        
        # Preset heights in meters
        self.preset_heights = {
            XboxController.Button.kA: 0.0,    # Ground position
            XboxController.Button.kB: 0.5,    # Mid position
            XboxController.Button.kX: 1.0,    # High position
            XboxController.Button.kY: 1.5     # Maximum height
        }
        
        # State tracking
        self.is_calibrated = False
        self.target_height = 0.0
        self.last_reported_height = None
        self.report_threshold = 0.02  # Only report changes larger than 2cm
        
        # Position conversion factors
        self.rotations_to_meters = self.drum_circumference / self.gear_ratio
        self.meters_to_rotations = self.gear_ratio / self.drum_circumference
        
    def calibrate(self) -> Command:
        """Create a command to calibrate the elevator by finding home position."""
        class CalibrateCommand(Command):
            def __init__(self, elevator):
                super().__init__()
                self.elevator = elevator
                self.addRequirements(elevator)
                
            def initialize(self):
                print("Starting elevator calibration...")
                
            def execute(self):
                # Slowly move down until limit switch is hit
                if not self.elevator.limit_switch.get():
                    self.elevator.motor.set_voltage(-2.0)  # Low voltage for slow movement
                else:
                    self.elevator.motor.set_voltage(0)
                    
            def end(self, interrupted):
                self.elevator.motor.set_voltage(0)
                if not interrupted and self.elevator.limit_switch.get():
                    # Reset encoder position to zero
                    self.elevator.motor.set_position(0)
                    self.elevator.is_calibrated = True
                    print("Elevator calibration complete")
                else:
                    print("Elevator calibration interrupted or failed")
                    
            def isFinished(self):
                return self.elevator.limit_switch.get()
                
        return CalibrateCommand(self)
        
    def get_current_height(self) -> float:
        """Get the current height of the elevator in meters."""
        motor_rotations = self.motor.get_position().value
        return motor_rotations * self.rotations_to_meters
        
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
                if not self.elevator.is_calibrated:
                    print("WARNING: Elevator not calibrated!")
                print(f"Moving elevator to height: {self.target_height:.2f}m")
                target_rotations = self.target_height * self.elevator.meters_to_rotations
                self.elevator.motor.set_position(target_rotations)
                
            def execute(self):
                current_height = self.elevator.get_current_height()
                # Additional safety check
                if current_height < self.elevator.MIN_HEIGHT - 0.1 or \
                   current_height > self.elevator.MAX_HEIGHT + 0.1:
                    self.elevator.motor.set_voltage(0)
                    print(f"SAFETY STOP: Height {current_height:.2f}m outside safe range!")
                
            def isFinished(self):
                current_height = self.elevator.get_current_height()
                return abs(current_height - self.target_height) < 0.02  # 2cm tolerance
                
            def end(self, interrupted):
                if interrupted:
                    print("Elevator movement interrupted")
                else:
                    print(f"Elevator reached target height: {self.target_height:.2f}m")
                    
        return ElevatorMoveCommand(self, height)
    
    def stop(self):
        """Stop the elevator motor."""
        self.motor.set_voltage(0)
        
    def periodic(self):
        """Periodic update function for telemetry and monitoring."""
        current_height = self.get_current_height()
        
        # Only report if height has changed significantly
        if (self.last_reported_height is None or 
            abs(current_height - self.last_reported_height) >= self.report_threshold):
            print(f"Elevator Height: {current_height:.2f}m")
            self.last_reported_height = current_height
            
        # Check if height is within safe limits
        if current_height < self.MIN_HEIGHT or current_height > self.MAX_HEIGHT:
            print(f"WARNING: Elevator height {current_height:.2f}m outside safe range!")
            
        # Check limit switch
        if self.limit_switch.get():
            print("Elevator at bottom limit")