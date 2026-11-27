"""Pruebas de los fixtures sinteticos y del mock de habilitacion."""
import unittest

from domain.scheduling import ErrorCode, ScheduleError, offerings_conflict
from synthetic import CatalogParams, eligible_courses, generate_catalog, tiny_catalog

SEEDS = range(25)


def is_dag(catalog):
    deps = {c.code: set() for c in catalog.courses}
    for g in catalog.prerequisite_groups:
        deps[g.course_code].update(g.alternatives)
    done, left = set(), set(deps)
    while left:
        ready = {c for c in left if deps[c] <= done}
        if not ready:
            return False
        done |= ready
        left -= ready
    return True


def codes(lst):
    return [e.course_code for e in lst]


class DeterminismTests(unittest.TestCase):
    def test_misma_semilla_mismo_catalogo(self):
        self.assertEqual(
            generate_catalog(CatalogParams(seed=7)), generate_catalog(CatalogParams(seed=7))
        )

    def test_semillas_distintas_difieren(self):
        self.assertNotEqual(
            generate_catalog(CatalogParams(seed=1)), generate_catalog(CatalogParams(seed=2))
        )


class StructureTests(unittest.TestCase):
    def test_invariantes_estructurales(self):
        for seed in SEEDS:
            with self.subTest(seed=seed):
                cat = generate_catalog(CatalogParams(seed=seed))
                all_codes = [c.code for c in cat.courses]
                self.assertEqual(len(all_codes), len(set(all_codes)))
                nrcs = [o.nrc for o in cat.offerings]
                self.assertEqual(len(nrcs), len(set(nrcs)))
                self.assertTrue(all(o.course_code in set(all_codes) for o in cat.offerings))
                self.assertTrue(all(o.source == "fixture-sintetico" for o in cat.offerings))
                self.assertEqual({e.career_id for e in cat.entries}, {"1CMP", "1MAC"})
                self.assertTrue(all(e.course_code in set(all_codes) for e in cat.entries))
                for g in cat.prerequisite_groups:
                    self.assertIn(g.course_code, all_codes)
                    self.assertTrue(g.alternatives)
                    self.assertEqual(len(set(g.alternatives)), len(g.alternatives))
                    self.assertTrue(all(a in all_codes and a != g.course_code for a in g.alternatives))
                self.assertTrue(is_dag(cat))

    def test_prerrequisitos_cerrados_dentro_de_cada_malla(self):
        for seed in SEEDS:
            cat = generate_catalog(CatalogParams(seed=seed))
            for career in ("1CMP", "1MAC"):
                in_career = cat.career_codes(career)
                for g in cat.prerequisite_groups:
                    if g.course_code in in_career:
                        with self.subTest(seed=seed, career=career, course=g.course_code):
                            self.assertLessEqual(set(g.alternatives), in_career)

    def test_cobertura_de_casos_exigidos(self):
        for seed in SEEDS:
            with self.subTest(seed=seed):
                cat = generate_catalog(CatalogParams(seed=seed))
                cmp_, mac = cat.career_codes("1CMP"), cat.career_codes("1MAC")
                self.assertTrue(cmp_ & mac)
                self.assertTrue(cmp_ - mac and mac - cmp_)
                kinds = {e.kind for e in cat.entries}
                self.assertLessEqual(
                    {"core", "shared", "general_college", "english", "lab", "exercise",
                     "elective", "optional"}, kinds)
                self.assertTrue(any(len(g.alternatives) > 1 for g in cat.prerequisite_groups))
                self.assertTrue(any(len(o.meetings) > 1 for o in cat.offerings))

    def test_prefijo_no_decide_la_pertenencia(self):
        for seed in SEEDS:
            with self.subTest(seed=seed):
                cat = generate_catalog(CatalogParams(seed=seed))
                self.assertIn("SYNCMP901", cat.course_codes())
                self.assertNotIn("SYNCMP901", cat.career_codes("1CMP") | cat.career_codes("1MAC"))
                self.assertIn("SYNMAC902", cat.career_codes("1CMP"))
                self.assertNotIn("SYNMAC902", cat.career_codes("1MAC"))

    def test_densidad_de_cruces_depende_del_pool(self):
        def ratio(pool):
            offs = generate_catalog(CatalogParams(seed=3, slot_pool=pool)).offerings
            pairs = [(a, b) for i, a in enumerate(offs) for b in offs[i + 1:]]
            return sum(offerings_conflict(a, b) for a, b in pairs) / len(pairs)

        self.assertGreater(ratio(6), ratio(110))


