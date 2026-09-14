from datetime import datetime, timezone

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from backend.app.ai_service import (
    analyze_gridguard_intelligence,
    get_ai_runtime_status,
)
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
    version="0.6.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def build_history(
    db: Session,
    panel_id: str,
    limit: int = 20,
) -> list[dict]:
    records = (
        db.query(Telemetry)
        .filter(
            Telemetry.panel_id == panel_id,
            or_(
                Telemetry.data_quality != "BAD",
                Telemetry.arc_detected.is_(True),
            ),
        )
        .order_by(
            Telemetry.timestamp.desc(),
            Telemetry.id.desc(),
        )
        .limit(limit)
        .all()
    )

    # Database gives newest -> oldest.
    # Risk Engine expects oldest -> newest.
    records.reverse()

    history = []

    for record in records:
        # BAD analog telemetry must not influence deterministic
        # trends. A positive arc signal is retained as a
        # fail-safe digital safety event, but its analog values
        # are deliberately neutralized.
        if record.data_quality == "BAD":
            history.append(
                {
                    "current_a": None,
                    "cable_temperature_c": None,
                    "ambient_temperature_c": None,
                    "humidity_pct": None,
                    "pd_index": None,
                    "arc_detected": bool(
                        record.arc_detected
                    ),
                }
            )
            continue

        history.append(
            {
                "current_a": record.current_a,
                "cable_temperature_c": (
                    record.cable_temperature_c
                ),
                "ambient_temperature_c": (
                    record.ambient_temperature_c
                ),
                "humidity_pct": record.humidity_pct,
                "pd_index": record.pd_index,
                "arc_detected": record.arc_detected,
            }
        )

    return history


def build_ai_history(
    db: Session,
    panel_id: str,
    limit: int = 20,
) -> list[dict]:
    records = (
        db.query(Telemetry)
        .filter(Telemetry.panel_id == panel_id)
        .order_by(
            Telemetry.timestamp.desc(),
            Telemetry.id.desc(),
        )
        .limit(limit)
        .all()
    )

    # AI temporal features require oldest -> newest.
    records.reverse()

    return [
        {
            "current_a": record.current_a,
            "cable_temperature_c": record.cable_temperature_c,
            "ambient_temperature_c": record.ambient_temperature_c,
            "humidity_pct": record.humidity_pct,
            "pd_index": record.pd_index,
            "arc_detected": record.arc_detected,
            "data_quality": record.data_quality,
        }
        for record in records
    ]


def sync_alarm(
    db: Session,
    panel_id: str,
    risk_result: dict,
    timestamp: datetime,
    data_quality: str = "GOOD",
) -> dict | None:
    abnormal_statuses = {
        "WARNING",
        "HIGH",
        "CRITICAL",
    }

    open_alarm = (
        db.query(Alarm)
        .filter(
            Alarm.panel_id == panel_id,
            Alarm.status == "OPEN",
        )
        .order_by(Alarm.opened_at.desc())
        .first()
    )

    # A NORMAL result may resolve an alarm only when the newest
    # telemetry is fully trusted. DEGRADED telemetry can still
    # raise risk, but it cannot prove recovery on its own.
    if risk_result["status"] == "NORMAL":
        if open_alarm is not None:
            if data_quality != "GOOD":
                open_alarm.last_seen_at = timestamp
                db.commit()

                return {
                    "action": "HELD",
                    "alarm_id": open_alarm.id,
                    "reason": (
                        "Alarm resolution requires "
                        "GOOD telemetry quality."
                    ),
                }

            open_alarm.status = "RESOLVED"
            open_alarm.resolved_at = timestamp
            open_alarm.last_seen_at = timestamp

            db.commit()

            return {
                "action": "RESOLVED",
                "alarm_id": open_alarm.id,
            }

        return None

    # WARNING / HIGH / CRITICAL may still be opened or updated
    # from GOOD or DEGRADED telemetry. BAD analog telemetry does
    # not reach this path, except for the fail-safe arc case.
    if risk_result["status"] in abnormal_statuses:
        message = (
            risk_result["causes"][0]
            if risk_result["causes"]
            else "GridGuard anomaly detected."
        )

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
                status="OPEN",
            )

            db.add(new_alarm)
            db.commit()
            db.refresh(new_alarm)

            return {
                "action": "OPENED",
                "alarm_id": new_alarm.id,
            }

        open_alarm.last_seen_at = timestamp
        open_alarm.severity = risk_result["status"]
        open_alarm.primary_risk = risk_result["primary_risk"]
        open_alarm.risk_score = risk_result["risk_score"]
        open_alarm.message = message

        db.commit()

        return {
            "action": "UPDATED",
            "alarm_id": open_alarm.id,
        }

    return None


