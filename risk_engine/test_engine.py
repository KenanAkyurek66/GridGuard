from risk_engine.engine import evaluate_risk


normal_history = [
    {
        "current_a": 300,
        "cable_temperature_c": 44,
        "ambient_temperature_c": 30,
        "humidity_pct": 43,
        "pd_index": 11,
        "arc_detected": False
    },
    {
        "current_a": 305,
        "cable_temperature_c": 45,
        "ambient_temperature_c": 30,
        "humidity_pct": 44,
        "pd_index": 12,
        "arc_detected": False
    },
    {
        "current_a": 298,
        "cable_temperature_c": 44,
        "ambient_temperature_c": 31,
        "humidity_pct": 42,
        "pd_index": 10,
        "arc_detected": False
    }
]


overheating_history = [
    {
        "current_a": 300,
        "cable_temperature_c": 44,
        "ambient_temperature_c": 30,
        "humidity_pct": 43,
        "pd_index": 12,
        "arc_detected": False
    },
    {
        "current_a": 320,
        "cable_temperature_c": 48,
        "ambient_temperature_c": 30,
        "humidity_pct": 43,
        "pd_index": 13,
        "arc_detected": False
    },
    {
        "current_a": 350,
        "cable_temperature_c": 54,
        "ambient_temperature_c": 31,
        "humidity_pct": 44,
        "pd_index": 14,
        "arc_detected": False
    },
    {
        "current_a": 400,
        "cable_temperature_c": 63,
        "ambient_temperature_c": 31,
        "humidity_pct": 44,
        "pd_index": 15,
        "arc_detected": False
    },
    {
        "current_a": 470,
        "cable_temperature_c": 76,
        "ambient_temperature_c": 31,
        "humidity_pct": 45,
        "pd_index": 17,
        "arc_detected": False
    }
]


pd_degradation_history = [
    {
        "current_a": 310,
        "cable_temperature_c": 45,
        "ambient_temperature_c": 30,
        "humidity_pct": 44,
        "pd_index": 12,
        "arc_detected": False
    },
    {
        "current_a": 312,
        "cable_temperature_c": 45,
        "ambient_temperature_c": 30,
        "humidity_pct": 44,
        "pd_index": 19,
        "arc_detected": False
    },
    {
        "current_a": 308,
        "cable_temperature_c": 46,
        "ambient_temperature_c": 30,
        "humidity_pct": 45,
        "pd_index": 28,
        "arc_detected": False
    },
    {
        "current_a": 311,
        "cable_temperature_c": 45,
        "ambient_temperature_c": 31,
        "humidity_pct": 44,
        "pd_index": 42,
        "arc_detected": False
    },
    {
        "current_a": 314,
        "cable_temperature_c": 46,
        "ambient_temperature_c": 31,
        "humidity_pct": 45,
        "pd_index": 61,
        "arc_detected": False
    }
]


arc_history = [
    {
        "current_a": 320,
        "cable_temperature_c": 46,
        "ambient_temperature_c": 31,
        "humidity_pct": 44,
        "pd_index": 13,
        "arc_detected": True
    }
]


print("\n--- NORMAL ---")
print(evaluate_risk(normal_history))

print("\n--- OVERHEATING ---")
print(evaluate_risk(overheating_history))

print("\n--- PD DEGRADATION ---")
print(evaluate_risk(pd_degradation_history))

print("\n--- ARC FLASH ---")
print(evaluate_risk(arc_history))