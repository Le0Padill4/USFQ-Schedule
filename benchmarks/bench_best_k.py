"""Benchmark O1 (reformulada): los K mejores horarios.

Candidatos: A = generar todos (CSP) + puntuar + Top-K con heap; B = branch and bound con
cota optimista (descarta ramas que no pueden entrar al Top-K). Ambos devuelven exactamente
lo mismo (el arnes lo comprueba antes de medir).
Tamano = combinaciones del espacio de busqueda (10 paralelos por materia, 3 a 6 materias).
Escenarios (preferencias y k):
- preferencias_fuertes_k10: dia libre, menos dias y franjas preferidas/evitadas; k = 10.
- sin_preferencias_k10: sin preferencias (todo empata); k = 10.
- preferencias_fuertes_k_grande: igual que el primero con k = 100 000.
- solo_huecos_k10: solo minimizar huecos (cota debil); k = 10.
Se mide tiempo y pasos (nodos, comparaciones de cruce, comparaciones del heap, cotas, podas).
"""

from __future__ import annotations

from pathlib import Path

from domain.scheduling import (
    Meeting,
    Preferences,
    Stats,
    best_schedules_all,
    best_schedules_bnb,
)

from .bench_generation import FULL_SIZES, build_instance
from .common import DEFAULT_SEED, summarize, time_runs, write_csv

POOL = 110  # franjas distintas: pocos cruces, muchos horarios factibles
STRONG = Preferences(
    free_day=4,
    minimize_days=True,
    preferred_ranges=(Meeting(0, 540, 720), Meeting(2, 540, 720), Meeting(3, 540, 720)),
    avoided_ranges=(Meeting(1, 420, 540), Meeting(4, 420, 540)),
    w_free_day=100, w_days=10, w_preferred=2, w_avoided=3,
)
SCENARIOS = {
    "preferencias_fuertes_k10": (STRONG, 10),
    "sin_preferencias_k10": (None, 10),
    "preferencias_fuertes_k_grande": (STRONG, 100_000),
    "solo_huecos_k10": (Preferences(minimize_gaps=True), 10),
}
CANDIDATES = {"todos_topk": best_schedules_all, "branch_and_bound": best_schedules_bnb}
STEP_FIELDS = ["nodes", "conflict_checks", "comparisons", "bounds", "pruned"]


def run(out_dir: Path, *, sizes=None, repeats: int = 5, seed: int = DEFAULT_SEED) -> list[dict]:
    sizes = sizes or FULL_SIZES
    raw, summary = [], []
    for scenario, (prefs, k) in SCENARIOS.items():
        for size, n_courses in sizes.items():
            problem = build_instance(n_courses, POOL, seed, prefs, k)
            expected, steps = None, {}
            for name, fn in CANDIDATES.items():  # equivalencia + pasos
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
                    raw.append({"operation": "mejores_k", "scenario": scenario, "size": size,
                                "candidate": name, "repeat": i, "time_ms": round(t, 4)})
                summary.append({
                    "operation": "mejores_k", "scenario": scenario, "size": size,
                    "candidate": name, "k": k, "repeats": repeats,
                    **{key: round(v, 4) for key, v in summarize(times).items()},
                    **{f: getattr(steps[name], f) for f in STEP_FIELDS},
                    "result_count": len(expected),
                })
    write_csv(out_dir / "mejores_k_raw.csv", raw,
              ["operation", "scenario", "size", "candidate", "repeat", "time_ms"])
    write_csv(out_dir / "mejores_k_summary.csv", summary,
              ["operation", "scenario", "size", "candidate", "k", "repeats", "time_ms_median",
               "time_ms_min", "time_ms_max", *STEP_FIELDS, "result_count"])
    return summary
