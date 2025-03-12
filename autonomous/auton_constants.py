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
        "drive1_timeout": 3.5,
    }
}

INSTRUCTIONS_A = {
    "blue_left": {
        "moves": "left",
        "shot1": 20,
        "intake": 13,
        "shot2": 19
    },
    "blue_right": {
        "moves": "right",
        "shot1": 22,
        "intake": 12,
        "shot2": 14
    },
    "red_left": {
        "moves": "left",
        "shot1": 11,
        "intake": 1,
        "shot2": 6
    },
    "red_right": {
        "moves": "right",
        "shot1": 9,
        "intake": 2,
        "shot2": 8
    },
    "blue_center": {
        "shot1": 0
    },
    "red_center": {
        "shot1": 0
    }
}

INSTRUCTIONS_MOVES = {
    "left": {
        "move1": {
            "speed_y": 2,
            "time": 20,
        },
        "move2": {
            "speed_x": 2,
            "speed_y": 1,
            "rotation": -2.5,
            "time": 20,
        },
    },
    "right": {
        "move1": {
            "speed_y": -2,
            "time": 20,
        },
        "move2": {
            "speed_x": 2,
            "speed_y": -1,
            "rotation": 2.5,
            "time": 20,
        },
    },
    "approach": {
        "in": {
            "speed_x": 0.6,
            "speed_y": 0,
            "rotation": 0,
            "time": 100,
            "sensor_stop_distance": 0.5
        },
        "out1": {
            "speed_x": -2,
            "speed_y": 0,
            "rotation": 0,
            "time": 20,
            "sensor_stop_distance": None
        },
        "out2": {
            "speed_x": 0,
            "speed_y": 0,
            "rotation": 3,
            "time": 20,
            "sensor_stop_distance": None
        },
    }
}

LL_DATA_SETTINGS = {
    "yaw": {
        "multiplier": 0.115
    },
    "tx": {
        "multiplier": 0.222
    },
    "distance": {}
}

DRIVING = {
    "speed_x": {
        "inverter": {
            "red": 1,
            "blue": -1
        },
        "max": 2,
        "multiplier": .5,
        "add_min": 0.5,
        "target_tolerance": 0.3,
        "target_tolerance_intake": 4,
        "reduce_when_close": {
            "distance": 1,
            "multiplier": 0.7,
            "max": 0.6
        },
        "no_spin_power": 0.5
    },
    "speed_y": {
        "inverter": {
            "red": -1,
            "blue": 1
        },
        "max": 1.5,
        "multiplier": 0.4,
        "add_min": 0,
        "target_tolerance": 0.5,
        "target_tolerance_intake": 0.2,
        "engage_at_distance": 99,
        "reduce_when_close": {
            "distance": 1.5,
            "multiplier": 0.3,
            "max": 0.55
        },
        "no_spin_power": 0.5
    },
    "rotation": {
        "inverter": {
            "red": -1,
            "blue": 1
        },
        "max": 0.8,
        "multiplier": 0.2,
        "add_min": 0.4,
        "target_tolerance": 0.08,
        "target_tolerance_intake": 0.04,
        "engage_at_distance": 99,
        "reduce_when_close": {
            "distance": 2,
            "multiplier": 1.5
        },
        "no_spin_power": 0.5
    }
}

CANRANGE = {
    "speed": 0.55,
    "right": {
        "target": 0.40,
        "bang": 0.45,
        "max_time": 20
    },
    "left": {
        "target": 0.48,
        "bang": 0.25,
        "max_time": 30
    }
}
