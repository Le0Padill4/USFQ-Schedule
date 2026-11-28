"""Compare ordered-range workloads with an AVL map and a sorted Python list."""
import bisect
import csv
import math
import platform
import random
import statistics
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from domain.course_index.avl import CourseAVL  # noqa: E402

OUT = Path(__file__).resolve().parent
SIZES = (1000, 5000, 10000, 50000)
SCENARIOS = (("consultas_90", 360), ("consultas_10", 40))
REPEATS = 3
OPERATIONS = 400
SEED = 20261125


def workload(size, queries):
    rng = random.Random(SEED + size + queries)
    updates = rng.sample(range(size), OPERATIONS - queries)
    operations = [("insert", 2 * x + 1, 0) for x in updates]
    for _ in range(queries):
        start = rng.randrange(size * 2)
        operations.append(("range", start, start + 20))
    rng.shuffle(operations)
    return operations


def run(size, operations, candidate):
    keys = list(range(0, size * 2, 2))
    if candidate == "avl":
        index = CourseAVL()
        for key in keys:
            index.put(key, key)
    else:
        index = keys
    start = time.perf_counter_ns()
    results = []
    for kind, low, high in operations:
        if kind == "insert":
            if candidate == "avl":
                index.put(low, low)
            else:
                bisect.insort(index, low)
        elif candidate == "avl":
            results.append(tuple(key for key, _ in index.range_items(low, high)))
        else:
            left = bisect.bisect_left(index, low)
            right = bisect.bisect_right(index, high)
            results.append(tuple(index[left:right]))
    elapsed = time.perf_counter_ns() - start
    if candidate == "avl":
        index.assert_valid()
    return elapsed, results


def svg(rows):
    width, height = 940, 390
    panels = []
    colors = {"avl": "#1565c0", "lista_ordenada": "#c54d16"}
    panels.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">')
    panels.append('<rect width="100%" height="100%" fill="white"/>')
    panels.append('<text x="30" y="28" font-family="sans-serif" font-size="17">Rangos e inserciones: mediana del lote (ms; escala logarítmica)</text>')
    for panel, (scenario, _) in enumerate(SCENARIOS):
        x0, y0, w, h = 60 + panel * 450, 75, 360, 240
        subset = [row for row in rows if row["escenario"] == scenario]
        vals = [float(row["mediana_ms"]) for row in subset]
        ymin, ymax = math.log10(min(vals)) - 0.2, math.log10(max(vals)) + 0.2
        panels.append(f'<text x="{x0}" y="60" font-family="sans-serif" font-size="13">{scenario}</text>')
        panels.append(f'<path d="M{x0},{y0} V{y0+h} H{x0+w}" fill="none" stroke="#333"/>')
        for j in range(4):
            exponent = ymin + (ymax-ymin) * j / 3
            y = y0+h - h*j/3
            panels.append(f'<text x="{x0-8}" y="{y+4:.1f}" text-anchor="end" font-family="sans-serif" font-size="10">{10**exponent:.2f}</text>')
        for i, n in enumerate(SIZES):
            x = x0 + i*w/3
            panels.append(f'<text x="{x:.1f}" y="{y0+h+18}" text-anchor="middle" font-family="sans-serif" font-size="10">{n}</text>')
        for candidate, color in colors.items():
            values = [float(row["mediana_ms"]) for row in subset if row["candidato"] == candidate]
            points = []
            for i, v in enumerate(values):
                x = x0 + i*w/3
                y = y0+h - h*(math.log10(v)-ymin)/(ymax-ymin)
                points.append(f'{x:.1f},{y:.1f}')
            panels.append(f'<polyline points="{" ".join(points)}" fill="none" stroke="{color}" stroke-width="2"/>')
        panels.append(f'<text x="{x0+110}" y="{y0+h+42}" font-family="sans-serif" font-size="11">n inicial</text>')
    panels.append('<text x="80" y="375" font-family="sans-serif" font-size="12" fill="#1565c0">Azul: AVL</text>')
    panels.append('<text x="210" y="375" font-family="sans-serif" font-size="12" fill="#c54d16">Naranja: lista ordenada</text></svg>')
    return "\n".join(panels)


def main():
    rows = []
    for scenario, queries in SCENARIOS:
        for size in SIZES:
            ops = workload(size, queries)
            times = {"avl": [], "lista_ordenada": []}
            outputs = []
            # Alternate measurement order to reduce systematic order effects.
            for repeat in range(REPEATS):
                order = list(times)
                if repeat % 2:
                    order.reverse()
                for candidate in order:
                    elapsed, result = run(size, ops, candidate)
                    times[candidate].append(elapsed / 1e6)
                    outputs.append(result)
            if any(result != outputs[0] for result in outputs[1:]):
                raise AssertionError("candidate results differ")
            checksum = sum(sum(result) for result in outputs[0])
            for candidate, values in times.items():
                rows.append({"escenario": scenario, "n": size, "candidato": candidate,
                             "operaciones": OPERATIONS, "consultas": queries,
                             "repeticiones": REPEATS, "mediana_ms": f"{statistics.median(values):.4f}",
                             "checksum": checksum})
    with (OUT / "resultados.csv").open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    (OUT / "rangos.svg").write_text(svg(rows), encoding="utf-8")
    (OUT / "entorno.txt").write_text(f"Python {platform.python_version()}\n{platform.system()} {platform.machine()}\nSemilla {SEED}; {REPEATS} repeticiones por punto.\n", encoding="utf-8")
    print(f"Escritos {len(rows)} resultados; todas las respuestas por rango coinciden.")


if __name__ == '__main__':
    main()
