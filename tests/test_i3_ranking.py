"""Puntaje, orden y Top-K (heap propio frente a ordenamiento completo)."""
import random
import unittest

from domain.scheduling import (
    BoundedHeap,
    EligibleCourse,
    ErrorCode,
    Meeting,
    Offering,
    Preferences,
    ScheduleError,
    ScheduleRequest,
    ScheduleResult,
    Stats,
    build_problem,
    generate_schedules,
    rank_key,
    score_schedule,
    top_k_heap,
    top_k_sort,
)
from synthetic import eligible_courses, tiny_catalog


def req(**kw):
    kw.setdefault("term", "SYN-T1")
    kw.setdefault("career_id", "1CMP")
    kw.setdefault("required_courses", ("SYN-G1", "SYN-S1"))
    return ScheduleRequest(**kw)


def terms(result):
    return {t.name: (t.raw_value, t.weight, t.points) for t in result.explanations}


class ScoringTests(unittest.TestCase):
    def setUp(self):
        self.el = eligible_courses(tiny_catalog(), "1CMP", set())

    def score(self, nrcs, request):
        return score_schedule(nrcs, build_problem(request, self.el))

    def test_dia_libre(self):
        r = req(preferences=Preferences(free_day=1))  # martes libre
        self.assertEqual(terms(self.score(("1001", "2001"), r))["free_day"], (1, 100, 100))
        self.assertEqual(terms(self.score(("1002", "2001"), r))["free_day"], (0, 100, 0))

    def test_dias_usados(self):
        r = req(preferences=Preferences(minimize_days=True))
        s = self.score(("1001", "2001"), r)  # lunes y miercoles
        self.assertEqual(terms(s)["days_used"], (2, -10, -20))
        self.assertEqual(s.score, -20)

    def test_franja_preferida(self):
        r = req(preferences=Preferences(preferred_ranges=(Meeting(0, 540, 600),)))
        # 2001 (lunes 540-600) cae entero dentro; 1001 (480-540) solo toca el borde: 0 min.
        self.assertEqual(terms(self.score(("1001", "2001"), r))["preferred_minutes"], (60, 2, 120))

    def test_franja_evitada(self):
        r = req(preferences=Preferences(avoided_ranges=(Meeting(0, 480, 510),)))
        self.assertEqual(terms(self.score(("1001", "2001"), r))["avoided_minutes"], (30, -3, -90))

    def test_prioridad_de_opcionales(self):
        r = req(required_courses=("SYN-G1",), optional_courses=(("SYN-S1", 3),))
        self.assertEqual(terms(self.score(("1001", "2001"), r))["optional_priority"], (3, 10, 30))
        self.assertEqual(terms(self.score(("1001",), r))["optional_priority"], (0, 10, 0))

    def test_horas_libres(self):
        def off(nrc, code, *m):
            return Offering("SYN-T1", nrc, code, "1", "d", tuple(Meeting(*x) for x in m), "s", "r")

        el = [
            EligibleCourse("SYN-A", 3, (off("A1", "SYN-A", (0, 480, 540), (2, 480, 540)),)),
            EligibleCourse("SYN-B", 3, (off("B1", "SYN-B", (0, 600, 660)),)),
        ]
        r = ScheduleRequest("SYN-T1", "1CMP", ("SYN-A", "SYN-B"),
                            preferences=Preferences(minimize_gaps=True, w_gaps=2))
        s = score_schedule(("A1", "B1"), build_problem(r, el))
        self.assertEqual(terms(s)["gap_minutes"], (60, -2, -120))  # lunes 540 a 600

    def test_explicacion_suma_el_puntaje(self):
        r = req(preferences=Preferences(free_day=4, minimize_days=True, minimize_gaps=True,
                                        preferred_ranges=(Meeting(1, 480, 600),)))
        for result in generate_schedules(r, self.el):
            self.assertEqual(result.score, sum(t.points for t in result.explanations))

    def test_terminos_fijos_y_pesos_inactivos(self):
        s = self.score(("1001", "2001"), req())
        self.assertEqual([t.name for t in s.explanations],
                         ["free_day", "days_used", "gap_minutes", "preferred_minutes",
                          "avoided_minutes", "optional_priority"])
        self.assertEqual(s.score, 0)

    def test_orden_con_desempate_lexicografico(self):
        r = req(preferences=Preferences(free_day=1))
        got = [x.nrcs for x in generate_schedules(r, self.el)]
        # (1001,2001) deja martes libre (+100); los otros dos empatan en 0 -> orden por NRC.
        self.assertEqual(got, [("1001", "2001"), ("1002", "2001"), ("1002", "2002")])

    def test_max_results_recorta(self):
        r = req(preferences=Preferences(free_day=1), max_results=2)
        self.assertEqual([x.nrcs for x in generate_schedules(r, self.el)],
                         [("1001", "2001"), ("1002", "2001")])

    def test_los_cuatro_pipelines_coinciden(self):
        r = req(preferences=Preferences(free_day=1, minimize_days=True))
        outs = [generate_schedules(r, self.el, generator=g, selector=s)
                for g in ("exhaustive", "backtracking") for s in ("heap", "sort")]
        self.assertTrue(all(o == outs[0] for o in outs))


