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
    "speed": {
        "v_max": 12,
        "v_min": 2,
        "cp_to_acceleration_ratio": 1.3,
        "v_calc_to_limit_ratio": 1
    }
}

CON_ARM = {
    "min": 2.1,
    "max": 14,
    "min_max_tolerance": 0,
    "hard_hold": 0,
    "move": 2.1,  # Safe position to move up and down
    "intake": 4.9,  # Angle for intake of coral
    "level_1": 9,  # Angle to deposit coral onto reef
    "level_1_flip": 9,
    "level_23": 8.8,  # Angle to deposit coral onto reef
    "level_4": 9.8,  # angle for highest level, higher is steeper
    "flip": 8,  # angle for highest level
    "target_position_tolerance": 0.3,
    "elevator_danger": 5.75,  # angle where we should not be moving the elevator
    "safety_retreat": 0.5,
    "hard_hold_v": .2,
    "speed": {
        "v_max": 12,
        "v_min": 2,
        "cp_to_acceleration_ratio": 1.2,
        "v_calc_to_limit_ratio": 0.5
    },
    "lock": {
        "open": 0,
        "closed": 0,
        "time_delay": 0
    }
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
