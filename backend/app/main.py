from datetime import datetime, timezone

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

from backend.app.database import Base, engine, get_db
from backend.app.models import (
    Alarm,
    Panel,
    RiskAssessment,
    Telemetry,
)
from backend.app.schemas import TelemetryData
from risk_engine.engine import evaluate_risk


Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="GridGuard API",
    description="GridGuard Edge Monitoring and Early Warning System",
    version="0.5.0"
)


def build_history(
    db: Session,
    panel_id: str,
    limit: int = 20
) -> list[dict]:
    records = (
        db.query(Telemetry)
        .filter(Telemetry.panel_id == panel_id)
        .order_by(Telemetry.timestamp.desc())
        .limit(limit)
        .all()
    )

    # Database gives newest -> oldest.
    # Risk Engine expects oldest -> newest.
    records.reverse()

    history = [
        {
            "current_a": record.current_a,
            "cable_temperature_c": record.cable_temperature_c,
            "ambient_temperature_c": record.ambient_temperature_c,
            "humidity_pct": record.humidity_pct,
            "pd_index": record.pd_index,
            "arc_detected": record.arc_detected
        }
        for record in records
    ]

    return history


def sync_alarm(
    db: Session,
    panel_id: str,
    risk_result: dict,
    timestamp: datetime
) -> dict | None:

    abnormal_statuses = {
        "WARNING",
        "HIGH",
        "CRITICAL"
    }

    open_alarm = (
        db.query(Alarm)
        .filter(
            Alarm.panel_id == panel_id,
            Alarm.status == "OPEN"
        )
        .order_by(Alarm.opened_at.desc())
        .first()
    )

    # NORMAL -> resolve an existing open alarm.
    if risk_result["status"] == "NORMAL":
        if open_alarm is not None:
            open_alarm.status = "RESOLVED"
            open_alarm.resolved_at = timestamp
            open_alarm.last_seen_at = timestamp

            db.commit()

            return {
                "action": "RESOLVED",
                "alarm_id": open_alarm.id
            }

        return None

    # WARNING / HIGH / CRITICAL
    if risk_result["status"] in abnormal_statuses:

        message = (
            risk_result["causes"][0]
            if risk_result["causes"]
            else "GridGuard anomaly detected."
        )

        # No alarm yet -> open one.
        if open_alarm is None:
            new_alarm = Alarm(
                panel_id=panel_id,
                opened_at=timestamp,
                last_seen_at=timestamp,
                resolved_at=None,
                severity=risk_result["status"],
                primary_risk=risk_result["primary_risk"],
                risk_score=risk_result["risk_score"],
                message=message,
                status="OPEN"
            )

            db.add(new_alarm)
            db.commit()
            db.refresh(new_alarm)

            return {
                "action": "OPENED",
                "alarm_id": new_alarm.id
            }

        # Alarm already exists -> update the same alarm.
        open_alarm.last_seen_at = timestamp
        open_alarm.severity = risk_result["status"]
        open_alarm.primary_risk = risk_result["primary_risk"]
        open_alarm.risk_score = risk_result["risk_score"]
        open_alarm.message = message

        db.commit()

        return {
            "action": "UPDATED",
            "alarm_id": open_alarm.id
        }

    return None


@app.get("/")
def root():
    return {
        "service": "GridGuard API",
        "status": "running",
        "version": "0.5.0"
    }


@app.get("/health")
def health_check(
    db: Session = Depends(get_db)
):
    connected_panels = db.query(Panel).count()

    return {
        "status": "healthy",
        "connected_panels": connected_panels
    }


