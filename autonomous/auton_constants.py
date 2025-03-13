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
        "shot2": 17
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
        "moves": "center",
        "shot1": 21
    },
    "red_center": {
        "moves": "center",
        "shot1": 10
    }
}

INSTRUCTIONS_MOVES = {
    "center": {
        "move0": {
            "speed_y": 0,
            "speed_x": 2,
            "rotation": 0,
            "time": 25,
        }
    },
    "left": {
        "move0": {
            "speed_y": 0,
            "speed_x": 2,
            "rotation": 3,
            "time": 25,
        },
        "move1": {
            "speed_y": -3,
            "speed_x": 0,
            "rotation": 0,
            "time": 25,
        },
        "move2": {
            "speed_x": 3,
            "speed_y": 0,
            "rotation": -4,
            "time": 30,
        },
    },
    "right": {
        "move0": {
            "speed_y": 0,
            "speed_x": 2,
            "rotation": 3,
            "time": 25,
        },
        "move1": {
            "speed_y": 3,
            "speed_x": 0,
            "rotation": 0,
            "time": 25,
        },
        "move2": {
            "speed_x": -3,
            "speed_y": 0,
            "rotation": 4,
            "time": 30,
        },
    },
    "approach": {
        "in": {
            "speed_x": 2,
            "speed_y": 0,
            "rotation": 0,
            "time": 40,
            "sensor_stop_distance": None
        },
        "in3": {
            "speed_x": .8,
            "speed_y": 0,
            "rotation": 0,
            "time": 60,
            "sensor_stop_distance": None
        },
        "out1": {
            "speed_x": -2,
            "speed_y": -1.5,
            "rotation": 0,
            "time": 30,
            "sensor_stop_distance": None
        },
        "out2": {
            "speed_x": 0,
            "speed_y": 0,
            "rotation": -8,
            "time": 25,
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
        "max": 3,
        "multiplier": .5,
        "add_min": 0.5,
        "target_tolerance": 0.3,
        "target_tolerance_intake": 3,
        "reduce_when_close": {
            "distance": 1.2,
            "multiplier": 0.6,
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
            "multiplier": .7
        },
        "no_spin_power": 0.5
    }
}

CANRANGE = {
    "speed": 0.55,
    "right": {
        "target": 0.45,
        "bang": 0.35,
        "max_time": 22
    },
    "left": {
        "target": 0.49,
        "bang": 0.25,
        "max_time": 22
    }
}
