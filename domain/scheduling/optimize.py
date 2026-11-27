"""Operacion «mejores K horarios»: dos candidatos que devuelven exactamente lo mismo.

- A (``best_schedules_all``): generar TODOS los horarios factibles (CSP), puntuarlos y quedarse
  con el Top-K mediante el heap.
- B (``best_schedules_bnb``): branch and bound. Recorre el espacio como el backtracking, pero
  con cota optimista del puntaje; descarta una rama cuando su cota es ESTRICTAMENTE menor que el
  peor puntaje del Top-K actual (con empate no se poda, porque el desempate por NRC aun podria
  admitirla). Los hijos se exploran de mayor a menor cota para llenar pronto el Top-K.

Cota (por termino del puntaje, ``max(w*lo, w*hi)`` sobre el rango alcanzable del valor crudo;
valida para cualquier signo de peso):
- free_day: [0, 1] si el dia aun no se usa; [0, 0] si ya se uso.
- days_used: [dias ya usados, 7].
- gap_minutes: [0, 7*1440] (agregar clases puede reducir los huecos; cota debil a proposito).
- preferred / avoided: [valor actual, actual + maximo posible de cada materia restante].
- optional_priority: [actual, actual + prioridades de las opcionales restantes].
El puntaje final de cada hoja se calcula con ``score_schedule`` (mismo codigo que el candidato A).
"""

from __future__ import annotations

from collections.abc import Callable

from .generation import Stats, generate_csp, offerings_conflict
from .models import Offering
from .request import Problem
from .scoring import ScheduleResult, _overlap_minutes, score_schedule
from .topk import BoundedHeap, top_k_heap

_MAX_GAP_MINUTES = 7 * 1440


def best_schedules_all(problem: Problem, stats: Stats | None = None) -> list[ScheduleResult]:
    """Candidato A: generar todos (CSP) + puntuar + Top-K con heap."""
    scored = [score_schedule(c, problem) for c in generate_csp(problem, stats)]
    return top_k_heap(scored, problem.max_results, stats)


def _build_bound(problem: Problem):
    """Prepara la cota. Devuelve (bound, infos, credit_suffix)."""
    p = problem.preferences
    slots = problem.slots
    n = len(slots)
    infos: dict[str, tuple[frozenset[int], int, int]] = {}
    for s in slots:
        for o in s.options:
            infos[o.nrc] = (
                frozenset(m.day for m in o.meetings),
                sum(_overlap_minutes(m, r) for m in o.meetings for r in p.preferred_ranges),
                sum(_overlap_minutes(m, r) for m in o.meetings for r in p.avoided_ranges),
            )
    pref_suf, avoid_suf, prio_suf, credit_suf = ([0] * (n + 1) for _ in range(4))
    for i in range(n - 1, -1, -1):
        s = slots[i]
        pref_suf[i] = pref_suf[i + 1] + max((infos[o.nrc][1] for o in s.options), default=0)
        avoid_suf[i] = avoid_suf[i + 1] + max((infos[o.nrc][2] for o in s.options), default=0)
        prio_suf[i] = prio_suf[i + 1] + (s.priority if s.optional else 0)
        credit_suf[i] = credit_suf[i + 1] + s.credits

    w_free = p.w_free_day if p.free_day is not None else 0
    w_days = -p.w_days if p.minimize_days else 0
    w_gaps = -p.w_gaps if p.minimize_gaps else 0
    w_pref = p.w_preferred if p.preferred_ranges else 0
    w_avoid = -p.w_avoided if p.avoided_ranges else 0
    w_prio = p.w_priority

    def bound(days: frozenset[int], pref: int, avoid: int, prio: int, i: int) -> int:
        free_hi = 0 if (p.free_day is None or p.free_day in days) else 1
        return (
            max(0, w_free * free_hi)
            + max(w_days * len(days), w_days * 7)
            + max(0, w_gaps * _MAX_GAP_MINUTES)
            + max(w_pref * pref, w_pref * (pref + pref_suf[i]))
            + max(w_avoid * avoid, w_avoid * (avoid + avoid_suf[i]))
            + max(w_prio * prio, w_prio * (prio + prio_suf[i]))
        )

    return bound, infos, credit_suf


def score_upper_bound(problem: Problem) -> int:
    """Cota optimista del puntaje de cualquier horario factible (para pruebas)."""
    bound, _, _ = _build_bound(problem)
    return bound(frozenset(), 0, 0, 0, 0)


def best_schedules_bnb(
    problem: Problem,
    stats: Stats | None = None,
    *,
    _audit: list | None = None,
) -> list[ScheduleResult]:
    """Candidato B: branch and bound con cota optimista y Top-K en heap."""
    st = stats if stats is not None else Stats()
    slots = problem.slots
    n = len(slots)
    bound, infos, credit_suf = _build_bound(problem)
    heap = BoundedHeap(problem.max_results, st)
    chosen: list[Offering] = []

    def rec(i: int, credits: int, days: frozenset[int], pref: int, avoid: int, prio: int) -> None:
        st.nodes += 1
        if credits + credit_suf[i] < problem.min_credits:
            return
        if i == n:
            if chosen:
                heap.offer(score_schedule(tuple(sorted(o.nrc for o in chosen)), problem))
            return
        slot = slots[i]
        children = []
        for off in slot.options:
            if problem.max_credits is not None and credits + slot.credits > problem.max_credits:
                continue
            clash = False
            for other in chosen:
                st.conflict_checks += 1
                if offerings_conflict(other, off):
                    clash = True
                    break
            if clash:
                continue
            d, pf, av = infos[off.nrc]
            nd, npf, nav, npr = days | d, pref + pf, avoid + av, prio + slot.priority
            st.bounds += 1
            b = bound(nd, npf, nav, npr, i + 1)
            if _audit is not None:
                _audit.append((tuple(o.nrc for o in chosen) + (off.nrc,), i + 1, b))
            children.append((b, off.nrc, off, nd, npf, nav, npr))
        if slot.optional:
            st.bounds += 1
            b = bound(days, pref, avoid, prio, i + 1)
            if _audit is not None:
                _audit.append((tuple(o.nrc for o in chosen), i + 1, b))
            children.append((b, "", None, days, pref, avoid, prio))
        children.sort(key=lambda c: (-c[0], c[1]))
        for b, _, off, nd, npf, nav, npr in children:
            th = heap.threshold()
            if th is not None and b < th:  # estricto: con empate no se poda
                st.pruned += 1
                break  # hijos ordenados por cota decreciente: el resto tampoco entra
            if off is None:
                rec(i + 1, credits, nd, npf, nav, npr)
            else:
                chosen.append(off)
                rec(i + 1, credits + slot.credits, nd, npf, nav, npr)
                chosen.pop()

    rec(0, 0, frozenset(), 0, 0, 0)
    return heap.best_first()


METHODS: dict[str, Callable[..., list[ScheduleResult]]] = {
    "todos_topk": best_schedules_all,
    "branch_and_bound": best_schedules_bnb,
}
