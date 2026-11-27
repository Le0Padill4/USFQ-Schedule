"""Pruebas de Meeting, Offering, EligibleCourse y solapes (fixtures sinteticos)."""
import random
import unittest

from domain.scheduling import (
    EligibleCourse,
    ErrorCode,
    Meeting,
    Offering,
    ScheduleError,
    meetings_overlap,
    offerings_conflict,
)


def offering(nrc, course="SYN101", meetings=((0, 480, 540),)):
    return Offering(
        term="SYN-T1", nrc=nrc, course_code=course, section="1",
        instructor_label="Docente sintetico",
        meetings=tuple(Meeting(*m) for m in meetings),
        source="fixture-sintetico", retrieved_at="2026-11-24",
    )


class ModelTestCase(unittest.TestCase):
    def assertCode(self, code, fn, *args, **kwargs):
        with self.assertRaises(ScheduleError) as cm:
            fn(*args, **kwargs)
        self.assertIs(cm.exception.code, code)


class MeetingTests(ModelTestCase):
    def test_fuera_de_rango(self):
        for args in [(-1, 0, 60), (7, 0, 60), (0, -1, 60), (0, 60, 60), (0, 90, 60), (0, 0, 1441)]:
            with self.subTest(args=args):
                self.assertCode(ErrorCode.INVALID_RANGE, Meeting, *args)

    def test_tipos_invalidos(self):
        for args in [(0.5, 0, 60), (True, 0, 60), (0, "0", 60), (0, 0, None)]:
            with self.subTest(args=args):
                self.assertCode(ErrorCode.INVALID_RANGE, Meeting, *args)

    def test_limites_validos(self):
        Meeting(0, 0, 1)
        Meeting(6, 1439, 1440)

    def test_inmutable(self):
        with self.assertRaises(AttributeError):
            Meeting(0, 0, 60).day = 1


class OverlapTests(unittest.TestCase):
    def test_clases_consecutivas_no_se_cruzan(self):
        self.assertFalse(meetings_overlap(Meeting(1, 480, 540), Meeting(1, 540, 600)))
        self.assertFalse(meetings_overlap(Meeting(1, 540, 600), Meeting(1, 480, 540)))

    def test_solape_parcial_y_contenido(self):
        self.assertTrue(meetings_overlap(Meeting(1, 480, 540), Meeting(1, 539, 600)))
        self.assertTrue(meetings_overlap(Meeting(1, 480, 600), Meeting(1, 500, 520)))

    def test_mismo_horario_distinto_dia(self):
        self.assertFalse(meetings_overlap(Meeting(1, 480, 540), Meeting(2, 480, 540)))

    def test_paralelo_con_varias_reuniones(self):
        a = offering("1", meetings=((0, 480, 540), (2, 480, 540)))
        b = offering("2", "SYN102", meetings=((1, 480, 540), (2, 530, 600)))
        c = offering("3", "SYN103", meetings=((1, 480, 540), (2, 540, 600)))
        self.assertTrue(offerings_conflict(a, b))
        self.assertFalse(offerings_conflict(a, c))

    def test_conflicto_simetrico_y_reflexivo(self):
        a, b = offering("1"), offering("2", meetings=((0, 500, 560),))
        self.assertEqual(offerings_conflict(a, b), offerings_conflict(b, a))
        self.assertTrue(offerings_conflict(a, a))

    def test_equivale_a_interseccion_de_minutos(self):
        """Oraculo independiente: conjuntos de minutos (semilla fija, 3000 pares)."""
        rng = random.Random(20261124)

        def rand_meeting():
            start = rng.randrange(0, 1439)
            return Meeting(rng.randrange(0, 3), start, rng.randrange(start + 1, min(start + 181, 1441)))

        def minutes(m):
            return {(m.day, t) for t in range(m.start_minute, m.end_minute)}

        for _ in range(3000):
            a, b = rand_meeting(), rand_meeting()
            self.assertEqual(meetings_overlap(a, b), bool(minutes(a) & minutes(b)))


class OfferingTests(ModelTestCase):
    def test_sin_reuniones(self):
        self.assertCode(ErrorCode.INVALID_RANGE, offering, "1", meetings=())

    def test_campos_vacios(self):
        base = {
            "term": "T", "nrc": "1", "course_code": "X", "section": "1",
            "instructor_label": "d", "meetings": (Meeting(0, 0, 60),),
            "source": "s", "retrieved_at": "r",
        }
        for field in ("nrc", "course_code"):
            with self.subTest(field=field):
                self.assertCode(ErrorCode.INVALID_RANGE, Offering, **{**base, field: ""})


class EligibleCourseTests(ModelTestCase):
    def test_creditos_invalidos(self):
        for credits in (0, -1, 1.5, True, None):
            with self.subTest(credits=credits):
                self.assertCode(ErrorCode.INVALID_RANGE, EligibleCourse, "SYN101", credits, ())

    def test_rechaza_oferta_de_otra_materia(self):
        self.assertCode(
            ErrorCode.INVALID_RANGE, EligibleCourse, "SYN101", 3, (offering("1", "OTRA"),)
        )

    def test_sin_ofertas_es_valido(self):
        self.assertEqual(EligibleCourse("SYN101", 3, ()).offerings, ())


if __name__ == "__main__":
    unittest.main()
