"""Small, model-independent conflict operations for weekly meeting intervals."""
from dataclasses import dataclass
from collections.abc import Iterable


@dataclass(frozen=True, slots=True)
class Interval:
    """Synthetic weekly interval: Monday=0, Sunday=6, [start, end) minutes."""
    day: int
    start: int
    end: int

    def __post_init__(self):
        if (type(self.day) is not int or type(self.start) is not int
                or type(self.end) is not int or not 0 <= self.day <= 6
                or not 0 <= self.start < self.end <= 1440):
            raise ValueError("invalid weekly interval")


def overlaps(left: Interval, right: Interval) -> bool:
    return (left.day == right.day and left.start < right.end
            and right.start < left.end)


def conflicts(left: Iterable[Interval], right: Iterable[Interval]) -> bool:
    """True if any meeting from each collection overlaps.

    Empty collections do not establish a conflict, but callers must separately
    distinguish unknown or asynchronous meetings from confirmed empty data.
    """
    second = tuple(right)
    return any(overlaps(a, b) for a in left for b in second)
