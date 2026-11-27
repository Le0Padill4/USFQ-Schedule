"""Diferencial del motor completo (I1 + I2 + I3): >= 10.000 operaciones aleatorias.

Dos mundos reciben exactamente la misma secuencia de operaciones:

* rapido: ``CourseGraph`` (I1), ``CourseIndex`` AVL (I2), adaptador de elegibilidad,
  motor de horarios de I3 (``best_schedules`` / ``generate_schedules``);
* lento: ``ListGraph`` (I1), ``SlowCourseIndex`` (I2), elegibilidad por listas y
  ``reference_schedules`` (I3), cada uno escrito por su duenio sin compartir algoritmos.

Se compara el resultado (o el codigo de error) de cada operacion, incluidas las que usan
codigos inexistentes o invalidos, y tras cada paso se comprueban los invariantes de las
estructuras rapidas. Todo el catalogo es sintetico.
"""

from __future__ import annotations

import random
import unittest
from collections import Counter
from dataclasses import replace

from domain.scheduling import (
    EligibleCourse,
    Meeting,
    Offering,
    ScheduleError,
    best_schedules,
    generate_schedules,
)
from domain.scheduling.reference import reference_schedules
from synthetic.requests import INVALID_KINDS, _make_invalid, _rand_meeting

try:  # piezas de I1/I2 que pueden faltar segun la rama (grafo en main; indice AVL en integracion)
    from domain.curriculum_graph import CourseGraph, GraphError
    from i1_graph_reference import ListGraph
    from domain.course_index.course_index import CourseIndex
    from domain.integration.eligibility import eligible_course_records
    from reference.course_index_slow import SlowCourseIndex

    MISSING = None
except ImportError as exc:  # pragma: no cover - depende de la rama
    MISSING = str(exc)

STEPS = 10_000
POOL = [f"SYN{i:03d}" for i in range(24)]
BAD_CODES = ["", " SYN001", "SYN001 ", 7, None]
TERM = "SYN-TERM"


def make_record(rng: random.Random, code: str, counter: list[int]) -> EligibleCourse:
    offerings = []
    for section in range(rng.randint(1, 3)):
        meetings, used = [], set()
        for _ in range(rng.randint(1, 2)):
            m = _rand_meeting(rng)
            if m.day not in used:
                used.add(m.day)
                meetings.append(m)
        counter[0] += 1
        offerings.append(
            Offering(TERM, str(20000 + counter[0]), code, str(section + 1), "Docente sintetico",
                     tuple(sorted(meetings)), "sintetico", "2026-01-01T00:00:00Z")
        )
    return EligibleCourse(code, rng.randint(1, 5), tuple(offerings))


def pick(rng: random.Random, bad: float = 0.04):
    """Codigo del pool (a veces inexistente en la estructura) o, raramente, invalido."""
    if rng.random() < bad:
        return rng.choice(BAD_CODES)
    return rng.choice(POOL) if rng.random() < 0.9 else f"NOEXISTE{rng.randrange(5)}"


def outcome(fn):
    """('ok', valor) o ('error', clase, codigo) con el mismo formato en ambos mundos."""
    try:
        return ("ok", fn())
    except (GraphError, ListGraph.Error) as e:
        return ("graph-error", e.code)
    except ScheduleError as e:
        return ("schedule-error", e.code)
    except (KeyError, ValueError, TypeError) as e:
        return ("error", type(e).__name__)


