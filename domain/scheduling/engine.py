"""Pipeline: validar -> generar -> puntuar -> Top-K."""

from __future__ import annotations

from .generation import generate_backtracking, generate_csp, generate_exhaustive
from .models import EligibleCourse
from .optimize import METHODS
from .request import ScheduleRequest, build_problem
from .scoring import ScheduleResult, score_schedule
from .topk import top_k_heap, top_k_sort

GENERATORS = {
    "exhaustive": generate_exhaustive,
    "backtracking": generate_backtracking,
    "csp": generate_csp,
}
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


def best_schedules(
    request: ScheduleRequest, eligible: list[EligibleCourse], *, method: str = "branch_and_bound"
) -> list[ScheduleResult]:
    """Los ``request.max_results`` mejores horarios; ``method`` elige el candidato."""
    return METHODS[method](build_problem(request, eligible))
