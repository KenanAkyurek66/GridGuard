import random
import time
from datetime import datetime, timezone

import requests


API_URL = "http://127.0.0.1:8000/telemetry"
PANEL_ID = "LV-001"


def generate_normal_telemetry():
    return {
        "panel_id": PANEL_ID,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "current_a": round(random.uniform(280, 340), 2),
        "cable_temperature_c": round(random.uniform(41, 47), 2),
        "ambient_temperature_c": round(random.uniform(29, 32), 2),
        "humidity_pct": round(random.uniform(38, 48), 2),
        "pd_index": round(random.uniform(8, 15), 2),
        "arc_detected": False,
        "data_quality": "GOOD"
    }


def send_telemetry():
    telemetry = generate_normal_telemetry()

    try:
        response = requests.post(
            API_URL,
            json=telemetry,
            timeout=5
        )

        if response.status_code == 200:
            print(
                f"[OK] {PANEL_ID} | "
                f"Current: {telemetry['current_a']} A | "
                f"Cable: {telemetry['cable_temperature_c']} °C | "
                f"Ambient: {telemetry['ambient_temperature_c']} °C | "
                f"Humidity: {telemetry['humidity_pct']} % | "
                f"PD: {telemetry['pd_index']}"
            )
        else:
            print(
                f"[ERROR] Backend returned "
                f"{response.status_code}: {response.text}"
            )

    except requests.RequestException as error:
        print(f"[CONNECTION ERROR] {error}")


def main():
    print(f"GridGuard simulator started for {PANEL_ID}")
    print("Press CTRL+C to stop.\n")

    try:
        while True:
            send_telemetry()
            time.sleep(1)

    except KeyboardInterrupt:
        print("\nSimulator stopped.")


if __name__ == "__main__":
    main()