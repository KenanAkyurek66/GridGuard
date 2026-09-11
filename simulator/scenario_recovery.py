import time
from datetime import datetime, timezone

import requests


PANEL_ID = "LV-050"

TELEMETRY_URL = "http://127.0.0.1:8000/telemetry"
RISK_URL = f"http://127.0.0.1:8000/panels/{PANEL_ID}/risk"


normal_steps = [
    {
        "current_a": 315.0,
        "cable_temperature_c": 46.0,
        "ambient_temperature_c": 31.0,
    },
    {
        "current_a": 305.0,
        "cable_temperature_c": 45.0,
        "ambient_temperature_c": 31.0,
    },
    {
        "current_a": 300.0,
        "cable_temperature_c": 44.0,
        "ambient_temperature_c": 30.0,
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

    return response.json()


def get_risk():
    response = requests.get(
        RISK_URL,
        timeout=5
    )

    response.raise_for_status()

    return response.json()


def main():
    print("=" * 70)
    print("GRIDGUARD - RECOVERY SCENARIO")
    print(f"Target panel: {PANEL_ID}")
    print("=" * 70)
    print()

    for step_number, step in enumerate(
        normal_steps,
        start=1
    ):
        result = send_telemetry(step)

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
            f"Alarm action: {result.get('alarm')}"
        )

        print()

        time.sleep(1)

    print("=" * 70)
    print("Recovery scenario completed.")
    print("=" * 70)


if __name__ == "__main__":
    main()