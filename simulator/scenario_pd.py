import time
from datetime import datetime, timezone

import requests


PANEL_ID = "LV-041"

TELEMETRY_URL = "http://127.0.0.1:8000/telemetry"
RISK_URL = f"http://127.0.0.1:8000/panels/{PANEL_ID}/risk"


scenario_steps = [
    12,
    16,
    22,
    30,
    42,
    56,
    72
]


def send_telemetry(pd_index: float):
    payload = {
        "panel_id": PANEL_ID,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "current_a": 310.0,
        "cable_temperature_c": 45.0,
        "ambient_temperature_c": 30.0,
        "humidity_pct": 44.0,
        "pd_index": pd_index,
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
    print("GRIDGUARD - PARTIAL DISCHARGE DEGRADATION SCENARIO")
    print(f"Target panel: {PANEL_ID}")
    print("=" * 70)
    print()

    for step_number, pd_index in enumerate(
        scenario_steps,
        start=1
    ):
        send_telemetry(pd_index)

        time.sleep(0.3)

        risk = get_risk()

        print(
            f"[Step {step_number}] "
            f"PD Index: {pd_index} | "
            f"Current: 310 A | "
            f"Cable: 45 °C"
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
