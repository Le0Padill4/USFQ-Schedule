"""Generacion de TODOS los horarios factibles: dos candidatos para la misma operacion.

Ambos reciben el mismo ``Problem`` y devuelven la misma lista: tuplas de NRC ordenadas
ascendentemente, y la lista ordenada lexicograficamente. ``Stats`` cuenta pasos
(nodos visitados y comparaciones de cruce) para los benchmarks.
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import product

from .models import Offering, offerings_conflict
from .request import Problem


@dataclass
class Stats:
    nodes: int = 0
    conflict_checks: int = 0
    comparisons: int = 0


def generate_exhaustive(problem: Problem, stats: Stats | None = None) -> list[tuple[str, ...]]:
    """Candidato A: producto cartesiano completo de opciones + filtro."""
    st = stats if stats is not None else Stats()
    slots = problem.slots
    choices = [((None,) + s.options) if s.optional else s.options for s in slots]
    out: list[tuple[str, ...]] = []
    for combo in product(*choices):
        st.nodes += 1
        chosen: list[Offering] = []
        credits = 0
        for slot, off in zip(slots, combo):
            if off is not None:
                chosen.append(off)
                credits += slot.credits
        if not chosen or credits < problem.min_credits:
            continue
        if problem.max_credits is not None and credits > problem.max_credits:
            continue
        ok = True
        for i in range(len(chosen)):
            for j in range(i + 1, len(chosen)):
                st.conflict_checks += 1
                if offerings_conflict(chosen[i], chosen[j]):
                    ok = False
                    break
            if not ok:
                break
        if ok:
            out.append(tuple(sorted(o.nrc for o in chosen)))
    out.sort()
    return out


def generate_backtracking(problem: Problem, stats: Stats | None = None) -> list[tuple[str, ...]]:
    """Candidato B: backtracking con poda por cruces y por limites de creditos."""
    st = stats if stats is not None else Stats()
    slots = problem.slots
    n = len(slots)
    suffix = [0] * (n + 1)
    for i in range(n - 1, -1, -1):
        suffix[i] = suffix[i + 1] + slots[i].credits
    out: list[tuple[str, ...]] = []
    chosen: list[Offering] = []

    def rec(i: int, credits: int) -> None:
        st.nodes += 1
        if credits + suffix[i] < problem.min_credits:
            return
        if i == n:
            if chosen:
                out.append(tuple(sorted(o.nrc for o in chosen)))
            return
        slot = slots[i]
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
            chosen.append(off)
            rec(i + 1, credits + slot.credits)
            chosen.pop()
        if slot.optional:
            rec(i + 1, credits)

    rec(0, 0)
    out.sort()
    return out
