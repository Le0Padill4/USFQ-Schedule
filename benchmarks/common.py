"""Utilidades comunes: temporizacion, memoria, CSV y entorno."""

from __future__ import annotations

import csv
import gc
import json
import os
import platform
import statistics
import sys
import time
import tracemalloc
from collections.abc import Callable
from datetime import datetime, timezone
from pathlib import Path

DEFAULT_SEED = 20261127


def time_runs(fn: Callable[[], object], repeats: int) -> list[float]:
    """Tiempos de pared en ms de ``repeats`` ejecuciones (recoleccion de basura previa)."""
    out = []
    for _ in range(repeats):
        gc.collect()
        t0 = time.perf_counter()
        fn()
        out.append((time.perf_counter() - t0) * 1000)
    return out


def peak_kib(fn: Callable[[], object]) -> float:
    """Pico de memoria extra (KiB) reservada durante ``fn`` segun tracemalloc.

    Solo cuenta lo asignado dentro de ``fn``; los datos de entrada creados antes no cuentan.
    """
    gc.collect()
    tracemalloc.start()
    try:
        fn()
        _, peak = tracemalloc.get_traced_memory()
    finally:
        tracemalloc.stop()
    return peak / 1024


def summarize(times: list[float]) -> dict[str, float]:
    return {
        "time_ms_median": statistics.median(times),
        "time_ms_min": min(times),
        "time_ms_max": max(times),
    }


def write_csv(path: Path, rows: list[dict], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def read_csv(path: Path) -> list[dict]:
    with path.open(newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def write_environment(out_dir: Path, **extra: object) -> None:
    info = {
        "python": sys.version.split()[0],
        "implementation": platform.python_implementation(),
        "platform": platform.platform(),
        "processor": platform.processor(),
        "cpu_count": os.cpu_count(),
        "run_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        **extra,
    }
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "environment.json").write_text(json.dumps(info, indent=2), encoding="utf-8")