class EligibilityTests(unittest.TestCase):
    def setUp(self):
        self.tiny = tiny_catalog()

    def test_sin_aprobadas(self):
        self.assertEqual(codes(eligible_courses(self.tiny, "1CMP", set())), ["SYN-G1", "SYN-S1"])
        self.assertEqual(codes(eligible_courses(self.tiny, "1MAC", set())), ["SYN-G1", "SYN-S1"])

    def test_requisito_alternativo_basta_con_una(self):
        for passed in ({"SYN-G1"}, {"SYN-S1"}):
            with self.subTest(passed=passed):
                self.assertIn("SYN-M1", codes(eligible_courses(self.tiny, "1MAC", passed)))

    def test_and_de_ors(self):
        # SYN-C2 exige SYN-C1 y (SYN-S1 o SYN-S2)
        self.assertNotIn("SYN-C2", codes(eligible_courses(self.tiny, "1CMP", {"SYN-C1"})))
        self.assertNotIn("SYN-C2", codes(eligible_courses(self.tiny, "1CMP", {"SYN-S1"})))
        ok = eligible_courses(self.tiny, "1CMP", {"SYN-C1", "SYN-G1", "SYN-S1"})
        self.assertIn("SYN-C2", codes(ok))

    def test_excluye_aprobadas_sin_oferta_y_fuera_de_malla(self):
        got = codes(eligible_courses(self.tiny, "1CMP", {"SYN-G1"}))
        self.assertNotIn("SYN-G1", got)  # aprobada
        self.assertNotIn("SYN-X1", got)  # sin oferta
        self.assertNotIn("SYNCMP901", got)  # ofertada, pero en ninguna malla
        self.assertNotIn("SYN-M1", got)  # solo de 1MAC

    def test_cruces_conocidos(self):
        offs = {o.nrc: o for o in self.tiny.offerings}
        for a, b in [("1001", "2002"), ("1001", "4001"), ("2002", "4001"), ("1001", "6001")]:
            with self.subTest(pair=(a, b)):
                self.assertTrue(offerings_conflict(offs[a], offs[b]))
        self.assertFalse(offerings_conflict(offs["1001"], offs["2001"]))  # consecutivas

    def test_tiny_es_dag(self):
        self.assertTrue(is_dag(self.tiny))

    def test_carrera_no_soportada(self):
        with self.assertRaises(ScheduleError) as cm:
            eligible_courses(self.tiny, "1XXX", set())
        self.assertIs(cm.exception.code, ErrorCode.CAREER_NOT_SUPPORTED)

    def test_aprobada_desconocida(self):
        with self.assertRaises(ScheduleError) as cm:
            eligible_courses(self.tiny, "1CMP", {"NO-EXISTE"})
        self.assertIs(cm.exception.code, ErrorCode.UNKNOWN_COURSE)

    def test_catalogo_sin_ofertas(self):
        cat = generate_catalog(CatalogParams(seed=1, offered_prob=0.0))
        self.assertEqual(cat.offerings, ())
        self.assertEqual(eligible_courses(cat, "1CMP", set()), [])
        self.assertEqual(eligible_courses(cat, "1MAC", set()), [])

    def test_ambas_carreras_en_generado(self):
        cat = generate_catalog(CatalogParams(seed=5))
        for career in ("1CMP", "1MAC"):
            with self.subTest(career=career):
                el = eligible_courses(cat, career, set())
                self.assertTrue(el)
                self.assertLessEqual({e.course_code for e in el}, cat.career_codes(career))
                self.assertTrue(any(e.offerings for e in el))


if __name__ == "__main__":
    unittest.main()
