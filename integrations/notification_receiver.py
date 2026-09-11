from datetime import datetime, timezone
from typing import Any

import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel


HOST = "127.0.0.1"
PORT = 9001


app = FastAPI(
    title="GridGuard Demo Notification Receiver",
    version="1.0.0",
)


notifications: list[dict[str, Any]] = []


class NotificationPayload(BaseModel):
    event: str
    panel_id: str
    alarm_id: int
    severity: str
    risk_score: float
    primary_risk: str
    message: str | None = None
    alarm_status: str
    timestamp: str


@app.get("/")
def root() -> dict[str, str]:
    return {
        "service": "GridGuard Notification Receiver",
        "status": "online",
    }


@app.get("/notifications")
def get_notifications() -> dict[str, Any]:
    return {
        "count": len(notifications),
        "notifications": notifications,
    }


@app.delete("/notifications")
def clear_notifications() -> dict[str, Any]:
    notifications.clear()

    return {
        "message": "Notifications cleared.",
        "count": 0,
    }


@app.post("/notify")
def receive_notification(
    payload: NotificationPayload,
) -> dict[str, Any]:
    notification = payload.model_dump()

    notification["received_at"] = (
        datetime.now(timezone.utc).isoformat()
    )

    notifications.append(notification)

    print()
    print("=" * 72)
    print(" GRIDGUARD EXTERNAL NOTIFICATION")
    print("=" * 72)

    print(f"Event        : {payload.event}")
    print(f"Panel        : {payload.panel_id}")
    print(f"Alarm ID     : {payload.alarm_id}")
    print(f"Status       : {payload.alarm_status}")
    print(f"Severity     : {payload.severity}")
    print(f"Risk Score   : {payload.risk_score}")
    print(f"Primary Risk : {payload.primary_risk}")

    if payload.message:
        print(f"Message      : {payload.message}")

    print("=" * 72)
    print()

    return {
        "accepted": True,
        "notification_count": len(notifications),
    }


def main() -> None:
    print()
    print("=" * 72)
    print(" GridGuard Demo Webhook Receiver")
    print("=" * 72)

    print(
        f"Webhook endpoint : "
        f"http://{HOST}:{PORT}/notify"
    )

    print(
        f"Notification log : "
        f"http://{HOST}:{PORT}/notifications"
    )

    print()
    print(
        "Waiting for GridGuard critical alerts..."
    )

    print("=" * 72)
    print()

    uvicorn.run(
        app,
        host=HOST,
        port=PORT,
        log_level="warning",
    )


if __name__ == "__main__":
    main()