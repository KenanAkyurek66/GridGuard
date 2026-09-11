import time
from datetime import datetime, timezone

import requests


PANEL_ID = "LV-042"

TELEMETRY_URL = "http://127.0.0.1:8000/telemetry"
RISK_URL = f"http://127.0.0.1:8000/panels/{PANEL_ID}/risk"


scenario_steps = [
    False,
    False,
    False,
    True
]


def send_telemetry(arc_detected: bool):
    payload = {
        "panel_id": PANEL_ID,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "current_a": 315.0,
        "cable_temperature_c": 46.0,
        "ambient_temperature_c": 31.0,
        "humidity_pct": 44.0,
        "pd_index": 13.0,
        "arc_detected": arc_detected,
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
    print("GRIDGUARD - ARC FLASH SCENARIO")
    print(f"Target panel: {PANEL_ID}")
    print("=" * 70)
    print()

    for step_number, arc_detected in enumerate(
        scenario_steps,
        start=1
    ):
        send_telemetry(arc_detected)

        time.sleep(0.3)

        risk = get_risk()

        print(
            f"[Step {step_number}] "
            f"ARC: {arc_detected} | "
            f"Current: 315 A | "
            f"Cable: 46 °C"
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