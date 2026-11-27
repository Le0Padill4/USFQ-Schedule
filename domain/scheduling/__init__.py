"""Generacion, validacion y ranking de horarios (Integrante 3)."""

from .errors import ErrorCode, ScheduleError
from .models import (
    DAYS_PER_WEEK,
    MINUTES_PER_DAY,
    EligibleCourse,
    Meeting,
    Offering,
    meetings_overlap,
    offerings_conflict,
)

__all__ = [
    "DAYS_PER_WEEK",
    "MINUTES_PER_DAY",
    "EligibleCourse",
    "ErrorCode",
    "Meeting",
    "Offering",
    "ScheduleError",
    "meetings_overlap",
    "offerings_conflict",
]
