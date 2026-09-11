from sqlalchemy import Boolean, DateTime, Float, Integer, JSON, String
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.database import Base


class Panel(Base):
    __tablename__ = "panels"

    panel_id: Mapped[str] = mapped_column(
        String(50),
        primary_key=True
    )

    last_seen: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        nullable=False
    )

    current_a: Mapped[float | None] = mapped_column(
        Float,
        nullable=True
    )

    cable_temperature_c: Mapped[float | None] = mapped_column(
        Float,
        nullable=True
    )

    ambient_temperature_c: Mapped[float | None] = mapped_column(
        Float,
        nullable=True
    )

    humidity_pct: Mapped[float | None] = mapped_column(
        Float,
        nullable=True
    )

    pd_index: Mapped[float | None] = mapped_column(
        Float,
        nullable=True
    )

    arc_detected: Mapped[bool] = mapped_column(
        Boolean,
        default=False
    )

    data_quality: Mapped[str] = mapped_column(
        String(20),
        nullable=False
    )


class Telemetry(Base):
    __tablename__ = "telemetry"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    panel_id: Mapped[str] = mapped_column(
        String(50),
        index=True,
        nullable=False
    )

    timestamp: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        index=True,
        nullable=False
    )

    received_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        nullable=False
    )

    current_a: Mapped[float | None] = mapped_column(
        Float,
        nullable=True
    )

    cable_temperature_c: Mapped[float | None] = mapped_column(
        Float,
        nullable=True
    )

    ambient_temperature_c: Mapped[float | None] = mapped_column(
        Float,
        nullable=True
    )

    humidity_pct: Mapped[float | None] = mapped_column(
        Float,
        nullable=True
    )

    pd_index: Mapped[float | None] = mapped_column(
        Float,
        nullable=True
    )

    arc_detected: Mapped[bool] = mapped_column(
        Boolean,
        default=False
    )

    data_quality: Mapped[str] = mapped_column(
        String(20),
        nullable=False
    )


class RiskAssessment(Base):
    __tablename__ = "risk_assessments"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    panel_id: Mapped[str] = mapped_column(
        String(50),
        index=True,
        nullable=False
    )

    timestamp: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        index=True,
        nullable=False
    )

    risk_score: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False
    )

    primary_risk: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )

    causes: Mapped[list] = mapped_column(
        JSON,
        nullable=False
    )

    component_scores: Mapped[dict | None] = mapped_column(
        JSON,
        nullable=True
    )

    metrics: Mapped[dict | None] = mapped_column(
        JSON,
        nullable=True
    )


class Alarm(Base):
    __tablename__ = "alarms"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    panel_id: Mapped[str] = mapped_column(
        String(50),
        index=True,
        nullable=False
    )

    opened_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        nullable=False
    )

    last_seen_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        nullable=False
    )

    resolved_at: Mapped[DateTime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )

    severity: Mapped[str] = mapped_column(
        String(20),
        nullable=False
    )

    primary_risk: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )

    risk_score: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    message: Mapped[str] = mapped_column(
        String(500),
        nullable=False
    )

    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="OPEN"
    )