def request_from(rng: random.Random, eligible: list[EligibleCourse]):
    from domain.scheduling import Constraints, Preferences, ScheduleRequest

    pool = [e.course_code for e in eligible]
    rng.shuffle(pool)
    n_req = min(len(pool), rng.randint(0, 3))
    required = tuple(pool[:n_req])
    optional = tuple((c, rng.randint(1, 5)) for c in pool[n_req:n_req + rng.randint(0, 2)])
    by_code = {e.course_code: e for e in eligible}
    pinned = tuple(
        (c, rng.choice(by_code[c].offerings).nrc)
        for c in required + tuple(c for c, _ in optional)
        if rng.random() < 0.15
    )
    max_credits = rng.choice((None, None, 8, 12, 16))
    min_credits = rng.choice((0, 0, 3, 5))
    if max_credits is not None and min_credits > max_credits:
        min_credits = 0
    prefs = Preferences(
        free_day=rng.choice((None, None, 4)),
        minimize_days=rng.random() < 0.5,
        minimize_gaps=rng.random() < 0.5,
        preferred_ranges=tuple(_rand_meeting(rng) for _ in range(rng.choice((0, 1)))),
        avoided_ranges=tuple(_rand_meeting(rng) for _ in range(rng.choice((0, 1)))),
    )
    if rng.random() < 0.5:
        prefs = replace(prefs, **{n: rng.randint(-5, 15) for n in (
            "w_free_day", "w_days", "w_gaps", "w_preferred", "w_avoided", "w_priority")})
    req = ScheduleRequest(
        term=TERM, career_id=rng.choice(("1CMP", "1MAC")), required_courses=required,
        optional_courses=optional, pinned=pinned,
        constraints=Constraints(max_credits=max_credits, min_credits=min_credits,
                                blocked_days=frozenset(d for d in range(5) if rng.random() < 0.05)),
        preferences=prefs, max_results=rng.randint(1, 6),
    )
    return req


