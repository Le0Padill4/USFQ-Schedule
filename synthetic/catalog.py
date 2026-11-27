"""Estructuras de un catalogo sintetico y un MOCK de habilitacion de materias.

Todo lo de este paquete es sintetico: codigos ``SYN...``, docentes y NRC
inventados para pruebas. ``eligible_courses`` es un mock temporal de lo que
hara el grafo curricular de I1; sirve para alimentar las pruebas del generador
hasta que ese modulo exista. No define el contrato real.
"""

from __future__ import annotations

from dataclasses import dataclass

from domain.scheduling import (
    SUPPORTED_CAREERS,
    EligibleCourse,
    ErrorCode,
    Offering,
    ScheduleError,
)


@dataclass(frozen=True)
class CourseRec:
    code: str
    title: str
    credits: int


@dataclass(frozen=True)
class CurriculumEntry:
    career_id: str
    course_code: str
    kind: str  # core, shared, general_college, english, lab, exercise, optional, elective


@dataclass(frozen=True)
class PrerequisiteGroup:
    """AND de ORs: la materia exige cumplir cada grupo con al menos una alternativa."""

    course_code: str
    alternatives: tuple[str, ...]


@dataclass(frozen=True)
class SyntheticCatalog:
    term: str
    courses: tuple[CourseRec, ...]
    entries: tuple[CurriculumEntry, ...]
    prerequisite_groups: tuple[PrerequisiteGroup, ...]
    offerings: tuple[Offering, ...]

    def course_codes(self) -> frozenset[str]:
        return frozenset(c.code for c in self.courses)

    def career_codes(self, career_id: str) -> frozenset[str]:
        return frozenset(e.course_code for e in self.entries if e.career_id == career_id)


def eligible_courses(
    catalog: SyntheticCatalog, career_id: str, passed_codes: frozenset[str] | set[str]
) -> list[EligibleCourse]:
    """MOCK de I1: materias de la malla, no aprobadas, con prerrequisitos cumplidos y oferta.

    Devuelve ``EligibleCourse`` ordenadas por codigo; las ofertas conservan el orden del catalogo.
    """
    if career_id not in SUPPORTED_CAREERS:
        raise ScheduleError(ErrorCode.CAREER_NOT_SUPPORTED, f"carrera no soportada: {career_id!r}")
    known = catalog.course_codes()
    for code in passed_codes:
        if code not in known:
            raise ScheduleError(ErrorCode.UNKNOWN_COURSE, f"materia aprobada desconocida: {code!r}")
    in_career = catalog.career_codes(career_id)
    groups: dict[str, list[tuple[str, ...]]] = {}
    for g in catalog.prerequisite_groups:
        groups.setdefault(g.course_code, []).append(g.alternatives)
    result = []
    for course in sorted(catalog.courses, key=lambda c: c.code):
        if course.code not in in_career or course.code in passed_codes:
            continue
        if not all(any(a in passed_codes for a in alts) for alts in groups.get(course.code, [])):
            continue
        offs = tuple(o for o in catalog.offerings if o.course_code == course.code)
        if offs:
            result.append(EligibleCourse(course.code, course.credits, offs))
    return result
