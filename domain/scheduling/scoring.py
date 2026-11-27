"""Puntaje determinista, entero y explicable de un horario.

Terminos (siempre en este orden; uno inactivo tiene peso 0):
free_day, days_used(-), gap_minutes(-), preferred_minutes, avoided_minutes(-), optional_priority.
``points = raw_value * weight`` y ``score = sum(points)``. Orden de resultados: ``(-score, nrcs)``.
"""

from __future__ import annotations

from dataclasses import dataclass

from .models import Meeting
from .request import Problem


@dataclass(frozen=True)
class ScoreTerm:
    name: str
    raw_value: int
    weight: int
    points: int


@dataclass(frozen=True)
class ScheduleResult:
    nrcs: tuple[str, ...]
    score: int
    explanations: tuple[ScoreTerm, ...]


def rank_key(result: ScheduleResult) -> tuple[int, tuple[str, ...]]:
    return (-result.score, result.nrcs)


def _overlap_minutes(m: Meeting, r: Meeting) -> int:
    if m.day != r.day:
        return 0
    return max(0, min(m.end_minute, r.end_minute) - max(m.start_minute, r.start_minute))


def score_schedule(nrcs: tuple[str, ...], problem: Problem) -> ScheduleResult:
    p = problem.preferences
    offerings = [problem.offerings_by_nrc[n] for n in nrcs]
    by_day: dict[int, list[Meeting]] = {}
    for off in offerings:
        for m in off.meetings:
            by_day.setdefault(m.day, []).append(m)

    free = 1 if (p.free_day is not None and p.free_day not in by_day) else 0
    days = len(by_day)
    gaps = 0
    for ms in by_day.values():
        ms = sorted(ms)
        for a, b in zip(ms, ms[1:]):
            gaps += max(0, b.start_minute - a.end_minute)
    preferred = sum(_overlap_minutes(m, r) for ms in by_day.values() for m in ms
                    for r in p.preferred_ranges)
    avoided = sum(_overlap_minutes(m, r) for ms in by_day.values() for m in ms
                  for r in p.avoided_ranges)
    prio = sum(problem.priority_by_course.get(o.course_code, 0) for o in offerings)

    raw = [
        ("free_day", free, p.w_free_day if p.free_day is not None else 0),
        ("days_used", days, -p.w_days if p.minimize_days else 0),
        ("gap_minutes", gaps, -p.w_gaps if p.minimize_gaps else 0),
        ("preferred_minutes", preferred, p.w_preferred if p.preferred_ranges else 0),
        ("avoided_minutes", avoided, -p.w_avoided if p.avoided_ranges else 0),
        ("optional_priority", prio, p.w_priority),
    ]
    terms = tuple(ScoreTerm(name, value, weight, value * weight) for name, value, weight in raw)
    return ScheduleResult(nrcs, sum(t.points for t in terms), terms)
