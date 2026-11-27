"""Generacion de horarios: casos hechos a mano sobre tiny_catalog y errores tipados."""
import unittest

from domain.scheduling import (
    Constraints,
    EligibleCourse,
    ErrorCode,
    Meeting,
    Offering,
    ScheduleError,
    ScheduleRequest,
    Stats,
    build_problem,
    generate_backtracking,
    generate_exhaustive,
)
from synthetic import CatalogParams, eligible_courses, generate_catalog, tiny_catalog

CANDIDATES = {"exhaustive": generate_exhaustive, "backtracking": generate_backtracking}


def req(**kw):
    kw.setdefault("term", "SYN-T1")
    kw.setdefault("career_id", "1CMP")
    return ScheduleRequest(**kw)


class GenerationCase(unittest.TestCase):
    def setUp(self):
        # Habilitadas sin aprobadas en 1CMP: SYN-G1 (1001, 1002) y SYN-S1 (2001, 2002).
        self.eligible = eligible_courses(tiny_catalog(), "1CMP", set())

    def run_all(self, request, eligible=None):
        """Ejecuta ambos candidatos y exige resultados identicos."""
        problem = build_problem(request, eligible if eligible is not None else self.eligible)
        results = {name: fn(problem) for name, fn in CANDIDATES.items()}
        self.assertEqual(results["exhaustive"], results["backtracking"])
        return results["exhaustive"]

    def assertCode(self, code, request, eligible=None):
        with self.assertRaises(ScheduleError) as cm:
            build_problem(request, eligible if eligible is not None else self.eligible)
        self.assertIs(cm.exception.code, code)


class HandDerivedTests(GenerationCase):
    def test_pares_factibles(self):
        # (1001,2001) consecutivas OK; (1001,2002) cruce lunes; (1002,*) martes vs lunes OK.
        got = self.run_all(req(required_courses=("SYN-G1", "SYN-S1")))
        self.assertEqual(got, [("1001", "2001"), ("1002", "2001"), ("1002", "2002")])

    def test_materia_opcional(self):
        got = self.run_all(req(required_courses=("SYN-G1",), optional_courses=(("SYN-S1", 3),)))
        self.assertEqual(
            got,
            [("1001",), ("1001", "2001"), ("1002",), ("1002", "2001"), ("1002", "2002")],
        )

    def test_paralelo_fijado(self):
        got = self.run_all(
            req(required_courses=("SYN-G1", "SYN-S1"), pinned=(("SYN-S1", "2002"),))
        )
        self.assertEqual(got, [("1002", "2002")])

    def test_dia_bloqueado(self):
        got = self.run_all(
            req(
                required_courses=("SYN-G1", "SYN-S1"),
                constraints=Constraints(blocked_days=frozenset({1})),  # sin martes
            )
        )
        self.assertEqual(got, [("1001", "2001")])

    def test_franja_bloqueada(self):
        got = self.run_all(
            req(
                required_courses=("SYN-G1", "SYN-S1"),
                constraints=Constraints(blocked_ranges=(Meeting(0, 500, 520),)),
            )
        )
        # Lunes 500-520 elimina 1001 (480-540) y 2002 (500-560); 2001 (540-600) sigue.
        self.assertEqual(got, [("1002", "2001")])

    def test_creditos(self):
        # G1 = 3 creditos, S1 = 4: total 7.
        base = {"required_courses": ("SYN-G1", "SYN-S1")}
        self.assertEqual(self.run_all(req(**base, constraints=Constraints(max_credits=6))), [])
        self.assertEqual(len(self.run_all(req(**base, constraints=Constraints(max_credits=7)))), 3)
        self.assertEqual(self.run_all(req(**base, constraints=Constraints(min_credits=8))), [])

    def test_solicitud_vacia(self):
        self.assertEqual(self.run_all(req()), [])

    def test_materia_sin_ofertas(self):
        sin = [EligibleCourse("SYN-X1", 3, ())]
        self.assertEqual(self.run_all(req(required_courses=("SYN-X1",)), sin), [])
        # Solo opcional sin ofertas: la seleccion vacia no cuenta como horario.
        self.assertEqual(self.run_all(req(optional_courses=(("SYN-X1", 1),)), sin), [])

    def test_sin_cruces_en_resultados(self):
        offs = {o.nrc: o for e in self.eligible for o in e.offerings}
        from domain.scheduling import offerings_conflict

        for combo in self.run_all(req(required_courses=("SYN-G1", "SYN-S1"))):
            for i, a in enumerate(combo):
                for b in combo[i + 1:]:
                    self.assertFalse(offerings_conflict(offs[a], offs[b]))


