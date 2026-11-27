"""Oráculo lento de I1 para I3: listas, sin usar algoritmos del grafo propio."""


class ListGraph:
    class Error(ValueError):
        def __init__(self, code):
            self.code = code

    def __init__(self):
        self.nodes = []
        self.arcs = []
        self.known = []

    def validate(self, code, exists=True):
        if not isinstance(code, str) or not code or code.strip() != code:
            raise self.Error("INVALID_CODE")
        if exists and code not in self.nodes:
            raise self.Error("UNKNOWN_COURSE")

    def add_course(self, code, *, prerequisites_known=False):
        self.validate(code, False)
        if type(prerequisites_known) is not bool:
            raise self.Error("INVALID_FLAG")
        if code in self.nodes:
            raise self.Error("DUPLICATE_COURSE")
        self.nodes.append(code)
        if prerequisites_known:
            self.known.append(code)

    def remove_course(self, code):
        self.validate(code)
        for pre, course in self.arcs:
            if pre == code and course in self.known:
                self.known.remove(course)
        self.arcs = [(a, b) for a, b in self.arcs if code not in (a, b)]
        self.nodes.remove(code)
        if code in self.known:
            self.known.remove(code)

    def add_prerequisite(self, pre, course):
        self.validate(pre)
        self.validate(course)
        if (pre, course) in self.arcs:
            return False
        if pre == course or course in self.dependencies(pre):
            raise self.Error("CYCLE")
        self.arcs.append((pre, course))
        return True

    def remove_prerequisite(self, pre, course):
        self.validate(pre)
        self.validate(course)
        if (pre, course) not in self.arcs:
            return False
        self.arcs.remove((pre, course))
        if course in self.known:
            self.known.remove(course)
        return True

    def set_rules_known(self, code, known):
        self.validate(code)
        if type(known) is not bool:
            raise self.Error("INVALID_FLAG")
        if code in self.known:
            self.known.remove(code)
        if known:
            self.known.append(code)

    def dependencies(self, code):
        self.validate(code)
        found = []
        changed = True
        while changed:
            changed = False
            for pre, course in self.arcs:
                if (course == code or course in found) and pre not in found:
                    found.append(pre)
                    changed = True
        return tuple(sorted(found))

    def eligible_courses(self, passed_codes):
        passed = list(passed_codes)
        for code in passed:
            self.validate(code)
        return tuple(sorted(code for code in self.nodes if code not in passed and code in self.known
                            and all(a in passed for a, b in self.arcs if b == code)))

    def topological_order(self):
        output = []
        while len(output) != len(self.nodes):
            ready = sorted(code for code in self.nodes if code not in output
                           and all(a in output for a, b in self.arcs if b == code))
            if not ready:
                raise self.Error("CYCLE")
            output.append(ready[0])
        return tuple(output)

    def snapshot(self):
        return tuple(sorted(self.nodes)), tuple(sorted(self.arcs)), tuple(sorted(self.known))
