import random
import time
from datetime import datetime, timezone

import requests


API_URL = "http://127.0.0.1:8000/telemetry"

PANEL_COUNT = 100
SEND_INTERVAL_SECONDS = 2


def generate_normal_telemetry(panel_number: int) -> dict:
    panel_id = f"LV-{panel_number:03d}"

    # Her panonun küçük farklılıkları olsun.
    base_current = 260 + ((panel_number * 7) % 60)
    base_cable_temp = 42 + ((panel_number * 3) % 5)
    base_ambient_temp = 29 + ((panel_number * 2) % 3)

    return {
        "panel_id": panel_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),

        "current_a": round(
            base_current + random.uniform(-15, 15),
            2
        ),

        "cable_temperature_c": round(
            base_cable_temp + random.uniform(-2, 2),
            2
        ),

        "ambient_temperature_c": round(
            base_ambient_temp + random.uniform(-1, 1),
            2
        ),

        "humidity_pct": round(
            random.uniform(38, 50),
            2
        ),

        "pd_index": round(
            random.uniform(7, 15),
            2
        ),

        "arc_detected": False,

        "data_quality": "GOOD"
    }


def send_all_panels(session: requests.Session) -> tuple[int, int]:
    success_count = 0
    error_count = 0

    for panel_number in range(1, PANEL_COUNT + 1):
        telemetry = generate_normal_telemetry(panel_number)

        try:
            response = session.post(
                API_URL,
                json=telemetry,
                timeout=5
            )

            if response.status_code == 200:
                success_count += 1
            else:
                error_count += 1

        except requests.RequestException:
            error_count += 1

    return success_count, error_count


def main():
    print("=" * 55)
    print("GRIDGUARD 100-PANEL SIMULATOR")
    print("=" * 55)
    print(f"Panels: {PANEL_COUNT}")
    print(f"Interval: {SEND_INTERVAL_SECONDS} seconds")
    print("Press CTRL+C to stop.")
    print()

    cycle = 1

    with requests.Session() as session:
        try:
            while True:
                started_at = time.perf_counter()

                success, errors = send_all_panels(session)

                elapsed = time.perf_counter() - started_at

                print(
                    f"[Cycle {cycle:03d}] "
                    f"Sent: {success}/{PANEL_COUNT} | "
                    f"Errors: {errors} | "
                    f"Time: {elapsed:.2f}s"
                )

                cycle += 1
                time.sleep(SEND_INTERVAL_SECONDS)

        except KeyboardInterrupt:
            print("\nGridGuard simulator stopped.")


if __name__ == "__main__":
    main()