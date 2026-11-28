"""In-memory lookup for offering identifiers scoped to an academic term."""
from typing import Generic, TypeVar

from domain.course_index.avl import CourseAVL

V = TypeVar("V")


def _key(term: str, nrc: str) -> tuple[str, str]:
    # Preserve leading zeroes; normalization belongs to the source adapter.
    if not isinstance(term, str) or not term or term != term.strip():
        raise ValueError("term must be a non-empty string without outer whitespace")
    if not isinstance(nrc, str) or not nrc or nrc != nrc.strip():
        raise ValueError("nrc must be a non-empty string without outer whitespace")
    return term, nrc


class NRCIndex(Generic[V]):
    """Unique (term, NRC) mapping, with no implicit overwrite on duplicates."""

    def __init__(self) -> None:
        self._tree: CourseAVL[tuple[str, str], V] = CourseAVL()

    def __len__(self) -> int:
        return len(self._tree)

    def add(self, term: str, nrc: str, value: V) -> None:
        key = _key(term, nrc)
        try:
            self._tree.get(key)
        except KeyError:
            self._tree.put(key, value)
            return
        raise ValueError("duplicate NRC in term")

    def get(self, term: str, nrc: str) -> V:
        return self._tree.get(_key(term, nrc))

    def remove(self, term: str, nrc: str) -> None:
        self._tree.delete(_key(term, nrc))

    def assert_valid(self) -> None:
        self._tree.assert_valid()