def normalize_event_timestamp(
    value: datetime,
) -> datetime:
    """
    Normalize timestamps to UTC for reliable chronological comparison.

    SQLite may return stored DateTime values without timezone
    information even when timezone=True is configured.
    Naive timestamps are therefore treated as UTC.
    """
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)

    return value.astimezone(timezone.utc)


def to_storage_timestamp(
    value: datetime,
) -> datetime:
    """
    Convert an event timestamp to UTC-naive form for consistent
    SQLite storage and equality checks.
    """
    return normalize_event_timestamp(
        value
    ).replace(tzinfo=None)


def telemetry_payload_matches(
    existing: Telemetry,
    incoming: TelemetryData,
) -> bool:
    """
    Return True when an existing event and incoming event contain
    the same telemetry payload.
    """
    return all(
        [
            existing.current_a == incoming.current_a,
            existing.cable_temperature_c
            == incoming.cable_temperature_c,
            existing.ambient_temperature_c
            == incoming.ambient_temperature_c,
            existing.humidity_pct == incoming.humidity_pct,
            existing.pd_index == incoming.pd_index,
            existing.arc_detected == incoming.arc_detected,
            existing.data_quality == incoming.data_quality.value,
        ]
    )


@app.get("/")
def root():
    return {
        "service": "GridGuard API",
        "status": "running",
        "version": "0.6.0",
    }


@app.get("/health")
def health_check(
    db: Session = Depends(get_db),
):
    connected_panels = db.query(Panel).count()

    return {
        "status": "healthy",
        "connected_panels": connected_panels,
    }


@app.get("/ai/status")
def ai_status():
    return get_ai_runtime_status()


