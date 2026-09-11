from datetime import datetime, timezone

from fastapi import FastAPI

from backend.app.schemas import TelemetryData


app = FastAPI(
    title="GridGuard API",
    description="GridGuard Edge Monitoring and Early Warning System",
    version="0.1.0"
)


# Her panelin en son telemetry verisini geçici olarak RAM'de tutuyoruz.
latest_telemetry: dict[str, dict] = {}


@app.get("/")
def root():
    return {
        "service": "GridGuard API",
        "status": "running",
        "version": "0.1.0"
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "connected_panels": len(latest_telemetry)
    }


@app.post("/telemetry")
def receive_telemetry(data: TelemetryData):
    received_at = datetime.now(timezone.utc)

    latest_telemetry[data.panel_id] = {
        "telemetry": data.model_dump(),
        "received_at": received_at
    }

    return {
        "status": "accepted",
        "received_at": received_at,
        "telemetry": data
    }


@app.get("/panels")
def get_panels():
    return {
        "count": len(latest_telemetry),
        "panels": latest_telemetry
    }