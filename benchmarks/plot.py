"""Graficos reproducibles (matplotlib, solo dependencia de desarrollo): uno por operacion.

Cada figura: columnas = escenarios, filas = metricas (tiempo y pasos; memoria en Top-K).
Ejes logaritmicos; linea = mediana de las repeticiones, banda = minimo a maximo.
Color y marcador fijos por candidato (azul/naranja/violeta, validados para daltonismo; el
marcador distinto evita depender solo del color).
"""

from __future__ import annotations

from pathlib import Path

from .common import read_csv

STYLE = {
    "exhaustiva": ("#6a4ce2", "s"),
    "backtracking": ("#257de0", "o"),
    "csp": ("#f47230", "^"),
    "heap": ("#257de0", "o"),
    "ordenamiento": ("#f47230", "^"),
}
METRICS = {
    "generacion": [
        ("time_ms_median", "Tiempo (ms)", True),
        ("nodes", "Nodos visitados", False),
        ("conflict_checks", "Comparaciones de cruce", False),
    ],
    "topk": [
        ("time_ms_median", "Tiempo (ms)", True),
        ("comparisons", "Comparaciones", False),
        ("peak_kib", "Pico de memoria extra (KiB)", False),
    ],
}
TITLES = {
    "generacion": "Generación de horarios: tiempo y pasos",
    "topk": "Top-K: tiempo, comparaciones y memoria",
}
XLABEL = {"generacion": "Tamaño (combinaciones del espacio de búsqueda)",
          "topk": "Tamaño (N resultados)"}


def plot_operation(operation: str, results_dir: Path) -> Path:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    rows = read_csv(results_dir / f"{operation}_summary.csv")
    scenarios = list(dict.fromkeys(r["scenario"] for r in rows))
    candidates = list(dict.fromkeys(r["candidate"] for r in rows))
    metrics = METRICS[operation]
    fig, axes = plt.subplots(
        len(metrics), len(scenarios), figsize=(3.6 * len(scenarios), 2.9 * len(metrics)),
        squeeze=False, constrained_layout=True,
    )
    for c, scenario in enumerate(scenarios):
        for r, (key, label, has_band) in enumerate(metrics):
            ax = axes[r][c]
            for cand in candidates:
                pts = sorted(
                    (int(x["size"]), x) for x in rows
                    if x["scenario"] == scenario and x["candidate"] == cand
                )
                if not pts:
                    continue
                xs = [p for p, _ in pts]
                ys = [max(float(x[key]), 1e-3) for _, x in pts]
                color, marker = STYLE[cand]
                ax.plot(xs, ys, color=color, marker=marker, markersize=5, linewidth=2,
                        label=cand)
                if has_band:
                    lo = [max(float(x["time_ms_min"]), 1e-3) for _, x in pts]
                    hi = [max(float(x["time_ms_max"]), 1e-3) for _, x in pts]
                    ax.fill_between(xs, lo, hi, color=color, alpha=0.15, linewidth=0)
            ax.set_xscale("log")
            ax.set_yscale("log")
            ax.grid(True, color="#e6e6e6", linewidth=0.6)
            ax.set_axisbelow(True)
            for side in ("top", "right"):
                ax.spines[side].set_visible(False)
            ax.tick_params(labelsize=8, colors="#666666")
            if r == 0:
                ax.set_title(scenario.replace("_", " "), fontsize=10, color="#191919")
            if c == 0:
                ax.set_ylabel(label, fontsize=9, color="#191919")
            if r == len(metrics) - 1:
                ax.set_xlabel(XLABEL[operation], fontsize=8, color="#666666")
    handles, labels = axes[0][0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="outside upper right", ncol=len(labels), frameon=False,
               fontsize=9)
    fig.suptitle(TITLES[operation], fontsize=12, x=0.01, ha="left", color="#191919")
    out = results_dir / f"{operation}.png"
    fig.savefig(out, dpi=140)
    plt.close(fig)
    return out
