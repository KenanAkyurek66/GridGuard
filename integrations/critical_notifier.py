import os
import time
from datetime import datetime, timezone
from typing import Any

import requests


GRIDGUARD_API_URL = (
    "http://127.0.0.1:8000/alarms"
)

WEBHOOK_URL = os.getenv(
    "GRIDGUARD_WEBHOOK_URL",
    "http://127.0.0.1:9001/notify",
)

POLL_INTERVAL_SECONDS = 2


AlarmState = tuple[
    str,
    str,
    float,
]


known_alarm_states: dict[
    int,
    AlarmState,
] = {}


def fetch_alarms() -> list[dict[str, Any]]:
    response = requests.get(
        GRIDGUARD_API_URL,
        timeout=5,
    )

    response.raise_for_status()

    data = response.json()

    return data.get(
        "alarms",
        [],
    )


def get_alarm_state(
    alarm: dict[str, Any],
) -> AlarmState:
    return (
        alarm.get(
            "status",
            "UNKNOWN",
        ),
        alarm.get(
            "severity",
            "UNKNOWN",
        ),
        float(
            alarm.get(
                "risk_score",
                0,
            )
            or 0
        ),
    )


def build_notification(
    event: str,
    alarm: dict[str, Any],
) -> dict[str, Any]:
    return {
        "event": event,
        "panel_id": alarm.get(
            "panel_id",
            "UNKNOWN",
        ),
        "alarm_id": alarm["id"],
        "severity": alarm.get(
            "severity",
            "UNKNOWN",
        ),
        "risk_score": float(
            alarm.get(
                "risk_score",
                0,
            )
            or 0
        ),
        "primary_risk": alarm.get(
            "primary_risk",
            "NONE",
        ),
        "message": alarm.get(
            "message"
        ),
        "alarm_status": alarm.get(
            "status",
            "UNKNOWN",
        ),
        "timestamp": (
            datetime.now(
                timezone.utc
            ).isoformat()
        ),
    }


def send_notification(
    payload: dict[str, Any],
) -> bool:
    try:
        response = requests.post(
            WEBHOOK_URL,
            json=payload,
            timeout=5,
        )

        response.raise_for_status()

    except requests.RequestException as exc:
        print()
        print("[WEBHOOK ERROR]")
        print(exc)

        return False

    print()
    print("[NOTIFICATION SENT]")

    print(
        f"Event      : "
        f"{payload['event']}"
    )

    print(
        f"Panel      : "
        f"{payload['panel_id']}"
    )

    print(
        f"Severity   : "
        f"{payload['severity']}"
    )

    print(
        f"Risk Score : "
        f"{payload['risk_score']}"
    )

    return True


def bootstrap() -> None:
    alarms = fetch_alarms()

    for alarm in alarms:
        alarm_id = alarm.get("id")

        if alarm_id is None:
            continue

        known_alarm_states[
            alarm_id
        ] = get_alarm_state(
            alarm
        )

    print(
        f"[BASELINE LOADED] "
        f"{len(known_alarm_states)} "
        f"existing alarms."
    )


def process_alarm(
    alarm: dict[str, Any],
) -> None:
    alarm_id = alarm.get("id")

    if alarm_id is None:
        return

    current_state = (
        get_alarm_state(
            alarm
        )
    )

    current_status = (
        current_state[0]
    )

    current_severity = (
        current_state[1]
    )

    previous_state = (
        known_alarm_states.get(
            alarm_id
        )
    )

    if previous_state is None:
        if (
            current_status == "OPEN"
            and
            current_severity
            == "CRITICAL"
        ):
            payload = (
                build_notification(
                    "CRITICAL_OPEN",
                    alarm,
                )
            )

            send_notification(
                payload
            )

        known_alarm_states[
            alarm_id
        ] = current_state

        return

    previous_status = (
        previous_state[0]
    )

    previous_severity = (
        previous_state[1]
    )

    became_critical = (
        current_status == "OPEN"
        and
        current_severity == "CRITICAL"
        and
        (
            previous_status
            != "OPEN"
            or
            previous_severity
            != "CRITICAL"
        )
    )

    critical_resolved = (
        current_status == "RESOLVED"
        and
        previous_status == "OPEN"
        and
        previous_severity
        == "CRITICAL"
    )

    if became_critical:
        payload = build_notification(
            "CRITICAL_OPEN",
            alarm,
        )

        send_notification(
            payload
        )

    elif critical_resolved:
        payload = build_notification(
            "CRITICAL_RESOLVED",
            alarm,
        )

        send_notification(
            payload
        )

    known_alarm_states[
        alarm_id
    ] = current_state


def run_monitor() -> None:
    print()
    print("=" * 72)
    print(
        " GridGuard Critical Alarm Notifier"
    )
    print("=" * 72)

    print(
        f"GridGuard API : "
        f"{GRIDGUARD_API_URL}"
    )

    print(
        f"Webhook       : "
        f"{WEBHOOK_URL}"
    )

    print(
        f"Poll interval : "
        f"{POLL_INTERVAL_SECONDS}s"
    )

    print("=" * 72)
    print()

    try:
        bootstrap()

    except requests.RequestException as exc:
        print("[STARTUP ERROR]")
        print(
            "Could not reach GridGuard API."
        )
        print(exc)

        return

    print()
    print(
        "[NOTIFIER READY] "
        "Watching for critical alarms..."
    )

    try:
        while True:
            try:
                alarms = fetch_alarms()

                for alarm in alarms:
                    process_alarm(
                        alarm
                    )

            except requests.RequestException as exc:
                print()
                print("[GRIDGUARD API ERROR]")
                print(exc)

            time.sleep(
                POLL_INTERVAL_SECONDS
            )

    except KeyboardInterrupt:
        print()
        print(
            "GridGuard notifier stopped."
        )


if __name__ == "__main__":
    run_monitor()