"""Modelos de dominio de scheduling: reuniones, ofertas y solapes.

Codificacion (propuesta I3, pendiente de confirmar con I2):
- ``day``: entero 0 (lunes) a 6 (domingo).
- minutos desde 00:00; ``0 <= start_minute < end_minute <= 1440``.
- Intervalo semiabierto ``[start, end)``: clases consecutivas no se cruzan.
"""

from __future__ import annotations

from dataclasses import dataclass

from .errors import ErrorCode, ScheduleError

DAYS_PER_WEEK = 7
MINUTES_PER_DAY = 1440


@dataclass(frozen=True, order=True)
class Meeting:
    day: int
    start_minute: int
    end_minute: int

    def __post_init__(self) -> None:
        for name in ("day", "start_minute", "end_minute"):
            value = getattr(self, name)
            if isinstance(value, bool) or not isinstance(value, int):
                raise ScheduleError(ErrorCode.INVALID_RANGE, f"{name} debe ser entero: {value!r}")
        if not 0 <= self.day < DAYS_PER_WEEK:
            raise ScheduleError(ErrorCode.INVALID_RANGE, f"day fuera de 0..6: {self.day}")
        if not 0 <= self.start_minute < self.end_minute <= MINUTES_PER_DAY:
            raise ScheduleError(
                ErrorCode.INVALID_RANGE,
                f"se exige 0 <= start < end <= {MINUTES_PER_DAY}: "
                f"({self.start_minute}, {self.end_minute})",
            )


@dataclass(frozen=True)
class Offering:
    """Paralelo ofertado. Campos segun ``docs/CONTRATOS_INTEGRACION.md``."""

    term: str
    nrc: str
    course_code: str
    section: str
    instructor_label: str
    meetings: tuple[Meeting, ...]
    source: str
    retrieved_at: str

    def __post_init__(self) -> None:
        if not self.nrc:
            raise ScheduleError(ErrorCode.INVALID_RANGE, "nrc vacio")
        if not self.course_code:
            raise ScheduleError(ErrorCode.INVALID_RANGE, "course_code vacio")
        object.__setattr__(self, "meetings", tuple(self.meetings))
        if not self.meetings:
            raise ScheduleError(ErrorCode.INVALID_RANGE, f"oferta {self.nrc} sin reuniones")


@dataclass(frozen=True)
class EligibleCourse:
    """Materia habilitada con sus paralelos; la arma la capa de aplicacion."""

    course_code: str
    credits: int
    offerings: tuple[Offering, ...]

    def __post_init__(self) -> None:
        if isinstance(self.credits, bool) or not isinstance(self.credits, int) or self.credits < 1:
            raise ScheduleError(ErrorCode.INVALID_RANGE, f"credits invalido: {self.credits!r}")
        object.__setattr__(self, "offerings", tuple(self.offerings))
        for off in self.offerings:
            if off.course_code != self.course_code:
                raise ScheduleError(
                    ErrorCode.INVALID_RANGE,
                    f"oferta {off.nrc} es de {off.course_code}, no de {self.course_code}",
                )


def meetings_overlap(a: Meeting, b: Meeting) -> bool:
    """True si comparten algun minuto el mismo dia (intervalos semiabiertos)."""
    return a.day == b.day and a.start_minute < b.end_minute and b.start_minute < a.end_minute


def offerings_conflict(a: Offering, b: Offering) -> bool:
    """Referencia por pares: cruce si alguna reunion de ``a`` se solapa con alguna de ``b``."""
    return any(meetings_overlap(ma, mb) for ma in a.meetings for mb in b.meetings)
