from __future__ import annotations

import time
from datetime import datetime, timezone

import requests


API_BASE = "http://127.0.0.1:8000"
PANEL_ID = "LV-050"

# Dashboard currently refreshes periodically.
# Eight seconds gives enough time to observe every state visually.
OBSERVATION_SECONDS = 8

STEPS = [
    {
        "current_a": 320.0,
        "cable_temperature_c": 45.0,
        "ambient_temperature_c": 31.0,
    },
    {
        "current_a": 340.0,
        "cable_temperature_c": 48.0,
        "ambient_temperature_c": 31.0,
    },
    {
        "current_a": 370.0,
        "cable_temperature_c": 54.0,
        "ambient_temperature_c": 31.0,
    },
    {
        "current_a": 400.0,
        "cable_temperature_c": 60.0,
        "ambient_temperature_c": 31.0,
    },
    {
        "current_a": 435.0,
        "cable_temperature_c": 68.0,
        "ambient_temperature_c": 31.0,
    },
    {
        "current_a": 470.0,
        "cable_temperature_c": 76.0,
        "ambient_temperature_c": 31.0,
    },
    {
        "current_a": 500.0,
        "cable_temperature_c": 82.0,
        "ambient_temperature_c": 32.0,
    },
]


def post_telemetry(step: dict) -> None:
    payload = {
        "panel_id": PANEL_ID,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "current_a": step["current_a"],
        "cable_temperature_c": step["cable_temperature_c"],
        "ambient_temperature_c": step["ambient_temperature_c"],
        "humidity_pct": 44.0,
        "pd_index": 12.0,
        "arc_detected": False,
        "data_quality": "GOOD",
    }

    response = requests.post(
        f"{API_BASE}/telemetry",
        json=payload,
        timeout=10,
    )
    response.raise_for_status()


def get_rule_risk() -> dict:
    response = requests.get(
        f"{API_BASE}/panels/{PANEL_ID}/risk",
        timeout=10,
    )
    response.raise_for_status()

    result = response.json()

    if isinstance(result.get("risk"), dict):
        result = result["risk"]

    return result


def get_intelligence() -> dict:
    response = requests.get(
        f"{API_BASE}/panels/{PANEL_ID}/intelligence",
        timeout=10,
    )
    response.raise_for_status()

    return response.json()


def countdown(seconds: int) -> None:
    print()
    print("Observe the LV-050 GridGuard Intelligence panel now.")

    for remaining in range(seconds, 0, -1):
        print(
            f"\rNext telemetry sample in {remaining:2d} seconds...",
            end="",
            flush=True,
        )
        time.sleep(1)

    print("\r" + " " * 50 + "\r", end="")


def main() -> None:
    print("=" * 88)
    print("GRIDGUARD - SLOW LIVE AI OVERHEATING DEMO")
    print("=" * 88)
    print(f"Target panel        : {PANEL_ID}")
    print(f"Observation period  : {OBSERVATION_SECONDS} seconds per step")
    print()
    print("Keep the LV-050 panel drawer open in the React dashboard.")
    print("=" * 88)

    input("\nPress ENTER when the dashboard is ready...")

    for index, step in enumerate(STEPS, start=1):
        post_telemetry(step)

        # Give FastAPI enough time to persist the new telemetry
        # and calculate the latest intelligence response.
        time.sleep(0.5)

        risk = get_rule_risk()
        intelligence = get_intelligence()

        predictive = intelligence["predictive"]
        anomaly = intelligence["anomaly"]
        consensus = intelligence["consensus"]

        rule_status = str(
            risk.get("status", "UNKNOWN")
        ).upper()

        rule_score = risk.get(
            "risk_score",
            "UNKNOWN",
        )

        primary_risk = risk.get(
            "primary_risk",
            "UNKNOWN",
        )

        print()
        print("-" * 88)
        print(f"STEP {index} / {len(STEPS)}")
        print("-" * 88)

        print(
            f"Current / Cable Temp : "
            f"{step['current_a']:.1f} A / "
            f"{step['cable_temperature_c']:.1f} °C"
        )

        print(
            f"Ambient Temperature  : "
            f"{step['ambient_temperature_c']:.1f} °C"
        )

        print()

        print(
            f"Rule Engine           : "
            f"{rule_status} ({rule_score}/100)"
        )

        print(
            f"Primary Risk          : "
            f"{primary_risk}"
        )

        print()

        print(
            f"Predictive AI         : "
            f"{predictive['decision']} "
            f"({predictive['probability_pct']}%)"
        )

        print(
            f"Prediction Horizon    : "
            f"{predictive.get('prediction_horizon_cycles', 5)} "
            f"telemetry cycles"
        )

        print(
            f"Anomaly Detector      : "
            f"{anomaly['level']}"
        )

        print()

        print(
            f"Consensus             : "
            f"{consensus['status']}"
        )

        print(
            f"Confidence            : "
            f"{consensus['confidence']}"
        )

        print(
            f"Agreement             : "
            f"{consensus['agreement_text']}"
        )

        if index < len(STEPS):
            countdown(OBSERVATION_SECONDS)

    print()
    print("=" * 88)
    print("DEMO COMPLETE")
    print("=" * 88)

    print(
        "The panel should now be at the final CRITICAL "
        "thermal condition."
    )

    print()
    print(
        "Run the recovery scenario after observation:"
    )

    print(
        "python simulator\\scenario_recovery.py"
    )

    print("=" * 88)


if __name__ == "__main__":
    main()