@app.post("/telemetry")
def receive_telemetry(
    data: TelemetryData,
    db: Session = Depends(get_db),
):
    received_at = datetime.now(timezone.utc)
    quality = data.data_quality.value

    incoming_timestamp = normalize_event_timestamp(
        data.timestamp
    )

    storage_timestamp = to_storage_timestamp(
        data.timestamp
    )

    # ---------------------------------------------------------
    # 1. Duplicate / timestamp-collision protection.
    # ---------------------------------------------------------

    existing_same_event = (
        db.query(Telemetry)
        .filter(
            Telemetry.panel_id == data.panel_id,
            Telemetry.timestamp == storage_timestamp,
        )
        .order_by(Telemetry.id.desc())
        .first()
    )

    if existing_same_event is not None:
        if telemetry_payload_matches(
            existing_same_event,
            data,
        ):
            return {
                "status": "duplicate",
                "received_at": received_at,
                "telemetry": data,
                "processing": {
                    "duplicate": True,
                    "timestamp_conflict": False,
                    "out_of_order": False,
                    "history_stored": False,
                    "latest_state_updated": False,
                    "risk_evaluated": False,
                    "alarm_updated": False,
                    "quality_policy": "DUPLICATE",
                    "existing_telemetry_id": (
                        existing_same_event.id
                    ),
                },
                "risk": None,
                "alarm": None,
            }

        raise HTTPException(
            status_code=409,
            detail={
                "error": "TELEMETRY_TIMESTAMP_CONFLICT",
                "message": (
                    "Telemetry already exists for this "
                    "panel and timestamp with a different "
                    "payload."
                ),
                "panel_id": data.panel_id,
                "timestamp": incoming_timestamp.isoformat(),
                "existing_telemetry_id": (
                    existing_same_event.id
                ),
            },
        )

    # ---------------------------------------------------------
    # 2. Determine chronological ordering.
    # ---------------------------------------------------------

    latest_existing_telemetry = (
        db.query(Telemetry)
        .filter(
            Telemetry.panel_id == data.panel_id
        )
        .order_by(
            Telemetry.timestamp.desc(),
            Telemetry.id.desc(),
        )
        .first()
    )

    out_of_order = False

    if latest_existing_telemetry is not None:
        latest_timestamp = normalize_event_timestamp(
            latest_existing_telemetry.timestamp
        )

        out_of_order = (
            incoming_timestamp
            < latest_timestamp
        )

    # ---------------------------------------------------------
    # 3. Store every unique raw telemetry event.
    # ---------------------------------------------------------

    telemetry_record = Telemetry(
        panel_id=data.panel_id,
        timestamp=storage_timestamp,
        received_at=received_at,
        current_a=data.current_a,
        cable_temperature_c=(
            data.cable_temperature_c
        ),
        ambient_temperature_c=(
            data.ambient_temperature_c
        ),
        humidity_pct=data.humidity_pct,
        pd_index=data.pd_index,
        arc_detected=data.arc_detected,
        data_quality=quality,
    )

    db.add(telemetry_record)

    # ---------------------------------------------------------
    # 4. Load or create current panel state.
    # ---------------------------------------------------------

    panel = (
        db.query(Panel)
        .filter(
            Panel.panel_id == data.panel_id
        )
        .first()
    )

    if panel is None:
        if quality == "BAD":
            # There is no trusted measurement state yet. Keep
            # analog values unknown, but retain a positive arc
            # event as fail-safe evidence.
            panel = Panel(
                panel_id=data.panel_id,
                last_seen=received_at,
                current_a=None,
                cable_temperature_c=None,
                ambient_temperature_c=None,
                humidity_pct=None,
                pd_index=None,
                arc_detected=bool(
                    data.arc_detected
                ),
                data_quality=quality,
            )
        else:
            panel = Panel(
                panel_id=data.panel_id,
                last_seen=received_at,
                current_a=data.current_a,
                cable_temperature_c=(
                    data.cable_temperature_c
                ),
                ambient_temperature_c=(
                    data.ambient_temperature_c
                ),
                humidity_pct=data.humidity_pct,
                pd_index=data.pd_index,
                arc_detected=data.arc_detected,
                data_quality=quality,
            )

        db.add(panel)
        out_of_order = False

    else:
        # Even delayed unique telemetry confirms communication.
        panel.last_seen = received_at

        if not out_of_order:
            if quality == "BAD":
                # BAD analog values are stored in raw history but
                # cannot overwrite the latest trusted measurements.
                panel.data_quality = "BAD"

                # Positive arc evidence is fail-safe and may not
                # be suppressed solely because analog quality is BAD.
                if data.arc_detected:
                    panel.arc_detected = True

            else:
                # GOOD and DEGRADED telemetry may update the
                # current measurement state. DEGRADED data can
                # raise risk but cannot resolve an existing alarm.
                panel.current_a = data.current_a
                panel.cable_temperature_c = (
                    data.cable_temperature_c
                )
                panel.ambient_temperature_c = (
                    data.ambient_temperature_c
                )
                panel.humidity_pct = (
                    data.humidity_pct
                )
                panel.pd_index = data.pd_index
                panel.arc_detected = (
                    data.arc_detected
                )
                panel.data_quality = quality

    db.commit()
    db.refresh(telemetry_record)

    # ---------------------------------------------------------
    # 5. Out-of-order telemetry is history-only.
    # ---------------------------------------------------------

    if out_of_order:
        return {
            "status": "accepted",
            "received_at": received_at,
            "telemetry": data,
            "processing": {
                "duplicate": False,
                "timestamp_conflict": False,
                "out_of_order": True,
                "history_stored": True,
                "latest_state_updated": False,
                "risk_evaluated": False,
                "alarm_updated": False,
                "quality_policy": "HISTORY_ONLY",
                "telemetry_id": telemetry_record.id,
                "latest_event_timestamp": (
                    latest_existing_telemetry.timestamp
                    if latest_existing_telemetry
                    is not None
                    else None
                ),
            },
            "risk": None,
            "alarm": None,
        }

    # ---------------------------------------------------------
    # 6. BAD non-arc telemetry is stored but held from the
    #    deterministic risk and alarm pipeline.
    # ---------------------------------------------------------

    if quality == "BAD" and not data.arc_detected:
        latest_risk = (
            db.query(RiskAssessment)
            .filter(
                RiskAssessment.panel_id
                == data.panel_id
            )
            .order_by(
                RiskAssessment.id.desc()
            )
            .first()
        )

        open_alarm = (
            db.query(Alarm)
            .filter(
                Alarm.panel_id == data.panel_id,
                Alarm.status == "OPEN",
            )
            .order_by(
                Alarm.opened_at.desc()
            )
            .first()
        )

        preserved_risk = None

        if latest_risk is not None:
            preserved_risk = {
                "risk_score": latest_risk.risk_score,
                "status": latest_risk.status,
                "primary_risk": (
                    latest_risk.primary_risk
                ),
                "causes": latest_risk.causes or [],
                "component_scores": (
                    latest_risk.component_scores
                    or {}
                ),
                "metrics": (
                    latest_risk.metrics or {}
                ),
            }

        preserved_alarm = None

        if open_alarm is not None:
            preserved_alarm = {
                "action": "PRESERVED",
                "alarm_id": open_alarm.id,
                "reason": (
                    "BAD telemetry cannot change "
                    "the current alarm state."
                ),
            }

        return {
            "status": "accepted",
            "received_at": received_at,
            "telemetry": data,
            "processing": {
                "duplicate": False,
                "timestamp_conflict": False,
                "out_of_order": False,
                "history_stored": True,
                "latest_state_updated": False,
                "risk_evaluated": False,
                "alarm_updated": False,
                "quality_policy": "BAD_HOLD",
                "telemetry_id": telemetry_record.id,
            },
            "risk": preserved_risk,
            "alarm": preserved_alarm,
        }

    # ---------------------------------------------------------
    # 7. Build deterministic history. BAD analog telemetry is
    #    excluded; BAD positive arc events remain fail-safe.
    # ---------------------------------------------------------

    history = build_history(
        db=db,
        panel_id=data.panel_id,
        limit=20,
    )

    risk_result = evaluate_risk(history)

    # DEGRADED telemetry may raise or update risk, but a NORMAL
    # result is not trusted enough to prove recovery from an
    # existing alarm. Preserve the previous deterministic risk
    # until a GOOD sample confirms recovery.
    if quality == "DEGRADED" and risk_result["status"] == "NORMAL":
        open_alarm = (
            db.query(Alarm)
            .filter(
                Alarm.panel_id == data.panel_id,
                Alarm.status == "OPEN",
            )
            .order_by(
                Alarm.opened_at.desc()
            )
            .first()
        )

        if open_alarm is not None:
            latest_risk = (
                db.query(RiskAssessment)
                .filter(
                    RiskAssessment.panel_id
                    == data.panel_id
                )
                .order_by(
                    RiskAssessment.id.desc()
                )
                .first()
            )

            open_alarm.last_seen_at = received_at
            db.commit()

            preserved_risk = None

            if latest_risk is not None:
                preserved_risk = {
                    "risk_score": latest_risk.risk_score,
                    "status": latest_risk.status,
                    "primary_risk": (
                        latest_risk.primary_risk
                    ),
                    "causes": latest_risk.causes or [],
                    "component_scores": (
                        latest_risk.component_scores
                        or {}
                    ),
                    "metrics": (
                        latest_risk.metrics or {}
                    ),
                }

            return {
                "status": "accepted",
                "received_at": received_at,
                "telemetry": data,
                "processing": {
                    "duplicate": False,
                    "timestamp_conflict": False,
                    "out_of_order": False,
                    "history_stored": True,
                    "latest_state_updated": True,
                    "risk_evaluated": True,
                    "risk_persisted": False,
                    "alarm_updated": True,
                    "alarm_resolution_held": True,
                    "quality_policy": "DEGRADED_HOLD",
                    "telemetry_id": telemetry_record.id,
                },
                "risk": preserved_risk,
                "candidate_risk": risk_result,
                "alarm": {
                    "action": "HELD",
                    "alarm_id": open_alarm.id,
                    "reason": (
                        "GOOD telemetry is required "
                        "to confirm alarm recovery."
                    ),
                },
            }

    # ---------------------------------------------------------
    # 8. Persist deterministic risk assessment.
    # ---------------------------------------------------------

    risk_record = RiskAssessment(
        panel_id=data.panel_id,
        timestamp=received_at,
        risk_score=risk_result[
            "risk_score"
        ],
        status=risk_result[
            "status"
        ],
        primary_risk=risk_result[
            "primary_risk"
        ],
        causes=risk_result[
            "causes"
        ],
        component_scores=risk_result.get(
            "component_scores"
        ),
        metrics=risk_result.get(
            "metrics"
        ),
    )

    db.add(risk_record)
    db.commit()

    # ---------------------------------------------------------
    # 9. Synchronize alarm lifecycle with quality policy.
    # ---------------------------------------------------------

    alarm_result = sync_alarm(
        db=db,
        panel_id=data.panel_id,
        risk_result=risk_result,
        timestamp=received_at,
        data_quality=quality,
    )

    quality_policy = "STANDARD"

    if quality == "DEGRADED":
        quality_policy = "DEGRADED_CAUTION"

    elif quality == "BAD" and data.arc_detected:
        quality_policy = "ARC_FAIL_SAFE"

    return {
        "status": "accepted",
        "received_at": received_at,
        "telemetry": data,
        "processing": {
            "duplicate": False,
            "timestamp_conflict": False,
            "out_of_order": False,
            "history_stored": True,
            "latest_state_updated": (
                quality != "BAD"
                or bool(data.arc_detected)
            ),
            "risk_evaluated": True,
            "alarm_updated": (
                alarm_result is not None
            ),
            "alarm_resolution_held": (
                alarm_result is not None
                and alarm_result.get("action")
                == "HELD"
            ),
            "quality_policy": quality_policy,
            "telemetry_id": telemetry_record.id,
        },
        "risk": risk_result,
        "alarm": alarm_result,
    }