def make_results(rng, n, score_range=5):
    """Resultados sinteticos con muchos empates de puntaje (NRC distintos)."""
    return [ScheduleResult((f"{rng.randrange(10**6):06d}", f"{i:04d}"), rng.randint(-score_range, score_range), ())
            for i in range(n)]


class TopKTests(unittest.TestCase):
    def test_heap_igual_a_ordenamiento_en_aleatorios(self):
        rng = random.Random(77)
        for trial in range(300):
            n, k = rng.randint(0, 60), rng.randint(1, 70)
            data = make_results(rng, n)
            rng.shuffle(data)
            with self.subTest(trial=trial, n=n, k=k):
                self.assertEqual(top_k_heap(data, k), top_k_sort(data, k))
                self.assertEqual(top_k_heap(data, k), sorted(data, key=rank_key)[:k])

    def test_invariante_tras_cada_insercion(self):
        rng = random.Random(5)
        heap = BoundedHeap(7)
        for item in make_results(rng, 200):
            heap.offer(item)
            heap.check_invariants()
        self.assertEqual(len(heap), 7)

    def test_k_mayor_que_n_devuelve_todo_y_k_uno(self):
        data = make_results(random.Random(1), 5)
        self.assertEqual(top_k_heap(data, 99), sorted(data, key=rank_key))
        self.assertEqual(top_k_heap(data, 1), sorted(data, key=rank_key)[:1])

    def test_vacio(self):
        self.assertEqual(top_k_heap([], 3), [])
        self.assertEqual(top_k_sort([], 3), [])

    def test_k_invalido(self):
        for k in (0, -1, 1.5, True, None):
            for fn in (top_k_heap, top_k_sort):
                with self.subTest(k=k, fn=fn.__name__):
                    with self.assertRaises(ScheduleError) as cm:
                        fn([], k)
                    self.assertIs(cm.exception.code, ErrorCode.INVALID_RANGE)

    def test_best_first_no_destruye_el_heap(self):
        heap = BoundedHeap(3)
        for item in make_results(random.Random(2), 10):
            heap.offer(item)
        first, second = heap.best_first(), heap.best_first()
        self.assertEqual(first, second)
        heap.check_invariants()

    def test_heap_usa_menos_comparaciones_con_k_pequeno(self):
        data = make_results(random.Random(3), 3000)
        h, s = Stats(), Stats()
        self.assertEqual(top_k_heap(data, 5, h), top_k_sort(data, 5, s))
        self.assertLess(h.comparisons, s.comparisons)


if __name__ == "__main__":
    unittest.main()
