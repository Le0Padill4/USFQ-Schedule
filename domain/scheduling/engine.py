"""Pipeline: validar -> generar -> puntuar -> Top-K."""

from __future__ import annotations

from .generation import generate_backtracking, generate_exhaustive
from .models import EligibleCourse
from .request import ScheduleRequest, build_problem
from .scoring import ScheduleResult, score_schedule
from .topk import top_k_heap, top_k_sort

GENERATORS = {"exhaustive": generate_exhaustive, "backtracking": generate_backtracking}
SELECTORS = {"heap": top_k_heap, "sort": top_k_sort}


def generate_schedules(
    request: ScheduleRequest,
    eligible: list[EligibleCourse],
    *,
    generator: str = "backtracking",
    selector: str = "heap",
) -> list[ScheduleResult]:
    problem = build_problem(request, eligible)
    combos = GENERATORS[generator](problem)
    scored = [score_schedule(c, problem) for c in combos]
    return SELECTORS[selector](scored, problem.max_results)
