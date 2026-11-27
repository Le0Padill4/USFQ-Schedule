"""Version LENTA de referencia: listas simples y conjuntos de minutos, facil de revisar a mano.

Reimplementa de forma independiente la validacion, la factibilidad (cruces por minutos),
el puntaje y el ranking, sin reutilizar el codigo de los candidatos. Solo para pruebas.
"""

from __future__ import annotations

from .errors import ErrorCode, ScheduleError
from .models import EligibleCourse
from .request import SUPPORTED_CAREERS, ScheduleRequest
from .scoring import ScheduleResult, ScoreTerm


def _int(x):
    return isinstance(x, int) and not isinstance(x, bool)


def _fail(code, msg="ref"):
    raise ScheduleError(code, msg)


def _minutes(meetings):
    return [(m.day, t) for m in meetings for t in range(m.start_minute, m.end_minute)]


def _validate(req: ScheduleRequest, eligible: list[EligibleCourse]) -> None:
    I = ErrorCode.INVALID_RANGE
    if req.career_id not in SUPPORTED_CAREERS:
        _fail(ErrorCode.CAREER_NOT_SUPPORTED)
    if not _int(req.max_results) or req.max_results < 1:
        _fail(I)
    seen_codes, seen_nrcs = [], []
    for ec in eligible:
        if ec.course_code in seen_codes:
            _fail(I)
        seen_codes.append(ec.course_code)
        for off in ec.offerings:
            if off.nrc in seen_nrcs:
                _fail(ErrorCode.DUPLICATE_NRC)
            seen_nrcs.append(off.nrc)
    c, p = req.constraints, req.preferences
    if not _int(c.min_credits) or c.min_credits < 0:
        _fail(I)
    if c.max_credits is not None and (not _int(c.max_credits) or c.max_credits < 1):
        _fail(I)
    if c.max_credits is not None and c.min_credits > c.max_credits:
        _fail(I)
    for d in c.blocked_days:
        if not _int(d) or d < 0 or d > 6:
            _fail(I)
    if p.free_day is not None and (not _int(p.free_day) or p.free_day < 0 or p.free_day > 6):
        _fail(I)
    for w in (p.w_free_day, p.w_days, p.w_gaps, p.w_preferred, p.w_avoided, p.w_priority):
        if not _int(w):
            _fail(I)
    req_codes = list(req.required_courses)
    opt_codes = [x for x, _ in req.optional_courses]
    if len(set(req_codes)) != len(req_codes) or len(set(opt_codes)) != len(opt_codes):
        _fail(I)
    for x in req_codes:
        if x in opt_codes:
            _fail(I)
    for _, prio in req.optional_courses:
        if not _int(prio) or prio < 1:
            _fail(I)
    for x in req_codes + opt_codes:
        if x not in seen_codes:
            _fail(ErrorCode.NOT_ELIGIBLE)
    pinned_courses = []
    for code, nrc in req.pinned:
        if code in pinned_courses:
            _fail(I)
        pinned_courses.append(code)
        if code not in req_codes and code not in opt_codes:
            _fail(ErrorCode.NOT_ELIGIBLE)
        offs = [o for ec in eligible if ec.course_code == code for o in ec.offerings]
        if nrc not in [o.nrc for o in offs]:
            _fail(ErrorCode.UNKNOWN_NRC)


def reference_generate(req: ScheduleRequest, eligible: list[EligibleCourse]) -> list[tuple]:
    _validate(req, eligible)
    c = req.constraints
    pins = dict(req.pinned)
    blocked = set()
    for r in c.blocked_ranges:
        blocked.update(_minutes([r]))
    for d in c.blocked_days:
        blocked.update((d, t) for t in range(1440))

    def options(code):
        ec = next(e for e in eligible if e.course_code == code)
        out = []
        for off in ec.offerings:
            if code in pins and off.nrc != pins[code]:
                continue
            if any(mm in blocked for mm in _minutes(off.meetings)):
                continue
            out.append(off)
        return ec.credits, out

    plan = [(x, False) for x in req.required_courses] + [(x, True) for x, _ in req.optional_courses]
    partials = [[]]  # lista de listas de (creditos, oferta)
    for code, optional in plan:
        credits, opts = options(code)
        nxt = []
        for part in partials:
            if optional:
                nxt.append(part)
            for off in opts:
                nxt.append(part + [(credits, off)])
        partials = nxt
    result = []
    for part in partials:
        if not part:
            continue
        total = sum(cr for cr, _ in part)
        if total < c.min_credits or (c.max_credits is not None and total > c.max_credits):
            continue
        used = set()
        clash = False
        for _, off in part:
            mins = _minutes(off.meetings)
            if any(mm in used for mm in mins):
                clash = True
                break
            used.update(mins)
        if not clash:
            result.append(tuple(sorted(off.nrc for _, off in part)))
    return sorted(set(result))


def reference_score(nrcs, req: ScheduleRequest, eligible: list[EligibleCourse]) -> ScheduleResult:
    p = req.preferences
    offs = [o for ec in eligible for o in ec.offerings if o.nrc in nrcs]
    mins = _minutes([m for o in offs for m in o.meetings])
    days = sorted({d for d, _ in mins})
    free = 1 if (p.free_day is not None and p.free_day not in days) else 0
    gaps = 0
    for d in days:
        today = sorted(t for dd, t in mins if dd == d)
        gaps += (today[-1] + 1 - today[0]) - len(today)
    def in_ranges(ranges):
        total = 0
        for r in ranges:
            rm = set(_minutes([r]))
            total += sum(1 for mm in mins if mm in rm)
        return total
    prio = dict(req.optional_courses)
    prio_sum = sum(prio.get(o.course_code, 0) for o in offs)
    raw = [
        ("free_day", free, p.w_free_day if p.free_day is not None else 0),
        ("days_used", len(days), -p.w_days if p.minimize_days else 0),
        ("gap_minutes", gaps, -p.w_gaps if p.minimize_gaps else 0),
        ("preferred_minutes", in_ranges(p.preferred_ranges), p.w_preferred if p.preferred_ranges else 0),
        ("avoided_minutes", in_ranges(p.avoided_ranges), -p.w_avoided if p.avoided_ranges else 0),
        ("optional_priority", prio_sum, p.w_priority),
    ]
    terms = tuple(ScoreTerm(n, v, w, v * w) for n, v, w in raw)
    return ScheduleResult(tuple(nrcs), sum(t.points for t in terms), terms)


def reference_schedules(req: ScheduleRequest, eligible: list[EligibleCourse]) -> list[ScheduleResult]:
    scored = [reference_score(c, req, eligible) for c in reference_generate(req, eligible)]
    # Seleccion del mejor repetida k veces (O(n*k)), a proposito simple.
    remaining = list(scored)
    out = []
    while remaining and len(out) < req.max_results:
        best = remaining[0]
        for r in remaining[1:]:
            if r.score > best.score or (r.score == best.score and r.nrcs < best.nrcs):
                best = r
        out.append(best)
        remaining.remove(best)
    return out
