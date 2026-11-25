"""Pruebas de los fixtures sinteticos y del mock de habilitacion."""

import pytest

from usfq_schedule.domain.scheduling import ErrorCode, ScheduleError, offerings_conflict
from usfq_schedule.synthetic import (
    CatalogParams,
    eligible_courses,
    generate_catalog,
    tiny_catalog,
)

SEEDS = list(range(25))


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


def nrc_codes(lst):
    return {o.nrc for ec in lst for o in ec.offerings}


# --- Determinismo ---


def test_misma_semilla_mismo_catalogo():
    assert generate_catalog(CatalogParams(seed=7)) == generate_catalog(CatalogParams(seed=7))


def test_semillas_distintas_difieren():
    assert generate_catalog(CatalogParams(seed=1)) != generate_catalog(CatalogParams(seed=2))


# --- Invariantes estructurales en 25 semillas ---


@pytest.mark.parametrize("seed", SEEDS)
def test_invariantes_estructurales(seed):
    cat = generate_catalog(CatalogParams(seed=seed))
    codes = [c.code for c in cat.courses]
    assert len(codes) == len(set(codes))
    nrcs = [o.nrc for o in cat.offerings]
    assert len(nrcs) == len(set(nrcs))
    assert all(o.course_code in set(codes) for o in cat.offerings)
    assert all(o.source == "fixture-sintetico" for o in cat.offerings)
    assert {e.career_id for e in cat.entries} == {"1CMP", "1MAC"}
    assert all(e.course_code in set(codes) for e in cat.entries)
    for g in cat.prerequisite_groups:
        assert g.course_code in codes and g.alternatives
        assert len(set(g.alternatives)) == len(g.alternatives)
        assert all(a in codes and a != g.course_code for a in g.alternatives)
    assert is_dag(cat)


@pytest.mark.parametrize("seed", SEEDS)
def test_prerrequisitos_cerrados_dentro_de_cada_malla(seed):
    """Todo prerrequisito de una materia de una malla esta en esa misma malla."""
    cat = generate_catalog(CatalogParams(seed=seed))
    for career in ("1CMP", "1MAC"):
        in_career = cat.career_codes(career)
        for g in cat.prerequisite_groups:
            if g.course_code in in_career:
                assert set(g.alternatives) <= in_career


@pytest.mark.parametrize("seed", SEEDS)
def test_cobertura_de_casos_exigidos(seed):
    cat = generate_catalog(CatalogParams(seed=seed))
    cmp_, mac = cat.career_codes("1CMP"), cat.career_codes("1MAC")
    assert cmp_ & mac, "debe haber materias compartidas"
    assert cmp_ - mac and mac - cmp_
    kinds = {e.kind for e in cat.entries}
    assert {"core", "shared", "general_college", "english", "lab", "exercise"} <= kinds
    assert {"elective", "optional"} <= kinds
    assert any(len(g.alternatives) > 1 for g in cat.prerequisite_groups)
    assert any(len(o.meetings) > 1 for o in cat.offerings)


@pytest.mark.parametrize("seed", SEEDS)
def test_prefijo_no_decide_la_pertenencia(seed):
    cat = generate_catalog(CatalogParams(seed=seed))
    assert "SYNCMP901" in cat.course_codes()
    assert "SYNCMP901" not in cat.career_codes("1CMP") | cat.career_codes("1MAC")
    assert "SYNMAC902" in cat.career_codes("1CMP")
    assert "SYNMAC902" not in cat.career_codes("1MAC")


def test_densidad_de_cruces_depende_del_pool_de_franjas():
    def conflict_ratio(pool):
        cat = generate_catalog(CatalogParams(seed=3, slot_pool=pool))
        offs = cat.offerings
        pairs = [(a, b) for i, a in enumerate(offs) for b in offs[i + 1 :]]
        return sum(offerings_conflict(a, b) for a, b in pairs) / len(pairs)

    assert conflict_ratio(6) > conflict_ratio(110)


# --- Mock de habilitacion sobre el catalogo hecho a mano ---


def test_tiny_sin_aprobadas_1cmp():
    el = eligible_courses(tiny_catalog(), "1CMP", set())
    assert [e.course_code for e in el] == ["SYN-G1", "SYN-S1"]


def test_tiny_sin_aprobadas_1mac():
    el = eligible_courses(tiny_catalog(), "1MAC", set())
    assert [e.course_code for e in el] == ["SYN-G1", "SYN-S1"]


def test_tiny_requisito_alternativo_basta_con_una():
    cat = tiny_catalog()
    assert "SYN-M1" in [e.course_code for e in eligible_courses(cat, "1MAC", {"SYN-G1"})]
    assert "SYN-M1" in [e.course_code for e in eligible_courses(cat, "1MAC", {"SYN-S1"})]


def test_tiny_and_de_ors():
    cat = tiny_catalog()
    # SYN-C2 exige SYN-C1 y (SYN-S1 o SYN-S2)
    assert "SYN-C2" not in [e.course_code for e in eligible_courses(cat, "1CMP", {"SYN-C1"})]
    assert "SYN-C2" not in [e.course_code for e in eligible_courses(cat, "1CMP", {"SYN-S1"})]
    ok = eligible_courses(cat, "1CMP", {"SYN-C1", "SYN-G1", "SYN-S1"})
    assert "SYN-C2" in [e.course_code for e in ok]


def test_tiny_excluye_aprobadas_sin_oferta_y_fuera_de_malla():
    cat = tiny_catalog()
    codes = [e.course_code for e in eligible_courses(cat, "1CMP", {"SYN-G1"})]
    assert "SYN-G1" not in codes  # aprobada
    assert "SYN-X1" not in codes  # sin oferta
    assert "SYNCMP901" not in codes  # ofertada pero en ninguna malla
    assert "SYN-M1" not in codes  # solo de 1MAC


def test_tiny_cruces_conocidos():
    offs = {o.nrc: o for o in tiny_catalog().offerings}
    assert offerings_conflict(offs["1001"], offs["2002"])
    assert offerings_conflict(offs["1001"], offs["4001"])
    assert offerings_conflict(offs["2002"], offs["4001"])
    assert offerings_conflict(offs["1001"], offs["6001"])
    assert not offerings_conflict(offs["1001"], offs["2001"])  # consecutivas


def test_tiny_es_dag_y_valido():
    assert is_dag(tiny_catalog())


# --- Errores y bordes ---


def test_carrera_no_soportada():
    with pytest.raises(ScheduleError) as e:
        eligible_courses(tiny_catalog(), "1XXX", set())
    assert e.value.code is ErrorCode.CAREER_NOT_SUPPORTED


def test_aprobada_desconocida():
    with pytest.raises(ScheduleError) as e:
        eligible_courses(tiny_catalog(), "1CMP", {"NO-EXISTE"})
    assert e.value.code is ErrorCode.UNKNOWN_COURSE


def test_catalogo_sin_ofertas_da_lista_vacia():
    cat = generate_catalog(CatalogParams(seed=1, offered_prob=0.0))
    assert cat.offerings == ()
    assert eligible_courses(cat, "1CMP", set()) == []
    assert eligible_courses(cat, "1MAC", set()) == []


def test_eligibles_para_ambas_carreras_en_generado():
    cat = generate_catalog(CatalogParams(seed=5))
    for career in ("1CMP", "1MAC"):
        el = eligible_courses(cat, career, set())
        assert el
        assert {e.course_code for e in el} <= cat.career_codes(career)
        assert nrc_codes(el)