class ErrorTests(GenerationCase):
    def test_codigos(self):
        cases = [
            (ErrorCode.CAREER_NOT_SUPPORTED, req(career_id="1XXX")),
            (ErrorCode.INVALID_RANGE, req(max_results=0)),
            (ErrorCode.INVALID_RANGE, req(max_results=True)),
            (ErrorCode.NOT_ELIGIBLE, req(required_courses=("SYN-C1",))),  # no habilitada
            (ErrorCode.NOT_ELIGIBLE, req(required_courses=("NO-EXISTE",))),
            (ErrorCode.INVALID_RANGE, req(required_courses=("SYN-G1", "SYN-G1"))),
            (ErrorCode.INVALID_RANGE,
             req(required_courses=("SYN-G1",), optional_courses=(("SYN-G1", 1),))),
            (ErrorCode.INVALID_RANGE,
             req(optional_courses=(("SYN-S1", 0),))),
            (ErrorCode.UNKNOWN_NRC,
             req(required_courses=("SYN-G1",), pinned=(("SYN-G1", "9999"),))),
            (ErrorCode.UNKNOWN_NRC,  # el NRC existe, pero en otra materia
             req(required_courses=("SYN-G1",), pinned=(("SYN-G1", "2001"),))),
            (ErrorCode.NOT_ELIGIBLE,
             req(required_courses=("SYN-G1",), pinned=(("SYN-S1", "2001"),))),
            (ErrorCode.INVALID_RANGE, req(constraints=Constraints(min_credits=9, max_credits=4))),
            (ErrorCode.INVALID_RANGE, req(constraints=Constraints(blocked_days=frozenset({7})))),
            (ErrorCode.INVALID_RANGE, req(constraints=Constraints(min_credits=-1))),
        ]
        for code, request in cases:
            with self.subTest(code=code, request=request):
                self.assertCode(code, request)

    def test_nrc_duplicado(self):
        a, b = self.eligible[0], self.eligible[1]
        clon = Offering(**{**b.offerings[0].__dict__, "nrc": a.offerings[0].nrc})
        roto = [a, EligibleCourse(b.course_code, b.credits, (clon,))]
        self.assertCode(ErrorCode.DUPLICATE_NRC, req(), roto)

    def test_materia_elegible_repetida(self):
        self.assertCode(ErrorCode.INVALID_RANGE, req(), self.eligible + self.eligible[:1])


class StatsTests(unittest.TestCase):
    def test_backtracking_visita_menos_nodos_con_muchos_cruces(self):
        cat = generate_catalog(CatalogParams(seed=11, slot_pool=4, sections=(3, 3), offered_prob=1.0))
        el = eligible_courses(cat, "1CMP", set())
        courses = tuple(e.course_code for e in el[:4])
        problem = build_problem(req(required_courses=courses, max_results=5), el)
        ex, bt = Stats(), Stats()
        self.assertEqual(generate_exhaustive(problem, ex), generate_backtracking(problem, bt))
        self.assertLess(bt.nodes, ex.nodes)

    def test_contadores_no_negativos(self):
        st = Stats()
        el = eligible_courses(tiny_catalog(), "1CMP", set())
        generate_backtracking(build_problem(req(required_courses=("SYN-G1", "SYN-S1")), el), st)
        self.assertGreater(st.nodes, 0)
        self.assertGreater(st.conflict_checks, 0)


if __name__ == "__main__":
    unittest.main()
