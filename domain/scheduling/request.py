"""Solicitud de horarios, validacion y construccion del problema (contrato I3 v0.2).

``build_problem`` normaliza la solicitud para que TODOS los candidatos resuelvan exactamente
el mismo problema: una oferta por materia requerida, cero o una por materia opcional,
sin cruces, respetando paralelos fijados, dias/franjas bloqueados y limites de creditos.
El orden de validacion (y por tanto el codigo de error cuando hay varios fallos) es:
carrera, max_results, catalogo elegible, restricciones/preferencias, listas de materias,
NOT_ELIGIBLE, paralelos fijados.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .errors import ErrorCode, ScheduleError
from .models import DAYS_PER_WEEK, EligibleCourse, Meeting, Offering

SUPPORTED_CAREERS = ("1CMP", "1MAC")


@dataclass(frozen=True)
class Constraints:
    """Restricciones obligatorias."""

    max_credits: int | None = None
    min_credits: int = 0
    blocked_days: frozenset[int] = frozenset()
    blocked_ranges: tuple[Meeting, ...] = ()


@dataclass(frozen=True)
class Preferences:
    """Preferencias flexibles: solo afectan el puntaje. Un termino inactivo pesa 0."""

    free_day: int | None = None
    minimize_days: bool = False
    minimize_gaps: bool = False
    preferred_ranges: tuple[Meeting, ...] = ()
    avoided_ranges: tuple[Meeting, ...] = ()
    w_free_day: int = 100
    w_days: int = 10
    w_gaps: int = 1
    w_preferred: int = 2
    w_avoided: int = 3
    w_priority: int = 10


@dataclass(frozen=True)
class ScheduleRequest:
    term: str
    career_id: str
    required_courses: tuple[str, ...] = ()
    optional_courses: tuple[tuple[str, int], ...] = ()  # (codigo, prioridad >= 1)
    pinned: tuple[tuple[str, str], ...] = ()  # (codigo de materia, nrc)
    constraints: Constraints = field(default_factory=Constraints)
    preferences: Preferences = field(default_factory=Preferences)
    max_results: int = 10


@dataclass(frozen=True)
class Slot:
    course_code: str
    credits: int
    optional: bool
    priority: int
    options: tuple[Offering, ...]


@dataclass(frozen=True, eq=False)
class Problem:
    slots: tuple[Slot, ...]
    min_credits: int
    max_credits: int | None
    max_results: int
    preferences: Preferences
    offerings_by_nrc: dict[str, Offering]
    priority_by_course: dict[str, int]


def _is_int(value: object) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def _bad(msg: str, code: ErrorCode = ErrorCode.INVALID_RANGE) -> ScheduleError:
    return ScheduleError(code, msg)


def _validate_day(day: object, what: str) -> None:
    if not _is_int(day) or not 0 <= day < DAYS_PER_WEEK:
        raise _bad(f"{what} fuera de 0..6: {day!r}")


def build_problem(request: ScheduleRequest, eligible: list[EligibleCourse]) -> Problem:
    if request.career_id not in SUPPORTED_CAREERS:
        raise _bad(f"carrera no soportada: {request.career_id!r}", ErrorCode.CAREER_NOT_SUPPORTED)
    if not _is_int(request.max_results) or request.max_results < 1:
        raise _bad(f"max_results invalido: {request.max_results!r}")

    by_code: dict[str, EligibleCourse] = {}
    by_nrc: dict[str, Offering] = {}
    for ec in eligible:
        if ec.course_code in by_code:
            raise _bad(f"materia elegible repetida: {ec.course_code}")
        by_code[ec.course_code] = ec
        for off in ec.offerings:
            if off.nrc in by_nrc:
                raise _bad(f"NRC repetido: {off.nrc}", ErrorCode.DUPLICATE_NRC)
            by_nrc[off.nrc] = off

    cons, prefs = request.constraints, request.preferences
    if not _is_int(cons.min_credits) or cons.min_credits < 0:
        raise _bad(f"min_credits invalido: {cons.min_credits!r}")
    if cons.max_credits is not None and (not _is_int(cons.max_credits) or cons.max_credits < 1):
        raise _bad(f"max_credits invalido: {cons.max_credits!r}")
    if cons.max_credits is not None and cons.min_credits > cons.max_credits:
        raise _bad("min_credits > max_credits")
    for day in cons.blocked_days:
        _validate_day(day, "blocked_days")
    if prefs.free_day is not None:
        _validate_day(prefs.free_day, "free_day")
    for name in ("w_free_day", "w_days", "w_gaps", "w_preferred", "w_avoided", "w_priority"):
        if not _is_int(getattr(prefs, name)):
            raise _bad(f"{name} debe ser entero")

    required = list(request.required_courses)
    optional = list(request.optional_courses)
    if len(set(required)) != len(required):
        raise _bad("materia requerida repetida")
    opt_codes = [code for code, _ in optional]
    if len(set(opt_codes)) != len(opt_codes):
        raise _bad("materia opcional repetida")
    if set(required) & set(opt_codes):
        raise _bad("materia a la vez requerida y opcional")
    for _, prio in optional:
        if not _is_int(prio) or prio < 1:
            raise _bad(f"prioridad invalida: {prio!r}")
    for code in required + opt_codes:
        if code not in by_code:
            raise _bad(f"materia no habilitada: {code}", ErrorCode.NOT_ELIGIBLE)

    pins: dict[str, str] = {}
    for code, nrc in request.pinned:
        if code in pins:
            raise _bad(f"paralelo fijado repetido para {code}")
        if code not in required and code not in opt_codes:
            raise _bad(f"paralelo fijado de materia no solicitada: {code}", ErrorCode.NOT_ELIGIBLE)
        if nrc not in {o.nrc for o in by_code[code].offerings}:
            raise _bad(f"NRC {nrc!r} no existe en {code}", ErrorCode.UNKNOWN_NRC)
        pins[code] = nrc

    def allowed(off: Offering) -> bool:
        for m in off.meetings:
            if m.day in cons.blocked_days:
                return False
            for r in cons.blocked_ranges:
                if m.day == r.day and m.start_minute < r.end_minute and r.start_minute < m.end_minute:
                    return False
        return True

    priority = dict(optional)
    slots = []
    for code in required + opt_codes:
        ec = by_code[code]
        options = tuple(
            o for o in ec.offerings if allowed(o) and (code not in pins or o.nrc == pins[code])
        )
        slots.append(Slot(code, ec.credits, code in priority, priority.get(code, 0), options))
    slots.sort(key=lambda s: (s.optional, len(s.options), s.course_code))
    return Problem(
        slots=tuple(slots),
        min_credits=cons.min_credits,
        max_credits=cons.max_credits,
        max_results=request.max_results,
        preferences=prefs,
        offerings_by_nrc=by_nrc,
        priority_by_course=priority,
    )
