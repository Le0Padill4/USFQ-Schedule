"""List-based reference for the isolated course index; no AVL or dict."""


class SlowCourseIndex:
    def __init__(self):
        self.items = []

    @staticmethod
    def _code(code):
        if not isinstance(code, str) or not code or code != code.strip():
            raise ValueError("invalid course code")
        return code

    def __len__(self):
        return len(self.items)

    def add(self, code, value):
        code = self._code(code)
        if any(key == code for key, _ in self.items):
            raise ValueError("duplicate course code")
        self.items.append((code, value))

    def get(self, code):
        code = self._code(code)
        for key, value in self.items:
            if key == code:
                return value
        raise KeyError(code)

    def remove(self, code):
        code = self._code(code)
        for position, (key, _) in enumerate(self.items):
            if key == code:
                del self.items[position]
                return
        raise KeyError(code)

    def range_items(self, lower, upper):
        lower, upper = self._code(lower), self._code(upper)
        if upper < lower:
            raise ValueError("reversed range")
        return iter(sorted((key, value) for key, value in self.items
                           if lower <= key <= upper))
