"""Compare deletion from an AVL and a sorted list on identical synthetic keys."""
import bisect
import csv
import platform
import statistics
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from domain.course_index.avl import CourseAVL
from experimentos.i2_rangos import benchmark as plot

OUT = Path(__file__).resolve().parent
SIZES = (1000, 5000, 10000, 50000)
SCENARIOS = ('bajas_inicio', 'bajas_final')
REPEATS = 5
COUNT = 200


def run(size, scenario, candidate):
    keys = list(range(size))
    targets = list(range(COUNT)) if scenario == 'bajas_inicio' else list(range(size - 1, size - COUNT - 1, -1))
    if candidate == 'avl':
        structure = CourseAVL()
        for key in keys:
            structure.put(key, key)
    else:
        structure = keys.copy()
    start = time.perf_counter_ns()
    for key in targets:
        if candidate == 'avl':
            structure.delete(key)
        else:
            pos = bisect.bisect_left(structure, key)
            if pos == len(structure) or structure[pos] != key:
                raise KeyError(key)
            structure.pop(pos)
    elapsed = time.perf_counter_ns() - start
    if candidate == 'avl':
        structure.assert_valid()
        remaining = [key for key, _ in structure.range_items(0, size - 1)]
    else:
        remaining = structure
    expected = keys[COUNT:] if scenario == 'bajas_inicio' else keys[:-COUNT]
    if remaining != expected:
        raise AssertionError('El estado final no coincide con las bajas esperadas')
    return elapsed, remaining


def main():
    rows = []
    for scenario in SCENARIOS:
        for size in SIZES:
            times = {'avl': [], 'lista_ordenada': []}
            baseline = None
            for repeat in range(REPEATS):
                order = list(times)
                if repeat % 2:
                    order.reverse()
                for candidate in order:
                    elapsed, remaining = run(size, scenario, candidate)
                    if baseline is None:
                        baseline = remaining
                    elif baseline != remaining:
                        raise AssertionError('Los estados finales no coinciden')
                    times[candidate].append(elapsed / 1e6)
            for candidate, values in times.items():
                rows.append({'escenario': scenario, 'n': size, 'candidato': candidate,
                             'bajas': COUNT, 'repeticiones': REPEATS,
                             'mediana_ms': f'{statistics.median(values):.4f}',
                             'restantes': len(baseline)})
    with (OUT / 'resultados.csv').open('w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=list(rows[0]), lineterminator='\n')
        writer.writeheader()
        writer.writerows(rows)
    plot.SCENARIOS = tuple((name, 0) for name in SCENARIOS)
    plot.SIZES = SIZES
    drawing = plot.svg(rows).replace('Rangos e inserciones: mediana del lote', 'Bajas: mediana del lote')
    (OUT / 'bajas.svg').write_text(drawing, encoding='utf-8')
    (OUT / 'entorno.txt').write_text(f'Python {platform.python_version()}\n{platform.system()} {platform.machine()}\n{REPEATS} repeticiones por punto.\n', encoding='utf-8')
    print(f'Escritos {len(rows)} resultados; estados finales iguales e invariantes AVL válidos.')


if __name__ == '__main__':
    main()
