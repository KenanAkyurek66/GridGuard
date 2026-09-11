from sqlalchemy import Boolean, DateTime, Float, Integer, String
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