@unittest.skipIf(MISSING, f"requiere main actualizado e indice AVL de I2 (rama de integracion): {MISSING}")
class FullEngineDifferentialTests(unittest.TestCase):
    def run_sequence(self, seed: int, steps: int) -> Counter:
        rng = random.Random(seed)
        counter = [0]
        graph, index = CourseGraph(), CourseIndex()
        lgraph, lindex = ListGraph(), SlowCourseIndex()
        passed: list = []
        stats: Counter = Counter()

        def compare(name, fast, slow, step):
            a, b = outcome(fast), outcome(slow)
            self.assertEqual(a, b, f"paso {step}: {name}")
            stats[f"{name}:{a[0]}" + (f":{a[1]}" if a[0] != "ok" else "")] += 1
            return a

        for step in range(steps):
            op = rng.choices(
                ("add_both", "graph_add", "index_add", "remove_both", "graph_remove",
                 "index_remove", "add_prereq", "remove_prereq", "set_known", "pass", "unpass",
                 "graph_eligible", "index_get", "index_range", "query"),
                weights=(12, 2, 2, 8, 2, 2, 10, 5, 6, 8, 3, 4, 4, 3, 25),
            )[0]
            if op in ("add_both", "graph_add"):
                code = pick(rng)
                known = rng.choice((True,) * 6 + (False, 1))  # 1 -> INVALID_FLAG
                compare("graph_add", lambda: graph.add_course(code, prerequisites_known=known),
                        lambda: lgraph.add_course(code, prerequisites_known=known), step)
            if op in ("add_both", "index_add"):
                code = code if op == "add_both" else pick(rng)
                rec = make_record(rng, code, counter) if isinstance(code, str) and code else 0
                compare("index_add", lambda: index.add(code, rec), lambda: lindex.add(code, rec), step)
            elif op in ("remove_both", "graph_remove"):
                code = pick(rng)
                compare("graph_remove", lambda: graph.remove_course(code),
                        lambda: lgraph.remove_course(code), step)
            if op in ("remove_both", "index_remove"):
                code = code if op == "remove_both" else pick(rng)
                compare("index_remove", lambda: index.remove(code), lambda: lindex.remove(code), step)
            elif op == "add_prereq":
                a, b = pick(rng), pick(rng)
                compare("add_prereq", lambda: graph.add_prerequisite(a, b),
                        lambda: lgraph.add_prerequisite(a, b), step)
            elif op == "remove_prereq":
                a, b = pick(rng), pick(rng)
                compare("remove_prereq", lambda: graph.remove_prerequisite(a, b),
                        lambda: lgraph.remove_prerequisite(a, b), step)
            elif op == "set_known":
                code, flag = pick(rng), rng.choice((True, False, False, "si"))
                compare("set_known", lambda: graph.set_rules_known(code, flag),
                        lambda: lgraph.set_rules_known(code, flag), step)
            elif op == "pass":
                code = rng.choice(lgraph.nodes) if lgraph.nodes and rng.random() < 0.93 else pick(rng, 0.1)
                if code not in passed:
                    passed.append(code)
            elif op == "unpass" and passed:
                passed.remove(rng.choice(passed))
            elif op == "graph_eligible":
                pl = self.passed_view(rng, lgraph, passed)
                compare("graph_eligible", lambda: graph.eligible_courses(pl),
                        lambda: lgraph.eligible_courses(pl), step)
            elif op == "index_get":
                code = pick(rng)
                compare("index_get", lambda: index.get(code), lambda: lindex.get(code), step)
            elif op == "index_range":
                lo, hi = pick(rng, 0.02), pick(rng, 0.02)
                compare("index_range", lambda: list(index.range_items(lo, hi)),
                        lambda: list(lindex.range_items(lo, hi)), step)
            elif op == "query":
                self.run_query(rng, graph, index, lgraph, lindex, passed, compare, stats, step)

            graph.check_invariants()
            index.assert_valid()
            self.assertEqual(graph.snapshot(), lgraph.snapshot(), f"paso {step}: grafo")
            self.assertEqual(len(index), len(lindex), f"paso {step}: indice")
            if step % 500 == 0:
                self.assertEqual(list(index.range_items("A", "~")), list(lindex.range_items("A", "~")))
        return stats

    @staticmethod
    def passed_view(rng, lgraph, passed):
        """Aprobadas que se envian: casi siempre existentes; a veces con codigos obsoletos."""
        if rng.random() < 0.9:
            return [c for c in passed if c in lgraph.nodes]
        return list(passed)

    def run_query(self, rng, graph, index, lgraph, lindex, passed, compare, stats, step):
        pl = self.passed_view(rng, lgraph, passed)

        def fast_records():
            return eligible_course_records(graph, index, pl)

        def slow_records():
            return tuple((c, lindex.get(c)) for c in lgraph.eligible_courses(pl))

        got = compare("elegibles", fast_records, slow_records, step)
        if got[0] != "ok":
            return
        eligible = [rec for _, rec in got[1]]
        stats["consultas_con_elegibles"] += bool(eligible)
        stats["consultas_con_2+_elegibles"] += len(eligible) >= 2
        req = request_from(rng, eligible)
        if rng.random() < 0.15:
            req, eligible = _make_invalid(rng, req, eligible)
        method = rng.choice(("branch_and_bound", "todos_topk"))
        generator = rng.choice(("exhaustive", "backtracking", "csp"))
        selector = rng.choice(("heap", "sort"))
        slow = outcome(lambda: reference_schedules(req, eligible))
        for name, fn in (
            (f"horarios[{method}]", lambda: best_schedules(req, eligible, method=method)),
            (f"horarios[{generator}+{selector}]",
             lambda: generate_schedules(req, eligible, generator=generator, selector=selector)),
        ):
            self.assertEqual(outcome(fn), slow, f"paso {step}: {name}")
        stats[f"horarios:{slow[0]}" + (f":{slow[1]}" if slow[0] != "ok" else "")] += 1
        if slow[0] == "ok" and slow[1]:
            stats["horarios_no_vacios"] += 1

    def test_ten_thousand_random_operations(self):
        stats = self.run_sequence(seed=20261127, steps=STEPS)
        print("\ncobertura diferencial motor completo:", dict(sorted(stats.items())))
        # La prueba no puede ser vacua: debe ejercitar exitos, errores y horarios reales.
        self.assertGreaterEqual(stats["consultas_con_2+_elegibles"], 100)
        self.assertGreaterEqual(stats["horarios_no_vacios"], 100)
        for key in ("graph_add:graph-error:DUPLICATE_COURSE", "graph_add:graph-error:INVALID_CODE",
                    "add_prereq:graph-error:CYCLE", "add_prereq:graph-error:UNKNOWN_COURSE",
                    "index_add:error:ValueError", "index_get:error:KeyError",
                    "elegibles:error:KeyError", "elegibles:graph-error:UNKNOWN_COURSE"):
            self.assertGreater(stats[key], 0, key)
        self.assertGreater(sum(v for k, v in stats.items() if k.startswith("horarios:schedule-error")), 20)

    def test_other_seeds_shorter(self):
        for seed in (1, 2, 3):
            self.run_sequence(seed=seed, steps=1500)


if __name__ == "__main__":
    unittest.main()
