from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class DataQuality(str, Enum):
    GOOD = "GOOD"
    DEGRADED = "DEGRADED"
    BAD = "BAD"


class TelemetryData(BaseModel):
    panel_id: str = Field(min_length=1, max_length=50)
    timestamp: datetime

    current_a: float | None = Field(default=None, ge=0)
    cable_temperature_c: float | None = None
    ambient_temperature_c: float | None = None
    humidity_pct: float | None = Field(default=None, ge=0, le=100)

    pd_index: float | None = Field(default=None, ge=0, le=100)
    arc_detected: bool = False

    data_quality: DataQuality = DataQuality.GOOD