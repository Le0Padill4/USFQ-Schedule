"""Generacion, validacion y ranking de horarios (Integrante 3)."""

from .engine import GENERATORS, SELECTORS, best_schedules, generate_schedules
from .errors import ErrorCode, ScheduleError
from .generation import Stats, generate_backtracking, generate_csp, generate_exhaustive
from .models import (
    DAYS_PER_WEEK,
    MINUTES_PER_DAY,
    EligibleCourse,
    Meeting,
    Offering,
    meetings_overlap,
    offerings_conflict,
)
from .optimize import (
    METHODS,
    best_schedules_all,
    best_schedules_bnb,
    score_upper_bound,
)
from .request import (
    SUPPORTED_CAREERS,
    Constraints,
    Preferences,
    Problem,
    ScheduleRequest,
    Slot,
    build_problem,
)
from .scoring import ScheduleResult, ScoreTerm, rank_key, score_schedule
from .topk import BoundedHeap, top_k_heap, top_k_sort

__all__ = [
    "DAYS_PER_WEEK",
    "GENERATORS",
    "METHODS",
    "MINUTES_PER_DAY",
    "SELECTORS",
    "SUPPORTED_CAREERS",
    "BoundedHeap",
    "Constraints",
    "EligibleCourse",
    "ErrorCode",
    "Meeting",
    "Offering",
    "Preferences",
    "Problem",
    "ScheduleError",
    "ScheduleRequest",
    "ScheduleResult",
    "ScoreTerm",
    "Slot",
    "Stats",
    "best_schedules",
    "best_schedules_all",
    "best_schedules_bnb",
    "build_problem",
    "generate_backtracking",
    "generate_csp",
    "generate_exhaustive",
    "generate_schedules",
    "meetings_overlap",
    "offerings_conflict",
    "rank_key",
    "score_schedule",
    "score_upper_bound",
    "top_k_heap",
    "top_k_sort",
]
