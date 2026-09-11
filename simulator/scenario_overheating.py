import time
from datetime import datetime, timezone

import requests


PANEL_ID = "LV-050"

TELEMETRY_URL = "http://127.0.0.1:8000/telemetry"
RISK_URL = f"http://127.0.0.1:8000/panels/{PANEL_ID}/risk"


scenario_steps = [
    {
        "current_a": 320,
        "cable_temperature_c": 45,
        "ambient_temperature_c": 31
    },
    {
        "current_a": 340,
        "cable_temperature_c": 48,
        "ambient_temperature_c": 31
    },
    {
        "current_a": 370,
        "cable_temperature_c": 54,
        "ambient_temperature_c": 31
    },
    {
        "current_a": 400,
        "cable_temperature_c": 60,
        "ambient_temperature_c": 31
    },
    {
        "current_a": 435,
        "cable_temperature_c": 68,
        "ambient_temperature_c": 31
    },
    {
        "current_a": 470,
        "cable_temperature_c": 76,
        "ambient_temperature_c": 31
    },
    {
        "current_a": 500,
        "cable_temperature_c": 82,
        "ambient_temperature_c": 32
    }
]


def send_telemetry(step: dict):
    payload = {
        "panel_id": PANEL_ID,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "current_a": step["current_a"],
        "cable_temperature_c": step["cable_temperature_c"],
        "ambient_temperature_c": step["ambient_temperature_c"],
        "humidity_pct": 44.0,
        "pd_index": 12.0,
        "arc_detected": False,
        "data_quality": "GOOD"
    }

    response = requests.post(
        TELEMETRY_URL,
        json=payload,
        timeout=5
    )

    response.raise_for_status()


def get_risk():
    response = requests.get(
        RISK_URL,
        timeout=5
    )

    response.raise_for_status()

    return response.json()


def main():
    print("=" * 70)
    print("GRIDGUARD - LOCAL OVERHEATING SCENARIO")
    print(f"Target panel: {PANEL_ID}")
    print("=" * 70)
    print()

    for step_number, step in enumerate(
        scenario_steps,
        start=1
    ):
        send_telemetry(step)

        time.sleep(0.3)

        risk = get_risk()

        print(
            f"[Step {step_number}] "
            f"Current: {step['current_a']} A | "
            f"Cable: {step['cable_temperature_c']} °C | "
            f"Ambient: {step['ambient_temperature_c']} °C"
        )

        print(
            f"         Risk: {risk['risk_score']}/100 | "
            f"Status: {risk['status']} | "
            f"Primary: {risk['primary_risk']}"
        )

        print()

        time.sleep(1.5)

    print("=" * 70)
    print("Scenario completed.")
    print("=" * 70)


if __name__ == "__main__":
    main()