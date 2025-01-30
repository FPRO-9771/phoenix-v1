from commands2 import SubsystemBase, Command
from phoenix6.hardware import TalonFX
from phoenix6.configs import TalonFXConfiguration, Slot0Configs
from phoenix6.signals import NeutralModeValue
from wpilib import XboxController
from wpimath.controller import PIDController

class Elevator(SubsystemBase):
    """
    Elevator subsystem that controls vertical movement using a TalonFX motor.
    Supports preset heights mapped to Xbox controller buttons.
    """
    
    def __init__(self, motor_id: int, gear_ratio: float = 10.0):
        """Initialize the elevator subsystem.
        
        Args:
            motor_id: CAN ID of the TalonFX motor
            gear_ratio: Gear ratio between motor and elevator drum
        """
        super().__init__()
        
        # Initialize motor
        self.motor = TalonFX(motor_id)
        
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
        
        # Preset heights in meters
        self.preset_heights = {
            XboxController.Button.kA: 0.0,    # Ground position
            XboxController.Button.kB: 0.5,    # Mid position
            XboxController.Button.kX: 1.0,    # High position
            XboxController.Button.kY: 1.5     # Maximum height
        }
        
        # Current target height
        self.target_height = 0.0
        
        # Position conversion factors
        self.rotations_to_meters = self.drum_circumference / self.gear_ratio
        self.meters_to_rotations = self.gear_ratio / self.drum_circumference
        
    def set_preset_height(self, button: XboxController.Button, height: float):
        """Set a preset height for a specific button.
        
        Args:
            button: XboxController button enum
            height: Target height in meters
        """
        self.preset_heights[button] = height
        
    def get_current_height(self) -> float:
        """Get the current height of the elevator in meters."""
        motor_rotations = self.motor.get_position().value
        return motor_rotations * self.rotations_to_meters
        
    def go_to_height(self, height: float) -> Command:
        """Create a command to move the elevator to a specific height.
        
        Args:
            height: Target height in meters
        """
        class ElevatorMoveCommand(Command):
            def __init__(self, elevator, target_height):
                super().__init__()
                self.elevator = elevator
                self.target_height = target_height
                self.addRequirements(elevator)
                
            def initialize(self):
                print(f"Moving elevator to height: {self.target_height}m")
                target_rotations = self.target_height * self.elevator.meters_to_rotations
                self.elevator.motor.set_position(target_rotations)
                
            def isFinished(self):
                current_height = self.elevator.get_current_height()
                return abs(current_height - self.target_height) < 0.02  # 2cm tolerance
                
            def end(self, interrupted):
                if interrupted:
                    print("Elevator movement interrupted")
                else:
                    print("Elevator reached target height")
                    
        return ElevatorMoveCommand(self, height)
    
    def stop(self):
        """Stop the elevator motor."""
        self.motor.set_position(self.motor.get_position().value)
        
    def periodic(self):
        """Periodic update function."""
        # Add any periodic updates needed (e.g., logging, telemetry)
        pass    