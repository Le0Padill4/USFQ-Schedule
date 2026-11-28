"""Benchmark O1: generacion de TODOS los horarios factibles.

Candidatos: A = enumeracion exhaustiva + filtro; B = backtracking con poda;
C = CSP con forward checking y orden MRV.
Tamano = numero de combinaciones del espacio de busqueda (secciones ** materias).
Escenarios: pocos cruces (muchas franjas distintas) y muchos cruces (pocas franjas).
Se mide tiempo (ms, varias repeticiones) y pasos (nodos y comparaciones de cruce).
"""

from __future__ import annotations

import random
from pathlib import Path

from domain.scheduling import (
    EligibleCourse,
    Meeting,
    Offering,
    ScheduleRequest,
    Stats,
    build_problem,
    generate_backtracking,
    generate_csp,
    generate_exhaustive,
)

from .common import DEFAULT_SEED, summarize, time_runs, write_csv

SECTIONS = 10
FULL_SIZES = {1_000: 3, 10_000: 4, 100_000: 5, 1_000_000: 6}  # combinaciones -> materias
QUICK_SIZES = {1_000: 3, 10_000: 4, 100_000: 5}
SCENARIOS = {"pocos_cruces": 110, "muchos_cruces": 10, "cruces_extremos": 4}  # franjas
CANDIDATES = {
    "exhaustiva": generate_exhaustive,
    "backtracking": generate_backtracking,
    "csp": generate_csp,
}


def slot_pool(seed: int, size: int) -> list[tuple[int, int]]:
    slots = [(d, s) for d in range(5) for s in range(420, 1081, 30)]
    random.Random(f"pool-{seed}").shuffle(slots)
    return slots[:size]


def build_instance(
    n_courses: int, pool_size: int, seed: int, preferences=None, max_results: int = 10
):
    """Instancia sintetica: ``n_courses`` materias requeridas con SECTIONS paralelos cada una."""
    rng = random.Random(f"gen-{seed}-{n_courses}-{pool_size}")
    pool = slot_pool(seed, pool_size)
    eligible, nrc = [], 0
    for c in range(n_courses):
        offs = []
        for s in range(SECTIONS):
            meetings, days = [], set()
            for day, start in rng.sample(pool, k=min(len(pool), 1 + (rng.random() < 0.4))):
                if day not in days:
                    days.add(day)
                    meetings.append(Meeting(day, start, start + rng.choice((60, 90))))
            nrc += 1
            offs.append(
                Offering("SYN-T1", f"{nrc:06d}", f"SYN-B{c}", str(s + 1), "Docente sintetico",
                         tuple(sorted(meetings)), "fixture-sintetico", "2026-11-27")
            )
        eligible.append(EligibleCourse(f"SYN-B{c}", 3, tuple(offs)))
    kwargs = {} if preferences is None else {"preferences": preferences}
    request = ScheduleRequest(
        "SYN-T1", "1CMP", required_courses=tuple(e.course_code for e in eligible),
        max_results=max_results, **kwargs,
    )
    return build_problem(request, eligible)


def run(out_dir: Path, *, sizes=None, repeats: int = 5, seed: int = DEFAULT_SEED) -> list[dict]:
    sizes = sizes or FULL_SIZES
    raw, summary = [], []
    for scenario, pool_size in SCENARIOS.items():
        for size, n_courses in sizes.items():
            problem = build_instance(n_courses, pool_size, seed)
            expected, steps = None, {}
            for name, fn in CANDIDATES.items():  # equivalencia + pasos (una corrida por candidato)
                st = Stats()
                result = fn(problem, st)
                if expected is None:
                    expected = result
                elif result != expected:
                    raise RuntimeError(f"candidatos no equivalentes: {scenario}/{size}")
                steps[name] = st
            for name, fn in CANDIDATES.items():
                times = time_runs(lambda fn=fn, problem=problem: fn(problem), repeats)
                for i, t in enumerate(times, 1):
                    raw.append({"operation": "generacion", "scenario": scenario, "size": size,
                                "candidate": name, "repeat": i, "time_ms": round(t, 4)})
                summary.append({
                    "operation": "generacion", "scenario": scenario, "size": size,
                    "candidate": name, "repeats": repeats,
                    **{k: round(v, 4) for k, v in summarize(times).items()},
                    "nodes": steps[name].nodes, "conflict_checks": steps[name].conflict_checks,
                    "result_count": len(expected),
                })
    write_csv(out_dir / "generacion_raw.csv", raw,
              ["operation", "scenario", "size", "candidate", "repeat", "time_ms"])
    write_csv(out_dir / "generacion_summary.csv", summary,
              ["operation", "scenario", "size", "candidate", "repeats", "time_ms_median",
               "time_ms_min", "time_ms_max", "nodes", "conflict_checks", "result_count"])
    return summary
