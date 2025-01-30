from commands2 import SubsystemBase, Command
from phoenix6.hardware import TalonFX
from phoenix6.configs import TalonFXConfiguration, Slot0Configs
from phoenix6.signals import NeutralModeValue
from wpilib import XboxController
from wpimath.geometry import Rotation2d
import math

class Arm(SubsystemBase):
    """
    Arm subsystem that controls rotational movement using a TalonFX motor.
    Supports preset angles mapped to controller buttons and has soft limits
    to prevent over-rotation.
    """
    
    def __init__(self, motor_id: int, gear_ratio: float = 50.0):
        """Initialize the arm subsystem."""
        super().__init__()
        
        # Initialize motor
        self.motor = TalonFX(motor_id)
        
        # Configure motor
        configs = TalonFXConfiguration()
        
        # PID configuration for position control
        slot0 = Slot0Configs()
        slot0.k_p = 4.0    # Position control gains - will need tuning
        slot0.k_i = 0.0
        slot0.k_d = 0.1
        slot0.k_v = 0.12   # Feedforward for gravity compensation
        configs.slot0 = slot0
        
        # Set motor to brake mode when stopped
        configs.motor_output.neutral_mode = NeutralModeValue.BRAKE
        
        # Apply configurations
        self.motor.configurator.apply(configs)
        
        # Constants
        self.gear_ratio = gear_ratio
        
        # Angle limits in degrees
        self.MIN_ANGLE = 0.0     # Assuming 0 is straight down
        self.MAX_ANGLE = 180.0   # Maximum rotation
        
        # Preset angles in degrees
        self.preset_angles = {
            XboxController.Button.kLeftBumper: 0.0,    # Stowed position
            XboxController.Button.kRightBumper: 90.0,  # Horizontal position
            XboxController.Button.kBack: 45.0,         # Mid position
            XboxController.Button.kStart: 135.0        # High position
        }
        
        # Current target angle and state tracking
        self.target_angle = 0.0
        self.is_holding_position = False
        self.last_target_angle = None
        
    def set_preset_angle(self, button: XboxController.Button, angle: float):
        """Set a preset angle for a specific button."""
        clamped_angle = min(max(angle, self.MIN_ANGLE), self.MAX_ANGLE)
        self.preset_angles[button] = clamped_angle
        
    def get_current_angle(self) -> float:
        """Get the current angle of the arm in degrees."""
        motor_rotations = self.motor.get_position().value
        arm_rotations = motor_rotations / self.gear_ratio
        return (arm_rotations * 360.0) % 360.0
        
    def angle_to_motor_rotations(self, angle: float) -> float:
        """Convert an angle in degrees to motor rotations."""
        return (angle / 360.0) * self.gear_ratio
        
    def go_to_angle(self, angle: float) -> Command:
        """Create a command to move the arm to a specific angle."""
        class ArmMoveCommand(Command):
            def __init__(self, arm, target_angle):
                super().__init__()
                self.arm = arm
                self.target_angle = min(max(target_angle, arm.MIN_ANGLE), arm.MAX_ANGLE)
                self.addRequirements(arm)
                self.reported_completion = False
                
            def initialize(self):
                if not self.arm.is_holding_position:  # Only print when not holding
                    print(f"Moving arm to angle: {self.target_angle} degrees")
                self.arm.motor.set_position(self.arm.angle_to_motor_rotations(self.target_angle))
                
            def isFinished(self):
                current_angle = self.arm.get_current_angle()
                at_target = abs(current_angle - self.target_angle) < 2.0  # 2 degree tolerance
                if at_target and not self.reported_completion and not self.arm.is_holding_position:
                    print(f"Arm reached target angle: {self.target_angle}")
                    self.reported_completion = True
                return at_target
                
            def end(self, interrupted):
                if interrupted and not self.arm.is_holding_position:
                    print("Arm movement interrupted")
                    
        return ArmMoveCommand(self, angle)
    
    def stop(self):
        """Stop the arm motor."""
        self.motor.set_position(self.motor.get_position().value)
        
    def hold_position(self) -> Command:
        """Command to hold the current position."""
        class HoldPositionCommand(Command):
            def __init__(self, arm):
                super().__init__()
                self.arm = arm
                self.addRequirements(arm)
                
            def initialize(self):
                self.arm.is_holding_position = True
                current_angle = self.arm.get_current_angle()
                if self.arm.last_target_angle is None:
                    self.arm.last_target_angle = current_angle
                    self.arm.motor.set_position(self.arm.angle_to_motor_rotations(current_angle))
                
            def execute(self):
                # Only update position if there's significant drift
                current_angle = self.arm.get_current_angle()
                if abs(current_angle - self.arm.last_target_angle) > 5.0:  # 5 degree threshold
                    self.arm.last_target_angle = current_angle
                    self.arm.motor.set_position(self.arm.angle_to_motor_rotations(current_angle))
                
            def end(self, interrupted):
                self.arm.is_holding_position = False
                self.arm.last_target_angle = None
                
        return HoldPositionCommand(self)
        
    def periodic(self):
        """Periodic update function."""
        current_angle = self.get_current_angle()
        if current_angle < self.MIN_ANGLE or current_angle > self.MAX_ANGLE:
            print(f"WARNING: Arm angle {current_angle} outside safe range!")