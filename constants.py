# Dictionary mapping motor names to their IDs
MOTOR_IDS = {
    "elevator_right": 20,
    "elevator_left": 21,
    "wrist": 22,
    "shooter": 25,
    "climber": 26
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
    "hard_hold": -0.5,  # Safe position to move up and down
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
    "voltage_limit": 2,
    "hard_hold_kP": .2,  # Safe position to move up and down
}

CON_SHOOT = {
    "very_low": 2,
    "low": 2,
    "high": 5,
    "shoot_duration_long": 0.3,
    "shoot_duration": 0.3
}

CON_CLIMB = {
    "min": 0,
    "min_max_tolerance": 1,
    "safety_retreat": 1,
    "power_ratio": 1
}
