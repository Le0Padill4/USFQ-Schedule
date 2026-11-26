"""Ordered in-memory index of course records by exact course code."""
from typing import Generic, Iterator, TypeVar

from domain.course_index.avl import CourseAVL

V = TypeVar("V")


def _code(value: str) -> str:
    if not isinstance(value, str) or not value or value != value.strip():
        raise ValueError("course code must be non-empty without outer whitespace")
    return value


class CourseIndex(Generic[V]):
    """Unique exact codes; career membership is deliberately kept elsewhere."""

    def __init__(self) -> None:
        self._tree: CourseAVL[str, V] = CourseAVL()

    def __len__(self) -> int:
        return len(self._tree)

    def add(self, code: str, value: V) -> None:
        code = _code(code)
        try:
            self._tree.get(code)
        except KeyError:
            self._tree.put(code, value)
            return
        raise ValueError("duplicate course code")

    def get(self, code: str) -> V:
        return self._tree.get(_code(code))

    def remove(self, code: str) -> None:
        self._tree.delete(_code(code))

    def range_items(self, lower: str, upper: str) -> Iterator[tuple[str, V]]:
        return self._tree.range_items(_code(lower), _code(upper))

    def assert_valid(self) -> None:
        self._tree.assert_valid()
