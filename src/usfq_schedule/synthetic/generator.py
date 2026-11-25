"""Generador sintetico determinista (misma semilla => mismo catalogo).

Parametros utiles para benchmarks: ``slot_pool`` (menos franjas distintas => mas cruces),
``sections`` (paralelos por materia) y ``n_*`` (cantidad de materias por tipo).
"""

from __future__ import annotations

import random
from dataclasses import dataclass

from usfq_schedule.domain.scheduling import Meeting, Offering

from .catalog import (
    CourseRec,
    CurriculumEntry,
    PrerequisiteGroup,
    SyntheticCatalog,
)

TERM = "SYN-T1"
SOURCE = "fixture-sintetico"
RETRIEVED_AT = "2026-11-24"
_DAYS = range(5)
_STARTS = range(420, 1081, 30)  # 07:00 a 18:00 cada 30 min
_DURATIONS = (60, 90)


@dataclass(frozen=True)
class CatalogParams:
    seed: int = 0
    n_general: int = 3
    n_english: int = 2
    n_shared: int = 6
    n_core_cmp: int = 8
    n_core_mac: int = 8
    n_labs: int = 2
    n_exercises: int = 2
    n_electives: int = 4
    sections: tuple[int, int] = (1, 3)
    slot_pool: int = 30
    multi_meeting_prob: float = 0.5
    prereq_prob: float = 0.7
    alt_prereq_prob: float = 0.3
    offered_prob: float = 0.9


def _slot_pool(seed: int, size: int) -> list[tuple[int, int]]:
    slots = [(d, s) for d in _DAYS for s in _STARTS]
    random.Random(f"pool-{seed}").shuffle(slots)
    return slots[: max(1, min(size, len(slots)))]


def generate_catalog(params: CatalogParams | None = None) -> SyntheticCatalog:
    params = params or CatalogParams()
    rng = random.Random(f"catalog-{params.seed}")
    courses: list[CourseRec] = []
    entries: list[CurriculumEntry] = []
    groups: list[PrerequisiteGroup] = []
    forced_alt = False

    def add(code: str, credits: int, kinds: dict[str, str], pool: list[str]) -> None:
        nonlocal forced_alt
        courses.append(CourseRec(code, f"Materia sintetica {code}", credits))
        for career, kind in kinds.items():
            entries.append(CurriculumEntry(career, code, kind))
        if not pool:
            return
        n_groups = 0
        if rng.random() < params.prereq_prob:
            n_groups = 1 + (rng.random() < 0.25)
        # Garantiza al menos un grupo OR en todo catalogo (cobertura exigida).
        if not forced_alt and len(pool) >= 2 and code.startswith("SYN-C") and n_groups == 0:
            n_groups = 1
            forced = True
        else:
            forced = False
        chosen: set[str] = set()
        for _ in range(n_groups):
            avail = [p for p in pool if p not in chosen]
            if not avail:
                break
            want_alt = forced or rng.random() < params.alt_prereq_prob
            k = 2 if (want_alt and len(avail) >= 2) else 1
            alts = tuple(sorted(rng.sample(avail, k)))
            chosen.update(alts)
            groups.append(PrerequisiteGroup(code, alts))
            if k == 2:
                forced_alt = True
            forced = False

    both = ("1CMP", "1MAC")
    general = [f"SYN-G{i}" for i in range(1, params.n_general + 1)]
    english = [f"SYN-E{i}" for i in range(1, params.n_english + 1)]
    shared = [f"SYN-S{i}" for i in range(1, params.n_shared + 1)]
    core_cmp = [f"SYN-C{i}" for i in range(1, params.n_core_cmp + 1)]
    core_mac = [f"SYN-M{i}" for i in range(1, params.n_core_mac + 1)]
    labs = [f"SYN-L{i}" for i in range(1, params.n_labs + 1)]
    exercises = [f"SYN-R{i}" for i in range(1, params.n_exercises + 1)]
    electives = [f"SYN-X{i}" for i in range(1, params.n_electives + 1)]

    for code in general:
        add(code, 3, dict.fromkeys(both, "general_college"), [])
    for code in english:
        add(code, 2, dict.fromkeys(both, "english"), [])
    for i, code in enumerate(shared):
        add(code, 4, dict.fromkeys(both, "shared"), shared[:i] + general)
    for i, code in enumerate(core_cmp):
        add(code, 4, {"1CMP": "core"}, shared + general + core_cmp[:i])
    for i, code in enumerate(core_mac):
        add(code, 4, {"1MAC": "core"}, shared + general + core_mac[:i])
    for code in labs:
        add(code, 1, {"1CMP": "lab"}, core_cmp[:3])
    for code in exercises:
        add(code, 1, {"1MAC": "exercise"}, core_mac[:3])
    for i, code in enumerate(electives):
        kinds = {"1CMP": "elective"}
        if i % 2 == 0:
            kinds["1MAC"] = "optional"
        add(code, 3, kinds, shared + general)
    # Trampas de prefijo: el codigo "parece" de una carrera pero la malla lo decide.
    add("SYNCMP901", 3, {}, [])  # prefijo CMP, en ninguna malla
    add("SYNMAC902", 3, {"1CMP": "elective"}, [])  # prefijo MAC, dentro de la malla 1CMP

    pool = _slot_pool(params.seed, params.slot_pool)
    offerings: list[Offering] = []
    counter = 0
    for course in courses:
        if rng.random() >= params.offered_prob:
            continue
        for section in range(1, rng.randint(*params.sections) + 1):
            n_meet = 1 + (rng.random() < params.multi_meeting_prob) + (rng.random() < 0.2)
            order = pool[:]
            rng.shuffle(order)
            used_days: set[int] = set()
            meetings = []
            for day, start in order:
                if day in used_days:
                    continue
                used_days.add(day)
                meetings.append(Meeting(day, start, start + rng.choice(_DURATIONS)))
                if len(meetings) == n_meet:
                    break
            counter += 1
            offerings.append(
                Offering(
                    term=TERM,
                    nrc=str(10000 + counter),
                    course_code=course.code,
                    section=str(section),
                    instructor_label=f"Docente sintetico {rng.randint(1, 8)}",
                    meetings=tuple(sorted(meetings)),
                    source=SOURCE,
                    retrieved_at=RETRIEVED_AT,
                )
            )
    return SyntheticCatalog(
        term=TERM,
        courses=tuple(courses),
        entries=tuple(entries),
        prerequisite_groups=tuple(groups),
        offerings=tuple(offerings),
    )


