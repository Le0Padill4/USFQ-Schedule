"""Directed acyclic prerequisite graph. Edges express AND requirements only."""
from collections import deque
import heapq
from collections.abc import Iterable


class GraphError(ValueError):
    """Stable machine-readable code plus a human-readable message."""

    def __init__(self, code: str, message: str):
        self.code = code
        super().__init__(message)


class CourseGraph:
    """Own adjacency-list graph; no graph-library dependency or recursive DFS.

    Unknown rule completeness is explicit and blocks eligibility. All externally
    returned collections are detached tuples. Public mutations preserve a DAG.
    """

    def __init__(self) -> None:
        self._next: dict[str, set[str]] = {}
        self._previous: dict[str, set[str]] = {}
        self._indegree: dict[str, int] = {}
        self._known: set[str] = set()

    @staticmethod
    def _validate_code(code: str) -> None:
        if not isinstance(code, str) or not code or code.strip() != code:
            raise GraphError("INVALID_CODE", "Expected an exact nonempty course code.")

    def _require(self, code: str) -> None:
        self._validate_code(code)
        if code not in self._next:
            raise GraphError("UNKNOWN_COURSE", f"Unknown course: {code}")

    @staticmethod
    def _validate_flag(flag: bool) -> None:
        if type(flag) is not bool:
            raise GraphError("INVALID_FLAG", "Expected a boolean rule-completeness flag.")

    @property
    def courses(self) -> tuple[str, ...]:
        return tuple(sorted(self._next))

    @property
    def edges(self) -> tuple[tuple[str, str], ...]:
        return tuple(sorted((pre, course) for pre, targets in self._next.items() for course in targets))

    def snapshot(self) -> tuple[tuple[str, ...], tuple[tuple[str, str], ...], tuple[str, ...]]:
        return self.courses, self.edges, tuple(sorted(self._known))

    def add_course(self, code: str, *, prerequisites_known: bool = False) -> None:
        self._validate_code(code)
        self._validate_flag(prerequisites_known)
        if code in self._next:
            raise GraphError("DUPLICATE_COURSE", f"Duplicate course: {code}")
        self._next[code] = set()
        self._previous[code] = set()
        self._indegree[code] = 0
        if prerequisites_known:
            self._known.add(code)

    def remove_course(self, code: str) -> None:
        self._require(code)
        for pre in self._previous[code]:
            self._next[pre].remove(code)
        for course in self._next[code]:
            self._previous[course].remove(code)
            self._indegree[course] -= 1
            self._known.discard(course)
        del self._next[code]
        del self._previous[code]
        del self._indegree[code]
        self._known.discard(code)

    def add_prerequisite(self, prerequisite_code: str, course_code: str) -> bool:
        self._require(prerequisite_code)
        self._require(course_code)
        if course_code in self._next[prerequisite_code]:
            return False
        if prerequisite_code == course_code or prerequisite_code in self._reachable(course_code, self._next):
            raise GraphError("CYCLE", "A prerequisite must not introduce a directed cycle.")
        self._next[prerequisite_code].add(course_code)
        self._previous[course_code].add(prerequisite_code)
        self._indegree[course_code] += 1
        return True

    def remove_prerequisite(self, prerequisite_code: str, course_code: str) -> bool:
        self._require(prerequisite_code)
        self._require(course_code)
        if course_code not in self._next[prerequisite_code]:
            return False
        self._next[prerequisite_code].remove(course_code)
        self._previous[course_code].remove(prerequisite_code)
        self._indegree[course_code] -= 1
        self._known.discard(course_code)
        return True

    def set_rules_known(self, code: str, known: bool) -> None:
        self._require(code)
        self._validate_flag(known)
        if known:
            self._known.add(code)
        else:
            self._known.discard(code)

    def rules_known(self, code: str) -> bool:
        self._require(code)
        return code in self._known

    @staticmethod
    def _reachable(start: str, adjacency: dict[str, set[str]]) -> set[str]:
        seen: set[str] = set()
        pending = list(adjacency[start])
        while pending:
            code = pending.pop()
            if code not in seen:
                seen.add(code)
                pending.extend(adjacency[code] - seen)
        return seen

    def dependencies(self, code: str, *, transitive: bool = True) -> tuple[str, ...]:
        self._require(code)
        self._validate_flag(transitive)
        found = self._reachable(code, self._previous) if transitive else self._previous[code]
        return tuple(sorted(found))

    def dependents(self, code: str, *, transitive: bool = True) -> tuple[str, ...]:
        self._require(code)
        self._validate_flag(transitive)
        found = self._reachable(code, self._next) if transitive else self._next[code]
        return tuple(sorted(found))

    def bfs(self, start: str) -> tuple[str, ...]:
        self._require(start)
        seen = {start}
        pending = deque([start])
        output = []
        while pending:
            code = pending.popleft()
            output.append(code)
            for target in sorted(self._next[code]):
                if target not in seen:
                    seen.add(target)
                    pending.append(target)
        return tuple(output)

    def dfs(self, start: str) -> tuple[str, ...]:
        self._require(start)
        seen: set[str] = set()
        pending = [start]
        output = []
        while pending:
            code = pending.pop()
            if code in seen:
                continue
            seen.add(code)
            output.append(code)
            pending.extend(sorted(self._next[code] - seen, reverse=True))
        return tuple(output)

    def topological_order(self) -> tuple[str, ...]:
        degrees = self._indegree.copy()
        ready = [code for code, degree in degrees.items() if degree == 0]
        heapq.heapify(ready)
        output = []
        while ready:
            code = heapq.heappop(ready)
            output.append(code)
            for target in self._next[code]:
                degrees[target] -= 1
                if degrees[target] == 0:
                    heapq.heappush(ready, target)
        if len(output) != len(self._next):
            raise GraphError("CYCLE", "The graph contains a directed cycle.")
        return tuple(output)

    def eligible_courses(self, passed_codes: Iterable[str]) -> tuple[str, ...]:
        # Validate before building a set so malformed elements produce GraphError.
        if isinstance(passed_codes, (str, bytes)) or not isinstance(passed_codes, Iterable):
            raise GraphError("INVALID_CODE", "Expected a collection of course codes.")
        passed: set[str] = set()
        for code in passed_codes:
            self._require(code)
            passed.add(code)
        return tuple(sorted(code for code in self._known - passed if self._previous[code] <= passed))

    def check_invariants(self) -> None:
        """Raise AssertionError for a corrupt representation; never mutate it."""
        nodes = set(self._next)
        assert nodes == set(self._previous) == set(self._indegree), "Node indexes disagree"
        assert self._known <= nodes, "Completeness references an absent node"
        for code in nodes:
            assert code not in self._next[code], "Self loop"
            assert self._indegree[code] == len(self._previous[code]), "Incorrect indegree"
            for target in self._next[code]:
                assert target in nodes and code in self._previous[target], "Missing reverse edge"
            for pre in self._previous[code]:
                assert pre in nodes and code in self._next[pre], "Missing forward edge"
        self.topological_order()
