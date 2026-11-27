"""Humo del arnes de benchmarks con tamanos minimos (no mide rendimiento)."""
import csv
import tempfile
import unittest
from pathlib import Path

from benchmarks import bench_generation, bench_topk


def read(path):
    with Path(path).open(newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


class BenchmarkHarnessTests(unittest.TestCase):
    def test_generacion_produce_csv_con_candidatos_equivalentes(self):
        with tempfile.TemporaryDirectory() as tmp:
            bench_generation.run(Path(tmp), sizes={100: 2, 1000: 3}, repeats=2, seed=1)
            summary = read(Path(tmp) / "generacion_summary.csv")
            raw = read(Path(tmp) / "generacion_raw.csv")
        scenarios = {r["scenario"] for r in summary}
        self.assertEqual(scenarios, set(bench_generation.SCENARIOS))
        self.assertEqual({r["candidate"] for r in summary}, set(bench_generation.CANDIDATES))
        self.assertEqual(len(summary), 3 * 2 * 3)  # escenarios x tamanos x candidatos
        self.assertEqual(len(raw), len(summary) * 2)  # una fila por repeticion
        by_key = {}
        for r in summary:
            by_key.setdefault((r["scenario"], r["size"]), set()).add(r["result_count"])
        self.assertTrue(all(len(v) == 1 for v in by_key.values()))  # mismos resultados

    def test_topk_produce_csv_con_pasos_y_memoria(self):
        with tempfile.TemporaryDirectory() as tmp:
            bench_topk.run(Path(tmp), sizes=(200, 400), repeats=2, seed=1)
            summary = read(Path(tmp) / "topk_summary.csv")
        self.assertEqual(len(summary), len(bench_topk.SCENARIOS) * 2 * 2)
        self.assertTrue(all(float(r["time_ms_median"]) > 0 for r in summary))
        self.assertTrue(all(int(r["comparisons"]) > 0 for r in summary))
        self.assertTrue(all(float(r["peak_kib"]) > 0 for r in summary))

    def test_los_datos_son_reproducibles(self):
        a = bench_topk.make_data(50, "k10_aleatorio", 7)
        self.assertEqual(a, bench_topk.make_data(50, "k10_aleatorio", 7))
        self.assertNotEqual(a, bench_topk.make_data(50, "k10_aleatorio", 8))

    def test_grafico_si_hay_matplotlib(self):
        try:
            import matplotlib  # noqa: F401
        except ImportError:
            self.skipTest("matplotlib no instalado")
        from benchmarks.plot import plot_operation

        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            bench_generation.run(out, sizes={100: 2, 1000: 3}, repeats=1, seed=1)
            bench_topk.run(out, sizes=(200, 400), repeats=1, seed=1)
            for op in ("generacion", "topk"):
                self.assertTrue(plot_operation(op, out).stat().st_size > 1000)


if __name__ == "__main__":
    unittest.main()