@app.get("/panels")
def get_panels(
    db: Session = Depends(get_db),
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
                "cable_temperature_c": (
                    panel.cable_temperature_c
                ),
                "ambient_temperature_c": (
                    panel.ambient_temperature_c
                ),
                "humidity_pct": panel.humidity_pct,
                "pd_index": panel.pd_index,
                "arc_detected": panel.arc_detected,
                "data_quality": panel.data_quality,
            }
            for panel in panels
        ],
    }


@app.get("/panels/{panel_id}")
def get_panel(
    panel_id: str,
    db: Session = Depends(get_db),
):
    panel = (
        db.query(Panel)
        .filter(Panel.panel_id == panel_id)
        .first()
    )

    if panel is None:
        raise HTTPException(
            status_code=404,
            detail="Panel not found",
        )

    return {
        "panel_id": panel.panel_id,
        "last_seen": panel.last_seen,
        "current_a": panel.current_a,
        "cable_temperature_c": (
            panel.cable_temperature_c
        ),
        "ambient_temperature_c": (
            panel.ambient_temperature_c
        ),
        "humidity_pct": panel.humidity_pct,
        "pd_index": panel.pd_index,
        "arc_detected": panel.arc_detected,
        "data_quality": panel.data_quality,
    }


@app.get("/panels/{panel_id}/telemetry")
def get_panel_telemetry(
    panel_id: str,
    limit: int = 20,
    db: Session = Depends(get_db),
):
    panel = (
        db.query(Panel)
        .filter(Panel.panel_id == panel_id)
        .first()
    )

    if panel is None:
        raise HTTPException(
            status_code=404,
            detail="Panel not found",
        )

    limit = max(1, min(limit, 500))

    records = (
        db.query(Telemetry)
        .filter(Telemetry.panel_id == panel_id)
        .order_by(
            Telemetry.timestamp.desc(),
            Telemetry.id.desc(),
        )
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
                "cable_temperature_c": (
                    record.cable_temperature_c
                ),
                "ambient_temperature_c": (
                    record.ambient_temperature_c
                ),
                "humidity_pct": record.humidity_pct,
                "pd_index": record.pd_index,
                "arc_detected": record.arc_detected,
                "data_quality": record.data_quality,
            }
            for record in records
        ],
    }


