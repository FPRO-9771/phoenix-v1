GENERAL = {
    "drive_speed": 20
}

INSTRUCTIONS = {
    "shoot_sides": {
        "drive1_v_x": {
            "red": -0.7,
            "blue": 0.7,
        },
        "drive1_timeout": 8
    },
    "shoot_center": {
        "drive1_v_x": {
            "red": -0.7,
            "blue": 0.7,
        },
        "drive1_timeout": 5.5,
        "drive2_v_y": -0.85,
        "drive2_timeout": 0.5,
    },
    "leave": {
        "drive1_v_x": {
            "red": -0.7,
            "blue": 0.7,
        },
        "drive1_timeout":3.5,
    }
}

DRIVING = {
    "speed_x": {
        "inverter": {
            "red": 1,
            "blue": -1
        },
        "multiplier": 0.4,
        "add_min": 0.35,
        "max": 3,
        "tolerance": 0.25
    },
    "speed_y": {
        "inverter": {
            "red": -1,
            "blue": 1
        },
        "multiplier": 1,
        "add_min": 0.3,
        "tolerance": 0.04
    },
    "rotation": {
        "inverter": {
            "red": -1,
            "blue": 1
        },
        "multiplier": 0.005,
        "add_min": 0.45,
        "tolerance": 0.5,
        "engage_at_distance": 99
    }
}