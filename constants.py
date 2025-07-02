# Shooter type selection - switch between "Competition" and "Parade"
SHOOTER_TYPE = "Parade"  # Change to "Competition" to use original shooter

# Dictionary mapping motor names to their IDs
MOTOR_IDS = {
    "elevator_right": 20,
    "elevator_left": 21,
    "wrist": 22,
    "shooter": 25,
    "climber": 26,
    "shooter_parade_left": 27,
    "shooter_parade_right": 28
}

CON_ELEV = {
    "min": 1,
    "max": 115,
    "min_max_tolerance": 0.3,
    "intake": 1.5,
    "level_2": 15,
    "level_3": 55,
    "level_4": 114,
    "target_position_tolerance": 0.3,
    "safety_retreat": 1,
    "voltage_limit": 11
}

CON_ARM = {
    "min": 2.1,
    "max": 14,
    "min_max_tolerance": 0,
    "move": 2.1,  # Safe position to move up and down
    "intake": 4.9,  # Angle for intake of coral
    "level_1": 9,  # Angle to deposit coral onto reef
    "level_1_flip": 9,
    "level_23": 8.6,  # Angle to deposit coral onto reef
    "level_4": 9.5,  # angle for highest level, higher is steeper
    "flip": 8,  # angle for highest level
    "target_position_tolerance": 0.3,
    "elevator_danger": 5.75,  # angle where we should not be moving the elevator
    "safety_retreat": 0.5,
    "voltage_limit": 2
}

CON_SHOOT = {
    "very_low": 2,
    "low": 2,
    "high": 5,
    "shoot_duration_long": 0.3,
    "shoot_duration": 0.3
}

CON_SHOOT_PARADE = {
    "low_rpm": 500,        # Low RPM for pull-back (negative direction) - UNUSED
    "max_rpm": 4000,       # Maximum RPM for firing - UNUSED
    "pullback_voltage": 3.0, # Low voltage for slow pull-back (direct voltage control)
    "fire_voltage": 12.0,  # Maximum voltage for fast firing (direct voltage control)
    "fire_duration": 0.5   # Fire duration in seconds (adjustable)
}

CON_CLIMB = {
    "min": 0,
    "min_max_tolerance": 1,
    "safety_retreat": 1,
    "power_ratio": 1
}

# Robot container configuration
CON_ROBOT = {
    # Speed and rotation settings
    "max_angular_rate_rotations": 0.75,  # 3/4 rotation per second max angular velocity
    "deadband_percent": 0.1,              # 10% deadband for drive and rotation
    "slow_mode_ratio": 0.1,               # Speed when in slow mode
    "rotation_multiplier": 1.5,           # Rotation ratio multiplier
    
    # Initial speed ratios by mode
    "parade_initial_speed": 0.3,          # Start slow for parades
    "competition_initial_speed": 1.0,     # Start full speed for competition
    
    # Controller ports
    "driver_controller_port": 0,
    "operator_controller_port": 1,
    
    # Subsystem initialization values
    "elevator_max_height": 1000,
    "arm_max_angle": 300,
    
    # Control thresholds
    "joystick_deadband": 0.1,            # Ignore joystick inputs below this
    "trigger_threshold": 0.05,           # Trigger activation threshold
    
    # Manual control speeds
    "climber_manual_up": 0.25,
    "climber_manual_down": -0.25
}
