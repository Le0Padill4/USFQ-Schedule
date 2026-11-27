"""Diferencial: referencia lenta frente a candidatos (generacion, puntaje, Top-K, errores).

La comparacion de 10.000 operaciones sobre el motor completo es una tarea posterior (T10);
esta es la base: solicitudes aleatorias reproducibles, validas e invalidas.
"""
import random
import unittest

from domain.scheduling import (
    ScheduleError,
    build_problem,
    generate_backtracking,
    generate_exhaustive,
    generate_schedules,
)
from domain.scheduling.reference import reference_generate, reference_schedules
from synthetic import CatalogParams, generate_catalog
from synthetic.requests import random_request


def outcome(fn, *args):
    try:
        return ("ok", fn(*args))
    except ScheduleError as exc:
        return ("err", exc.code)


class DifferentialTests(unittest.TestCase):
    def test_validas(self):
        total = 0
        for seed in range(4):
            cat = generate_catalog(CatalogParams(seed=seed, sections=(1, 3)))
            for i in range(120):
                rng = random.Random(f"{seed}-{i}")
                request, eligible = random_request(rng, cat)
                with self.subTest(seed=seed, i=i):
                    ref = reference_generate(request, eligible)
                    problem = build_problem(request, eligible)
                    self.assertEqual(generate_exhaustive(problem), ref)
                    self.assertEqual(generate_backtracking(problem), ref)
                    expected = reference_schedules(request, eligible)
                    for g in ("exhaustive", "backtracking"):
                        for s in ("heap", "sort"):
                            self.assertEqual(
                                generate_schedules(request, eligible, generator=g, selector=s),
                                expected,
                            )
                    total += len(ref)
        self.assertGreater(total, 100)  # el diferencial no es trivialmente vacio

    def test_invalidas_mismo_codigo_de_error(self):
        errores = 0
        cat = generate_catalog(CatalogParams(seed=9))
        for i in range(500):
            request, eligible = random_request(random.Random(f"inv-{i}"), cat, invalid_prob=1.0)
            with self.subTest(i=i):
                ref = outcome(reference_generate, request, eligible)
                new = outcome(generate_schedules, request, eligible)
                self.assertEqual(ref[0], new[0])
                if ref[0] == "err":
                    errores += 1
                    self.assertEqual(ref[1], new[1])
        self.assertGreater(errores, 300)


if __name__ == "__main__":
    unittest.main()
