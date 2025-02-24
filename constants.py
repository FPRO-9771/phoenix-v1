# Dictionary mapping motor names to their IDs
MOTOR_IDS = {
    "elevator_right": 20,
    "elevator_left": 21,
    "wrist": 22,
    "shooter": 25,
    "climber": "unsure"
}

ELEVATOR_ROTATIONS = {
    "intake": 5.2,
    "level_2": 21,
    "level_3": 57,
    "level_4": 110,
    "min": 1,
    "max": 111,
    "safety_retreat": 2
}

ARM_ROTATIONS = {
    "min": 0,
    "max": 14,
    "move": 13,  # Safe position to move up and down
    "intake": 4.5,  # Angle for intake of coral
    "level_23": 8.6,  # Angle to deposit coral onto reef
    "level_4": 7.6,  # angle for highest level
    "flip": 6,  # angle for highest level
    "elevator_danger": 5.75,  # angle where we should not be moving the elevator
    "safety_retreat": 3
}

SHOOTER_STRENGTH = {
    "low": 2,
    "high": 3
}

#thes are the calls I imagine we are going to need
CLIMBER_ARM = {

    "down": .2,
    #Lock should be used to turn on the servo 'locking' the arm in place
    "lock": True,
    "unlock": False,
    "up": 6,
    "safery_retreat": 3
}