@app.get("/panels/{panel_id}/risk")
def get_panel_risk(
    panel_id: str,
    limit: int = 20,
    db: Session = Depends(get_db),
):
    panel = (
        db.query(Panel)
        .filter(Panel.panel_id == panel_id)
        .first()
    )

    if panel is None:
        raise HTTPException(
            status_code=404,
            detail="Panel not found",
        )

    limit = max(3, min(limit, 100))

    history = build_history(
        db=db,
        panel_id=panel_id,
        limit=limit,
    )

    if not history:
        raise HTTPException(
            status_code=404,
            detail=(
                "No telemetry history available "
                "for this panel"
            ),
        )

    risk_result = evaluate_risk(history)

    return {
        "panel_id": panel_id,
        "analyzed_points": len(history),
        **risk_result,
    }


@app.get("/panels/{panel_id}/intelligence")
def get_panel_intelligence(
    panel_id: str,
    history_limit: int = 20,
    db: Session = Depends(get_db),
):
    panel = (
        db.query(Panel)
        .filter(Panel.panel_id == panel_id)
        .first()
    )

    if panel is None:
        raise HTTPException(
            status_code=404,
            detail="Panel not found",
        )

    history_limit = max(
        5,
        min(history_limit, 100),
    )

    telemetry_rows = build_ai_history(
        db=db,
        panel_id=panel_id,
        limit=history_limit,
    )

    latest_risk = (
        db.query(RiskAssessment)
        .filter(
            RiskAssessment.panel_id
            == panel_id
        )
        .order_by(
            RiskAssessment.id.desc()
        )
        .first()
    )

    if latest_risk is None:
        return {
            "panel_id": panel_id,
            "available": False,
            "reason": (
                "No risk assessment available."
            ),
            "history_points": (
                len(telemetry_rows)
            ),
            "generated_at": datetime.now(
                timezone.utc
            ),
        }

    risk_result = {
        "risk_score": latest_risk.risk_score,
        "status": latest_risk.status,
        "primary_risk": (
            latest_risk.primary_risk
        ),
        "causes": latest_risk.causes or [],
        "component_scores": (
            latest_risk.component_scores
            or {}
        ),
        "metrics": (
            latest_risk.metrics
            or {}
        ),
    }

    intelligence = (
        analyze_gridguard_intelligence(
            telemetry_rows=telemetry_rows,
            risk_result=risk_result,
        )
    )

    return {
        "panel_id": panel_id,
        "generated_at": datetime.now(
            timezone.utc
        ),
        **intelligence,
    }


