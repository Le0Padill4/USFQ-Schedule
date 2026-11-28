"""Benchmark O2: seleccion Top-K de resultados ya puntuados.

Candidatos: A = heap acotado propio (BoundedHeap); B = ordenamiento completo + corte.
Tamano = numero N de resultados. Escenarios (mezcla y forma de los datos):
- k10_aleatorio: k = 10, puntajes aleatorios, una sola consulta.
- k_decimo_aleatorio: k = N/10, puntajes aleatorios, una sola consulta.
- k_decimo_ascendente: k = N/10, puntajes ascendentes (peor caso del heap), una consulta.
- flujo_10_consultas: llegan N resultados en orden aleatorio y se pide el top-10 cada N/10
  llegadas (el candidato B reordena lo acumulado en cada consulta).
Se mide tiempo (ms), comparaciones (pasos) y pico de memoria extra (KiB).
"""

from __future__ import annotations

import random
from pathlib import Path

from domain.scheduling import BoundedHeap, ScheduleResult, Stats, top_k_heap, top_k_sort

from .common import DEFAULT_SEED, peak_kib, summarize, time_runs, write_csv

FULL_SIZES = (1_000, 10_000, 100_000, 1_000_000)
QUICK_SIZES = (1_000, 5_000, 20_000, 50_000)
SCENARIOS = (
    "k10_aleatorio",
    "k_decimo_aleatorio",
    "k_decimo_ascendente",
    "flujo_10_consultas",
)


def make_data(n: int, scenario: str, seed: int) -> list[ScheduleResult]:
    rng = random.Random(f"topk-{seed}-{n}-{scenario}")
    if scenario == "k_decimo_ascendente":
        scores = list(range(n))
    else:
        scores = [rng.randint(-10**6, 10**6) for _ in range(n)]
    return [ScheduleResult((f"{i:07d}",), s, ()) for i, s in enumerate(scores)]


def make_runners(scenario: str, data: list[ScheduleResult]):
    """Devuelve {candidato: fn(stats|None) -> respuesta} para el escenario."""
    n = len(data)
    if scenario == "flujo_10_consultas":
        step, k = max(1, n // 10), 10

        def heap(stats=None):
            h, answers = BoundedHeap(k, stats), []
            for i, item in enumerate(data, 1):
                h.offer(item)
                if i % step == 0:
                    answers.append(h.best_first())
            return answers

        def sort(stats=None):
            acc, answers = [], []
            for i, item in enumerate(data, 1):
                acc.append(item)
                if i % step == 0:
                    answers.append(top_k_sort(acc, k, stats))
            return answers

        return {"heap": heap, "ordenamiento": sort}, k
    k = 10 if scenario == "k10_aleatorio" else max(1, n // 10)
    return {
        "heap": lambda stats=None: top_k_heap(data, k, stats),
        "ordenamiento": lambda stats=None: top_k_sort(data, k, stats),
    }, k


def run(out_dir: Path, *, sizes=None, repeats: int = 5, seed: int = DEFAULT_SEED) -> list[dict]:
    sizes = sizes or FULL_SIZES
    raw, summary = [], []
    for scenario in SCENARIOS:
        for n in sizes:
            data = make_data(n, scenario, seed)
            runners, k = make_runners(scenario, data)
            answers, steps, mem = {}, {}, {}
            for name, fn in runners.items():
                st = Stats()
                answers[name] = fn(st)  # equivalencia + pasos (una corrida)
                steps[name] = st.comparisons
                mem[name] = peak_kib(fn)
            if answers["heap"] != answers["ordenamiento"]:
                raise RuntimeError(f"candidatos no equivalentes: {scenario}/{n}")
            for name, fn in runners.items():
                times = time_runs(fn, repeats)
                for i, t in enumerate(times, 1):
                    raw.append({"operation": "topk", "scenario": scenario, "size": n,
                                "candidate": name, "repeat": i, "time_ms": round(t, 4)})
                summary.append({
                    "operation": "topk", "scenario": scenario, "size": n, "candidate": name,
                    "k": k, "repeats": repeats,
                    **{key: round(v, 4) for key, v in summarize(times).items()},
                    "comparisons": steps[name], "peak_kib": round(mem[name], 1),
                })
    write_csv(out_dir / "topk_raw.csv", raw,
              ["operation", "scenario", "size", "candidate", "repeat", "time_ms"])
    write_csv(out_dir / "topk_summary.csv", summary,
              ["operation", "scenario", "size", "candidate", "k", "repeats", "time_ms_median",
               "time_ms_min", "time_ms_max", "comparisons", "peak_kib"])
    return summary
