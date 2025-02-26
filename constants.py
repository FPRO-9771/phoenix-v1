# Dictionary mapping motor names to their IDs
MOTOR_IDS = {
    "elevator_right": 20,
    "elevator_left": 21,
    "wrist": 22,
    "shooter": 25,
    "climber": 26
}

ELEVATOR_ROTATIONS = {
    "intake": 5.2,
    "level_2": 22,
    "level_3": 56,
    "level_4": 113,
    "target_position_tolerance": 0.1,
    "min": 1,
    "max": 117,
    "min_max_tolerance": 0.5,
    "safety_retreat": 2,
    "voltage_limit": 6
}

ARM_ROTATIONS = {
    "min": 0,
    "max": 14,
    "move": 13,  # Safe position to move up and down
    "intake": 4.5,  # Angle for intake of coral
    "level_23": 8.6,  # Angle to deposit coral onto reef
    "level_4": 10,  # angle for highest level
    "flip": 8,  # angle for highest level
    "elevator_danger": 5.75,  # angle where we should not be moving the elevator
    "safety_retreat": 2
}

SHOOTER_STRENGTH = {
    "low": 2,
    "high": 3,
    "shoot_duration": 0.3
}

CLIMBER_ROTATIONS = {
     "down": .2,
     "lock": True,
     "unlock": False,
     "up": 6,
     "safety_retreat": 3
 }