def tiny_catalog() -> SyntheticCatalog:
    """Catalogo escrito a mano para razonar resultados sin ejecutar nada.

    Cruces conocidos (dia 0 = lunes): 1001 vs 2002, 1001 vs 4001, 2002 vs 4001 y 1001 vs 6001
    (miercoles). 1001 y 2001 son consecutivas (sin cruce).
    """

    def off(nrc, code, *meetings):
        return Offering(
            term=TERM,
            nrc=nrc,
            course_code=code,
            section="1",
            instructor_label="Docente sintetico",
            meetings=tuple(Meeting(*m) for m in meetings),
            source=SOURCE,
            retrieved_at=RETRIEVED_AT,
        )

    c = CourseRec
    return SyntheticCatalog(
        term=TERM,
        courses=(
            c("SYN-G1", "Materia sintetica SYN-G1", 3),
            c("SYN-S1", "Materia sintetica SYN-S1", 4),
            c("SYN-S2", "Materia sintetica SYN-S2", 4),
            c("SYN-C1", "Materia sintetica SYN-C1", 4),
            c("SYN-C2", "Materia sintetica SYN-C2", 4),
            c("SYN-M1", "Materia sintetica SYN-M1", 4),
            c("SYN-X1", "Materia sintetica SYN-X1", 3),
            c("SYNCMP901", "Materia sintetica SYNCMP901", 3),
        ),
        entries=(
            CurriculumEntry("1CMP", "SYN-G1", "general_college"),
            CurriculumEntry("1MAC", "SYN-G1", "general_college"),
            CurriculumEntry("1CMP", "SYN-S1", "shared"),
            CurriculumEntry("1MAC", "SYN-S1", "shared"),
            CurriculumEntry("1CMP", "SYN-S2", "shared"),
            CurriculumEntry("1MAC", "SYN-S2", "shared"),
            CurriculumEntry("1CMP", "SYN-C1", "core"),
            CurriculumEntry("1CMP", "SYN-C2", "core"),
            CurriculumEntry("1MAC", "SYN-M1", "core"),
            CurriculumEntry("1CMP", "SYN-X1", "elective"),
        ),
        prerequisite_groups=(
            PrerequisiteGroup("SYN-S2", ("SYN-S1",)),
            PrerequisiteGroup("SYN-C1", ("SYN-G1",)),
            PrerequisiteGroup("SYN-M1", ("SYN-G1", "SYN-S1")),
            PrerequisiteGroup("SYN-C2", ("SYN-C1",)),
            PrerequisiteGroup("SYN-C2", ("SYN-S1", "SYN-S2")),
        ),
        offerings=(
            off("1001", "SYN-G1", (0, 480, 540), (2, 480, 540)),
            off("1002", "SYN-G1", (1, 480, 540)),
            off("2001", "SYN-S1", (0, 540, 600)),
            off("2002", "SYN-S1", (0, 500, 560)),
            off("3001", "SYN-S2", (4, 600, 690)),
            off("4001", "SYN-C1", (0, 480, 540), (3, 600, 660)),
            off("5001", "SYN-M1", (1, 480, 570)),
            off("6001", "SYN-C2", (2, 500, 560)),
            off("9001", "SYNCMP901", (3, 480, 540)),
        ),
    )
