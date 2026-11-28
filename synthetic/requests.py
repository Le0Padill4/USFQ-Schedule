"""Solicitudes aleatorias reproducibles (validas e invalidas) para pruebas y benchmarks."""

from __future__ import annotations

import random
from dataclasses import replace

from domain.scheduling import (
    Constraints,
    EligibleCourse,
    Meeting,
    Preferences,
    ScheduleRequest,
)

from .catalog import SyntheticCatalog, eligible_courses

INVALID_KINDS = (
    "unknown_nrc", "not_eligible", "dup_required", "bad_max_results", "bad_career",
    "dup_nrc", "min_gt_max", "bad_blocked_day", "pin_not_requested", "bad_priority",
)


def _rand_meeting(rng: random.Random) -> Meeting:
    start = rng.randrange(420, 1000, 30)
    return Meeting(rng.randrange(0, 5), start, start + rng.choice((60, 90, 180)))


def random_request(
    rng: random.Random,
    catalog: SyntheticCatalog,
    *,
    max_courses: int = 4,
    invalid_prob: float = 0.0,
) -> tuple[ScheduleRequest, list[EligibleCourse]]:
    career = rng.choice(("1CMP", "1MAC"))
    codes = sorted(catalog.course_codes())
    passed = {c for c in codes if rng.random() < 0.35}
    eligible = eligible_courses(catalog, career, passed)
    pool = [e.course_code for e in eligible]
    rng.shuffle(pool)
    n_req = min(len(pool), rng.randint(0, max_courses - 1))
    required = tuple(pool[:n_req])
    n_opt = min(len(pool) - n_req, rng.randint(0, 2))
    optional = tuple((c, rng.randint(1, 5)) for c in pool[n_req : n_req + n_opt])
    by_code = {e.course_code: e for e in eligible}
    pinned = []
    for code in required + tuple(c for c, _ in optional):
        if by_code[code].offerings and rng.random() < 0.2:
            pinned.append((code, rng.choice(by_code[code].offerings).nrc))
    max_credits = rng.choice((None, None, 6, 9, 12, 16, 20))
    min_credits = rng.choice((0, 0, 3, 4, 8))
    if max_credits is not None and min_credits > max_credits:
        min_credits = 0
    constraints = Constraints(
        max_credits=max_credits,
        min_credits=min_credits,
        blocked_days=frozenset(d for d in range(5) if rng.random() < 0.08),
        blocked_ranges=tuple(_rand_meeting(rng) for _ in range(rng.choice((0, 0, 1)))),
    )
    prefs = Preferences(
        free_day=rng.choice((None, None, 4, 0)),
        minimize_days=rng.random() < 0.5,
        minimize_gaps=rng.random() < 0.5,
        preferred_ranges=tuple(_rand_meeting(rng) for _ in range(rng.choice((0, 1, 2)))),
        avoided_ranges=tuple(_rand_meeting(rng) for _ in range(rng.choice((0, 1)))),
    )
    if rng.random() < 0.5:  # pesos arbitrarios: negativos, cero y grandes
        w = {name: rng.randint(-5, 15) for name in (
            "w_free_day", "w_days", "w_gaps", "w_preferred", "w_avoided", "w_priority")}
        prefs = replace(prefs, **w)
    req = ScheduleRequest(
        term=catalog.term,
        career_id=career,
        required_courses=required,
        optional_courses=optional,
        pinned=tuple(pinned),
        constraints=constraints,
        preferences=prefs,
        max_results=rng.randint(1, 8),
    )
    if rng.random() < invalid_prob:
        req, eligible = _make_invalid(rng, req, eligible)
    return req, eligible


def _make_invalid(rng, req, eligible):
    kind = rng.choice(INVALID_KINDS)
    if kind == "unknown_nrc":
        courses = req.required_courses
        if courses:
            return replace(req, pinned=((courses[0], "NO-NRC"),)), eligible
    elif kind == "not_eligible":
        return replace(req, required_courses=req.required_courses + ("NO-COURSE",)), eligible
    elif kind == "dup_required":
        if req.required_courses:
            return replace(req, required_courses=req.required_courses + req.required_courses[:1]), eligible
    elif kind == "bad_max_results":
        return replace(req, max_results=rng.choice((0, -3))), eligible
    elif kind == "bad_career":
        return replace(req, career_id="1XXX"), eligible
    elif kind == "dup_nrc":
        offs = [(i, o) for i, e in enumerate(eligible) for o in e.offerings]
        if len(offs) >= 2:
            (_, a), (j, b) = offs[0], offs[-1]
            if a.nrc != b.nrc:
                new = list(eligible)
                new[j] = replace(
                    new[j],
                    offerings=tuple(replace(o, nrc=a.nrc) if o is b else o for o in new[j].offerings),
                )
                return req, new
    elif kind == "min_gt_max":
        return replace(req, constraints=replace(req.constraints, min_credits=9, max_credits=4)), eligible
    elif kind == "bad_blocked_day":
        return replace(req, constraints=replace(req.constraints, blocked_days=frozenset({9}))), eligible
    elif kind == "pin_not_requested":
        for e in eligible:
            asked = set(req.required_courses) | {c for c, _ in req.optional_courses}
            if e.course_code not in asked and e.offerings:
                pin = (e.course_code, e.offerings[0].nrc)
                return replace(req, pinned=req.pinned + (pin,)), eligible
    elif kind == "bad_priority":
        return replace(req, optional_courses=req.optional_courses + (("NO-COURSE", 0),)), eligible
    return req, eligible