@app.get("/alarms")
def get_alarms(
    status: str | None = None,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    limit = max(1, min(limit, 500))

    query = db.query(Alarm)

    if status is not None:
        query = query.filter(
            Alarm.status == status.upper()
        )

    alarms = (
        query.order_by(
            Alarm.opened_at.desc()
        )
        .limit(limit)
        .all()
    )

    return {
        "count": len(alarms),
        "alarms": [
            {
                "id": alarm.id,
                "panel_id": alarm.panel_id,
                "opened_at": alarm.opened_at,
                "last_seen_at": (
                    alarm.last_seen_at
                ),
                "resolved_at": alarm.resolved_at,
                "severity": alarm.severity,
                "primary_risk": (
                    alarm.primary_risk
                ),
                "risk_score": alarm.risk_score,
                "message": alarm.message,
                "status": alarm.status,
            }
            for alarm in alarms
        ],
    }


@app.get("/panels/{panel_id}/risks")
def get_panel_risk_history(
    panel_id: str,
    limit: int = 50,
    db: Session = Depends(get_db),
):
    panel = (
        db.query(Panel)
        .filter(Panel.panel_id == panel_id)
        .first()
    )

    if panel is None:
        raise HTTPException(
            status_code=404,
            detail="Panel not found",
        )

    limit = max(1, min(limit, 500))

    records = (
        db.query(RiskAssessment)
        .filter(
            RiskAssessment.panel_id
            == panel_id
        )
        .order_by(
            RiskAssessment.timestamp.desc(),
            RiskAssessment.id.desc(),
        )
        .limit(limit)
        .all()
    )

    return {
        "panel_id": panel_id,
        "count": len(records),
        "risks": [
            {
                "timestamp": record.timestamp,
                "risk_score": record.risk_score,
                "status": record.status,
                "primary_risk": (
                    record.primary_risk
                ),
                "causes": record.causes,
                "component_scores": (
                    record.component_scores
                ),
                "metrics": record.metrics,
            }
            for record in records
        ],
    }


@app.get("/dashboard/summary")
def get_dashboard_summary(
    db: Session = Depends(get_db),
):
    connected_panels = db.query(Panel).count()

    # For each panel, identify the most recently
    # created risk assessment.
    latest_risk_ids = (
        db.query(
            func.max(
                RiskAssessment.id
            ).label("latest_id")
        )
        .group_by(
            RiskAssessment.panel_id
        )
        .subquery()
    )

    latest_risks = (
        db.query(RiskAssessment)
        .filter(
            RiskAssessment.id.in_(
                db.query(
                    latest_risk_ids.c.latest_id
                )
            )
        )
        .all()
    )

    distribution = {
        "NORMAL": 0,
        "WARNING": 0,
        "HIGH": 0,
        "CRITICAL": 0,
        "UNKNOWN": 0,
    }

    for risk in latest_risks:
        if risk.status in distribution:
            distribution[risk.status] += 1
        else:
            distribution["UNKNOWN"] += 1

    panels_with_risk = len(latest_risks)

    # Registered panels with no risk assessment yet.
    distribution["UNKNOWN"] += max(
        connected_panels - panels_with_risk,
        0,
    )

    active_alarms = (
        db.query(Alarm)
        .filter(Alarm.status == "OPEN")
        .count()
    )

    highest_risk_records = sorted(
        latest_risks,
        key=lambda item: (
            item.risk_score,
            item.id,
        ),
        reverse=True,
    )[:5]

    highest_risk_panels = [
        {
            "panel_id": record.panel_id,
            "risk_score": record.risk_score,
            "status": record.status,
            "primary_risk": (
                record.primary_risk
            ),
            "timestamp": record.timestamp,
        }
        for record in highest_risk_records
    ]

    return {
        "connected_panels": connected_panels,
        "risk_distribution": {
            "normal": distribution["NORMAL"],
            "warning": distribution["WARNING"],
            "high": distribution["HIGH"],
            "critical": (
                distribution["CRITICAL"]
            ),
            "unknown": distribution["UNKNOWN"],
        },
        "active_alarms": active_alarms,
        "highest_risk_panels": (
            highest_risk_panels
        ),
        "system_status": "ONLINE",
        "generated_at": datetime.now(
            timezone.utc
        ),
    }


@app.get("/dashboard/panels")
def get_dashboard_panels(
    status: str | None = None,
    search: str | None = None,
    limit: int = 200,
    db: Session = Depends(get_db),
):
    limit = max(1, min(limit, 500))

    panels = (
        db.query(Panel)
        .order_by(Panel.panel_id)
        .all()
    )

    # ---------------------------------------------------------
    # Latest risk record for every panel
    # ---------------------------------------------------------

    latest_risk_ids = (
        db.query(
            func.max(
                RiskAssessment.id
            ).label("latest_id")
        )
        .group_by(
            RiskAssessment.panel_id
        )
        .subquery()
    )

    latest_risks = (
        db.query(RiskAssessment)
        .filter(
            RiskAssessment.id.in_(
                db.query(
                    latest_risk_ids.c.latest_id
                )
            )
        )
        .all()
    )

    risk_by_panel = {
        risk.panel_id: risk
        for risk in latest_risks
    }

    # ---------------------------------------------------------
    # Open alarms
    # ---------------------------------------------------------

    open_alarms = (
        db.query(Alarm)
        .filter(Alarm.status == "OPEN")
        .all()
    )

    alarm_by_panel = {
        alarm.panel_id: alarm
        for alarm in open_alarms
    }

    # ---------------------------------------------------------
    # Build dashboard rows
    # ---------------------------------------------------------

    rows = []

    for panel in panels:
        risk = risk_by_panel.get(
            panel.panel_id
        )
        alarm = alarm_by_panel.get(
            panel.panel_id
        )

        if risk is None:
            risk_score = 0
            risk_status = "UNKNOWN"
            primary_risk = "NO_DATA"
        else:
            risk_score = risk.risk_score
            risk_status = risk.status
            primary_risk = (
                risk.primary_risk
            )

        row = {
            "panel_id": panel.panel_id,
            "status": risk_status,
            "risk_score": risk_score,
            "primary_risk": primary_risk,
            "current_a": panel.current_a,
            "cable_temperature_c": (
                panel.cable_temperature_c
            ),
            "ambient_temperature_c": (
                panel.ambient_temperature_c
            ),
            "humidity_pct": (
                panel.humidity_pct
            ),
            "pd_index": panel.pd_index,
            "arc_detected": (
                panel.arc_detected
            ),
            "data_quality": (
                panel.data_quality
            ),
            "last_seen": panel.last_seen,
            "has_open_alarm": (
                alarm is not None
            ),
            "alarm_id": (
                alarm.id
                if alarm is not None
                else None
            ),
            "alarm_severity": (
                alarm.severity
                if alarm is not None
                else None
            ),
        }

        rows.append(row)

    # ---------------------------------------------------------
    # Optional filtering
    # ---------------------------------------------------------

    if status:
        requested_status = (
            status.upper()
        )

        rows = [
            row
            for row in rows
            if row["status"]
            == requested_status
        ]

    if search:
        search_value = (
            search.strip().lower()
        )

        rows = [
            row
            for row in rows
            if search_value
            in row["panel_id"].lower()
        ]

    # ---------------------------------------------------------
    # Highest-risk panels first
    # ---------------------------------------------------------

    status_priority = {
        "CRITICAL": 4,
        "HIGH": 3,
        "WARNING": 2,
        "NORMAL": 1,
        "UNKNOWN": 0,
    }

    rows.sort(
        key=lambda row: (
            status_priority.get(
                row["status"],
                -1,
            ),
            row["risk_score"],
            row["panel_id"],
        ),
        reverse=True,
    )

    rows = rows[:limit]

    return {
        "count": len(rows),
        "panels": rows,
        "generated_at": datetime.now(
            timezone.utc
        ),
    }


@app.get(
    "/dashboard/panels/{panel_id}/detail"
)
def get_dashboard_panel_detail(
    panel_id: str,
    history_limit: int = 30,
    db: Session = Depends(get_db),
):
    history_limit = max(
        5,
        min(history_limit, 200),
    )

    # ---------------------------------------------------------
    # PANEL
    # ---------------------------------------------------------

    panel = (
        db.query(Panel)
        .filter(
            Panel.panel_id == panel_id
        )
        .first()
    )

    if panel is None:
        raise HTTPException(
            status_code=404,
            detail="Panel not found",
        )

    # ---------------------------------------------------------
    # LATEST RISK
    # ---------------------------------------------------------

    latest_risk = (
        db.query(RiskAssessment)
        .filter(
            RiskAssessment.panel_id
            == panel_id
        )
        .order_by(
            RiskAssessment.id.desc()
        )
        .first()
    )

    # ---------------------------------------------------------
    # ACTIVE ALARM
    # ---------------------------------------------------------

    active_alarm = (
        db.query(Alarm)
        .filter(
            Alarm.panel_id == panel_id,
            Alarm.status == "OPEN",
        )
        .order_by(
            Alarm.opened_at.desc()
        )
        .first()
    )

    # ---------------------------------------------------------
    # TELEMETRY HISTORY
    # ---------------------------------------------------------

    telemetry_records = (
        db.query(Telemetry)
        .filter(
            Telemetry.panel_id == panel_id
        )
        .order_by(
            Telemetry.timestamp.desc(),
            Telemetry.id.desc(),
        )
        .limit(history_limit)
        .all()
    )

    # Graphs should be oldest -> newest.
    telemetry_records.reverse()

    telemetry_history = [
        {
            "timestamp": record.timestamp,
            "current_a": record.current_a,
            "cable_temperature_c": (
                record.cable_temperature_c
            ),
            "ambient_temperature_c": (
                record.ambient_temperature_c
            ),
            "humidity_pct": (
                record.humidity_pct
            ),
            "pd_index": record.pd_index,
            "arc_detected": (
                record.arc_detected
            ),
            "data_quality": (
                record.data_quality
            ),
        }
        for record in telemetry_records
    ]

    # ---------------------------------------------------------
    # RISK HISTORY
    # ---------------------------------------------------------

    risk_records = (
        db.query(RiskAssessment)
        .filter(
            RiskAssessment.panel_id
            == panel_id
        )
        .order_by(
            RiskAssessment.id.desc()
        )
        .limit(history_limit)
        .all()
    )

    risk_records.reverse()

    risk_history = [
        {
            "timestamp": record.timestamp,
            "risk_score": (
                record.risk_score
            ),
            "status": record.status,
            "primary_risk": (
                record.primary_risk
            ),
        }
        for record in risk_records
    ]

    # ---------------------------------------------------------
    # LATEST RISK DATA
    # ---------------------------------------------------------

    if latest_risk is None:
        risk_data = {
            "risk_score": 0,
            "status": "UNKNOWN",
            "primary_risk": "NO_DATA",
            "causes": [
                "No risk assessment available."
            ],
            "component_scores": {},
            "metrics": {},
        }

    else:
        risk_data = {
            "risk_score": (
                latest_risk.risk_score
            ),
            "status": latest_risk.status,
            "primary_risk": (
                latest_risk.primary_risk
            ),
            "causes": (
                latest_risk.causes or []
            ),
            "component_scores": (
                latest_risk.component_scores
                or {}
            ),
            "metrics": (
                latest_risk.metrics or {}
            ),
        }

    # ---------------------------------------------------------
    # ACTIVE ALARM DATA
    # ---------------------------------------------------------

    if active_alarm is None:
        alarm_data = None

    else:
        alarm_data = {
            "id": active_alarm.id,
            "severity": (
                active_alarm.severity
            ),
            "primary_risk": (
                active_alarm.primary_risk
            ),
            "risk_score": (
                active_alarm.risk_score
            ),
            "message": (
                active_alarm.message
            ),
            "status": active_alarm.status,
            "opened_at": (
                active_alarm.opened_at
            ),
            "last_seen_at": (
                active_alarm.last_seen_at
            ),
        }

    # ---------------------------------------------------------
    # GRIDGUARD AI INTELLIGENCE
    # ---------------------------------------------------------
    #
    # AI is computed on demand for the selected panel instead
    # of on every telemetry ingestion. This keeps the 100-panel
    # simulator and ingestion pipeline lightweight.
    # ---------------------------------------------------------

    if latest_risk is None:
        intelligence = {
            "available": False,
            "reason": (
                "No risk assessment available."
            ),
            "history_points": (
                len(telemetry_history)
            ),
        }
    else:
        ai_history = build_ai_history(
            db=db,
            panel_id=panel_id,
            limit=max(
                20,
                history_limit,
            ),
        )

        intelligence = (
            analyze_gridguard_intelligence(
                telemetry_rows=ai_history,
                risk_result=risk_data,
            )
        )

    # ---------------------------------------------------------
    # RESPONSE
    # ---------------------------------------------------------

    return {
        "panel": {
            "panel_id": panel.panel_id,
            "last_seen": panel.last_seen,
            "current_a": panel.current_a,
            "cable_temperature_c": (
                panel.cable_temperature_c
            ),
            "ambient_temperature_c": (
                panel.ambient_temperature_c
            ),
            "humidity_pct": (
                panel.humidity_pct
            ),
            "pd_index": panel.pd_index,
            "arc_detected": (
                panel.arc_detected
            ),
            "data_quality": (
                panel.data_quality
            ),
        },
        "risk": risk_data,
        "intelligence": intelligence,
        "active_alarm": alarm_data,
        "telemetry_history": (
            telemetry_history
        ),
        "risk_history": risk_history,
        "generated_at": datetime.now(
            timezone.utc
        ),
    }
