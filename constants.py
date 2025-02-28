# Dictionary mapping motor names to their IDs
MOTOR_IDS = {
    "elevator_right": 20,
    "elevator_left": 21,
    "wrist": 22,
    "shooter": 25,
    "climber": 26
}

CON_ELEV = {
    "min": 1.7,
    "max": 116.5,
    "min_max_tolerance": 0.5,
    "intake": 11.47,
    "level_2": 22,
    "level_3": 56,
    "level_4": 117,
    "target_position_tolerance": 0.3,
    "safety_retreat": 1,
    "voltage_limit": 9
}

CON_ARM = {
    "min": 0,
    "max": 14,
    "min_max_tolerance": 0.5,
    "move": 13,  # Safe position to move up and down
    "intake": 4.5,  # Angle for intake of coral
    "level_1": 9,  # Angle to deposit coral onto reef
    "level_1_flip": 5,
    "level_23": 8.6,  # Angle to deposit coral onto reef
    "level_4": 9.3,  # angle for highest level, higher is steeper
    "flip": 8,  # angle for highest level
    "target_position_tolerance": 0.3,
    "elevator_danger": 5.75,  # angle where we should not be moving the elevator
    "safety_retreat": 2,
    "voltage_limit": 2
}

CON_SHOOT = {
    "very_low": 0.8,
    "low": 2,
    "high": 3,
    "shoot_duration_long": 1,
    "shoot_duration": 0.3
}

CON_CLIMB = {
     "down": .2,
     "lock": True,
     "unlock": False,
     "up": 6,
     "safety_retreat": 3
 }