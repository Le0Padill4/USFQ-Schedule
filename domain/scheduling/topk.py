"""Seleccion Top-K: heap acotado propio (candidato A) frente a ordenamiento completo (B).

Invariante del heap: es un min-heap respecto a "peor": cada padre es peor o igual que sus
hijos, y la raiz es el peor de los k mejores conservados; ``len <= k``.
Ambos candidatos devuelven los mismos k resultados, del mejor al peor, con orden ``rank_key``.
"""

from __future__ import annotations

from functools import cmp_to_key

from .errors import ErrorCode, ScheduleError
from .generation import Stats
from .scoring import ScheduleResult, rank_key


def _check_k(k: object) -> None:
    if isinstance(k, bool) or not isinstance(k, int) or k < 1:
        raise ScheduleError(ErrorCode.INVALID_RANGE, f"k invalido: {k!r}")


class BoundedHeap:
    def __init__(self, k: int, stats: Stats | None = None) -> None:
        _check_k(k)
        self.k = k
        self._a: list[ScheduleResult] = []
        self.stats = stats if stats is not None else Stats()

    def __len__(self) -> int:
        return len(self._a)

    def _worse(self, a: ScheduleResult, b: ScheduleResult) -> bool:
        """True si ``a`` esta estrictamente peor ubicado que ``b``."""
        self.stats.comparisons += 1
        return a.score < b.score or (a.score == b.score and a.nrcs > b.nrcs)

    def _sift_up(self, i: int) -> None:
        a = self._a
        while i > 0:
            parent = (i - 1) // 2
            if self._worse(a[i], a[parent]):
                a[i], a[parent] = a[parent], a[i]
                i = parent
            else:
                break

    def _sift_down(self, i: int) -> None:
        a, n = self._a, len(self._a)
        while True:
            left, right, worst = 2 * i + 1, 2 * i + 2, i
            if left < n and self._worse(a[left], a[worst]):
                worst = left
            if right < n and self._worse(a[right], a[worst]):
                worst = right
            if worst == i:
                return
            a[i], a[worst] = a[worst], a[i]
            i = worst

    def offer(self, item: ScheduleResult) -> None:
        if len(self._a) < self.k:
            self._a.append(item)
            self._sift_up(len(self._a) - 1)
        elif self._worse(self._a[0], item):
            self._a[0] = item
            self._sift_down(0)

    def best_first(self) -> list[ScheduleResult]:
        """Contenido ordenado del mejor al peor, sin destruir el heap."""
        clone = BoundedHeap(self.k)
        clone._a = list(self._a)
        worst_first = []
        while clone._a:
            worst_first.append(clone._a[0])
            last = clone._a.pop()
            if clone._a:
                clone._a[0] = last
                clone._sift_down(0)
        worst_first.reverse()
        return worst_first

    def check_invariants(self) -> None:
        assert len(self._a) <= self.k, "heap excede k"
        for i in range(1, len(self._a)):
            parent = self._a[(i - 1) // 2]
            child = self._a[i]
            assert not (
                child.score < parent.score
                or (child.score == parent.score and child.nrcs > parent.nrcs)
            ), "un hijo es peor que su padre"


def top_k_heap(
    results: list[ScheduleResult], k: int, stats: Stats | None = None
) -> list[ScheduleResult]:
    heap = BoundedHeap(k, stats)
    for r in results:
        heap.offer(r)
    return heap.best_first()


def top_k_sort(
    results: list[ScheduleResult], k: int, stats: Stats | None = None
) -> list[ScheduleResult]:
    _check_k(k)
    if stats is None:
        return sorted(results, key=rank_key)[:k]

    def cmp(a: ScheduleResult, b: ScheduleResult) -> int:
        stats.comparisons += 1
        ka, kb = rank_key(a), rank_key(b)
        return (ka > kb) - (ka < kb)

    return sorted(results, key=cmp_to_key(cmp))[:k]
