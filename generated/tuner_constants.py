from phoenix6.configs import (
    CANcoderConfiguration,
    CurrentLimitsConfigs,
    Pigeon2Configuration,
    Slot0Configs,
    TalonFXConfiguration,
)
from phoenix6.swerve import (
    SwerveDrivetrainConstants,
    SwerveModuleConstantsFactory,
    SteerFeedbackType,
    ClosedLoopOutputType
)
from wpimath.geometry import Pose2d, Translation2d, Rotation2d
from wpimath.units import inchesToMeters
from subsystems.command_swerve_drivetrain import CommandSwerveDrivetrain

# Steer motor PID/FF gains
steer_gains = Slot0Configs().with_k_p(100).with_k_i(0).with_k_d(0.2).with_k_s(0).with_k_v(1.5).with_k_a(0)

# Drive motor PID/FF gains
drive_gains = Slot0Configs().with_k_p(3).with_k_i(0).with_k_d(0).with_k_s(0).with_k_v(0).with_k_a(0)

# Replace "Voltage" strings with enum values
steer_closed_loop_output = ClosedLoopOutputType.VOLTAGE
drive_closed_loop_output = ClosedLoopOutputType.VOLTAGE

# Replace "FUSED_CANCODER" string with enum value
feedback_source = SteerFeedbackType.FUSED_CANCODER

# Current limits
drive_initial_configs = TalonFXConfiguration()
steer_initial_configs = TalonFXConfiguration().with_current_limits(
    CurrentLimitsConfigs()
    .with_stator_current_limit(60)
    .with_stator_current_limit_enable(True)
)
encoder_initial_configs = CANcoderConfiguration()

# Pigeon2 configuration (if applicable, None otherwise)
pigeon_configs = Pigeon2Configuration()

# Robot constants
k_speed_at_12_volts_mps = 5.41
k_couple_ratio = 0
k_drive_gear_ratio = 5.9
k_steer_gear_ratio = 18.75
k_wheel_radius_inches = 2
k_invert_left_side = False
k_invert_right_side = True
k_can_bus_name = ""
k_pigeon_id = 14

# Simulation-specific constants
k_steer_inertia = 0.00001
k_drive_inertia = 0.001
k_steer_friction_voltage = 0.25
k_drive_friction_voltage = 0.25

# Swerve drivetrain constants
drivetrain_constants = (
    SwerveDrivetrainConstants()
    .with_can_bus_name(k_can_bus_name)
    .with_pigeon2_id(k_pigeon_id)
    .with_pigeon2_configs(pigeon_configs)
)

# Swerve module constants factory
constant_creator = (
    SwerveModuleConstantsFactory()
    .with_drive_motor_gear_ratio(k_drive_gear_ratio)
    .with_steer_motor_gear_ratio(k_steer_gear_ratio)
    .with_wheel_radius(k_wheel_radius_inches)
    .with_slip_current(150.0)
    .with_steer_motor_gains(steer_gains)
    .with_drive_motor_gains(drive_gains)
    .with_steer_motor_closed_loop_output(steer_closed_loop_output)
    .with_drive_motor_closed_loop_output(drive_closed_loop_output)
    .with_speed_at12_volts(k_speed_at_12_volts_mps)
    .with_steer_inertia(k_steer_inertia)
    .with_drive_inertia(k_drive_inertia)
    .with_steer_friction_voltage(k_steer_friction_voltage)
    .with_drive_friction_voltage(k_drive_friction_voltage)
    .with_feedback_source(feedback_source)
    .with_coupling_gear_ratio(k_couple_ratio)
    .with_drive_motor_initial_configs(drive_initial_configs)
    .with_steer_motor_initial_configs(steer_initial_configs)
    .with_encoder_initial_configs(encoder_initial_configs)
)

# Swerve module constants
front_left = constant_creator.create_module_constants(
    steer_motor_id=5,
    drive_motor_id=6,
    encoder_id=11,
    encoder_offset=-0.340576171875,
    location_x=inchesToMeters(10.41),
    location_y=inchesToMeters(10.41),
    drive_motor_inverted=k_invert_left_side,
    steer_motor_inverted=True,
    encoder_inverted=False,
)

front_right = constant_creator.create_module_constants(
    steer_motor_id=3,
    drive_motor_id=4,
    encoder_id=10,
    encoder_offset=-0.14794921875,
    location_x=inchesToMeters(10.41),
    location_y=inchesToMeters(-10.41),
    drive_motor_inverted=k_invert_right_side,
    steer_motor_inverted=True,
    encoder_inverted=False,
)

back_left = constant_creator.create_module_constants(
    steer_motor_id=7,
    drive_motor_id=8,
    encoder_id=12,
    encoder_offset=0.198974609375,
    location_x=inchesToMeters(-10.41),
    location_y=inchesToMeters(10.41),
    drive_motor_inverted=k_invert_left_side,
    steer_motor_inverted=True,
    encoder_inverted=False,
)

back_right = constant_creator.create_module_constants(
    steer_motor_id=1,
    drive_motor_id=2,
    encoder_id=9,
    encoder_offset=0.3583984375,
    location_x=inchesToMeters(-10.41),
    location_y=inchesToMeters(-10.41),
    drive_motor_inverted=k_invert_right_side,
    steer_motor_inverted=True,
    encoder_inverted=False,
)

# Drivetrain subsystem
DriveTrain = CommandSwerveDrivetrain(drivetrain_constants, front_left, front_right, back_left, back_right)
