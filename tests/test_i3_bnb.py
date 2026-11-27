"""Mejores K horarios: branch and bound frente a generar-todos y a la referencia lenta."""
import random
import unittest

from benchmarks.bench_generation import build_instance
from domain.scheduling import (
    METHODS,
    Meeting,
    Preferences,
    ScheduleRequest,
    Stats,
    best_schedules,
    best_schedules_all,
    best_schedules_bnb,
    build_problem,
    score_upper_bound,
)
from domain.scheduling.reference import reference_generate, reference_schedules
from synthetic import CatalogParams, eligible_courses, generate_catalog, tiny_catalog
from synthetic.requests import random_request

STRONG = Preferences(
    free_day=4,
    minimize_days=True,
    preferred_ranges=(Meeting(0, 540, 720), Meeting(2, 540, 720)),
    avoided_ranges=(Meeting(1, 420, 540),),
    w_free_day=100, w_days=10, w_preferred=2, w_avoided=3,
)


class HandTests(unittest.TestCase):
    def test_tiny_k1_dia_libre(self):
        el = eligible_courses(tiny_catalog(), "1CMP", set())
        req = ScheduleRequest("SYN-T1", "1CMP", ("SYN-G1", "SYN-S1"),
                              preferences=Preferences(free_day=1), max_results=1)
        for method in METHODS:
            with self.subTest(method=method):
                got = best_schedules(req, el, method=method)
                self.assertEqual([r.nrcs for r in got], [("1001", "2001")])
                self.assertEqual(got[0].score, 100)

    def test_sin_cursos_o_sin_factibles(self):
        el = eligible_courses(tiny_catalog(), "1CMP", set())
        for req in (
            ScheduleRequest("SYN-T1", "1CMP"),
            ScheduleRequest("SYN-T1", "1CMP", ("SYN-G1", "SYN-S1"),
                            pinned=(("SYN-G1", "1001"), ("SYN-S1", "2002"))),  # cruzan
        ):
            for method in METHODS:
                self.assertEqual(best_schedules(req, el, method=method), [])


class DifferentialTests(unittest.TestCase):
    def test_contra_referencia_con_pesos_arbitrarios(self):
        compared = 0
        for seed in range(4):
            cat = generate_catalog(CatalogParams(seed=seed))
            for i in range(150):
                req, el = random_request(random.Random(f"bnb-{seed}-{i}"), cat)
                ref = reference_schedules(req, el)
                for method in METHODS:
                    with self.subTest(seed=seed, i=i, method=method):
                        self.assertEqual(best_schedules(req, el, method=method), ref)
                compared += len(ref)
        self.assertGreater(compared, 300)

    def test_cota_valida_en_cada_nodo(self):
        """Ninguna cota calculada por el B&B es menor que el mejor puntaje de sus completaciones."""
        checked = 0
        for seed in range(3):
            cat = generate_catalog(CatalogParams(seed=seed, sections=(1, 3)))
            for i in range(60):
                req, el = random_request(random.Random(f"aud-{seed}-{i}"), cat)
                problem = build_problem(req, el)
                full = reference_generate(req, el)
                if not full:
                    continue
                from domain.scheduling import score_schedule

                scores = {s: score_schedule(s, problem).score for s in full}
                slot_nrcs = [{o.nrc for o in s.options} for s in problem.slots]
                audit: list = []
                best_schedules_bnb(problem, _audit=audit)
                for prefix, depth, b in audit:
                    inside = set().union(*slot_nrcs[:depth]) if depth else set()
                    completions = [sc for s, sc in scores.items()
                                   if {x for x in s if x in inside} == set(prefix)]
                    if completions:
                        checked += 1
                        self.assertGreaterEqual(b, max(completions), (seed, i, prefix))
                self.assertGreaterEqual(score_upper_bound(problem), max(scores.values()))
        self.assertGreater(checked, 500)


class PruningTests(unittest.TestCase):
    def test_con_preferencias_fuertes_poda_y_visita_menos_nodos(self):
        problem = build_instance(5, 110, 1, STRONG, 10)
        a, b = Stats(), Stats()
        self.assertEqual(best_schedules_all(problem, a), best_schedules_bnb(problem, b))
        self.assertGreater(b.pruned, 0)
        self.assertLess(b.nodes, a.nodes)

    def test_sin_preferencias_todo_empata_y_no_poda(self):
        problem = build_instance(4, 110, 1, None, 10)
        a, b = Stats(), Stats()
        self.assertEqual(best_schedules_all(problem, a), best_schedules_bnb(problem, b))
        self.assertEqual(b.pruned, 0)  # con empate no se poda (el desempate por NRC cuenta)

    def test_k_mayor_que_los_factibles_no_poda(self):
        problem = build_instance(3, 110, 1, STRONG, 10**6)
        b = Stats()
        got = best_schedules_bnb(problem, b)
        self.assertEqual(got, best_schedules_all(problem))
        self.assertEqual(b.pruned, 0)


if __name__ == "__main__":
    unittest.main()