@app.post("/telemetry")
def receive_telemetry(
    data: TelemetryData,
    db: Session = Depends(get_db)
):
    received_at = datetime.now(timezone.utc)

    # 1. Store raw telemetry.
    telemetry_record = Telemetry(
        panel_id=data.panel_id,
        timestamp=data.timestamp,
        received_at=received_at,
        current_a=data.current_a,
        cable_temperature_c=data.cable_temperature_c,
        ambient_temperature_c=data.ambient_temperature_c,
        humidity_pct=data.humidity_pct,
        pd_index=data.pd_index,
        arc_detected=data.arc_detected,
        data_quality=data.data_quality.value
    )

    db.add(telemetry_record)

    # 2. Update latest panel state.
    panel = (
        db.query(Panel)
        .filter(Panel.panel_id == data.panel_id)
        .first()
    )

    if panel is None:
        panel = Panel(
            panel_id=data.panel_id,
            last_seen=received_at,
            data_quality=data.data_quality.value
        )
        db.add(panel)

    panel.last_seen = received_at
    panel.current_a = data.current_a
    panel.cable_temperature_c = data.cable_temperature_c
    panel.ambient_temperature_c = data.ambient_temperature_c
    panel.humidity_pct = data.humidity_pct
    panel.pd_index = data.pd_index
    panel.arc_detected = data.arc_detected
    panel.data_quality = data.data_quality.value

    # Commit first so the new telemetry is available
    # when build_history() queries the database.
    db.commit()

    # 3. Automatically evaluate risk.
    history = build_history(
        db=db,
        panel_id=data.panel_id,
        limit=20
    )

    risk_result = evaluate_risk(history)

    # 4. Persist risk assessment.
    risk_record = RiskAssessment(
        panel_id=data.panel_id,
        timestamp=received_at,
        risk_score=risk_result["risk_score"],
        status=risk_result["status"],
        primary_risk=risk_result["primary_risk"],
        causes=risk_result["causes"],
        component_scores=risk_result.get(
            "component_scores"
        ),
        metrics=risk_result.get(
            "metrics"
        )
    )

    db.add(risk_record)
    db.commit()

    # 5. Open/update/resolve alarm if necessary.
    alarm_result = sync_alarm(
        db=db,
        panel_id=data.panel_id,
        risk_result=risk_result,
        timestamp=received_at
    )

    return {
        "status": "accepted",
        "received_at": received_at,
        "telemetry": data,
        "risk": risk_result,
        "alarm": alarm_result
    }


@app.get("/panels")
def get_panels(
    db: Session = Depends(get_db)
):
    panels = (
        db.query(Panel)
        .order_by(Panel.panel_id)
        .all()
    )

    return {
        "count": len(panels),
        "panels": [
            {
                "panel_id": panel.panel_id,
                "last_seen": panel.last_seen,
                "current_a": panel.current_a,
                "cable_temperature_c": panel.cable_temperature_c,
                "ambient_temperature_c": panel.ambient_temperature_c,
                "humidity_pct": panel.humidity_pct,
                "pd_index": panel.pd_index,
                "arc_detected": panel.arc_detected,
                "data_quality": panel.data_quality
            }
            for panel in panels
        ]
    }


@app.get("/panels/{panel_id}")
def get_panel(
    panel_id: str,
    db: Session = Depends(get_db)
):
    panel = (
        db.query(Panel)
        .filter(Panel.panel_id == panel_id)
        .first()
    )

    if panel is None:
        raise HTTPException(
            status_code=404,
            detail="Panel not found"
        )

    return {
        "panel_id": panel.panel_id,
        "last_seen": panel.last_seen,
        "current_a": panel.current_a,
        "cable_temperature_c": panel.cable_temperature_c,
        "ambient_temperature_c": panel.ambient_temperature_c,
        "humidity_pct": panel.humidity_pct,
        "pd_index": panel.pd_index,
        "arc_detected": panel.arc_detected,
        "data_quality": panel.data_quality
    }


@app.get("/panels/{panel_id}/telemetry")
def get_panel_telemetry(
    panel_id: str,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    panel = (
        db.query(Panel)
        .filter(Panel.panel_id == panel_id)
        .first()
    )

    if panel is None:
        raise HTTPException(
            status_code=404,
            detail="Panel not found"
        )

    limit = max(1, min(limit, 500))

    records = (
        db.query(Telemetry)
        .filter(Telemetry.panel_id == panel_id)
        .order_by(Telemetry.timestamp.desc())
        .limit(limit)
        .all()
    )

    return {
        "panel_id": panel_id,
        "count": len(records),
        "telemetry": [
            {
                "timestamp": record.timestamp,
                "received_at": record.received_at,
                "current_a": record.current_a,
                "cable_temperature_c": record.cable_temperature_c,
                "ambient_temperature_c": record.ambient_temperature_c,
                "humidity_pct": record.humidity_pct,
                "pd_index": record.pd_index,
                "arc_detected": record.arc_detected,
                "data_quality": record.data_quality
            }
            for record in records
        ]
    }


@app.get("/panels/{panel_id}/risk")
def get_panel_risk(
    panel_id: str,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    panel = (
        db.query(Panel)
        .filter(Panel.panel_id == panel_id)
        .first()
    )

    if panel is None:
        raise HTTPException(
            status_code=404,
            detail="Panel not found"
        )

    limit = max(3, min(limit, 100))

    history = build_history(
        db=db,
        panel_id=panel_id,
        limit=limit
    )

    if not history:
        raise HTTPException(
            status_code=404,
            detail="No telemetry history available for this panel"
        )

    risk_result = evaluate_risk(history)

    return {
        "panel_id": panel_id,
        "analyzed_points": len(history),
        **risk_result
    }