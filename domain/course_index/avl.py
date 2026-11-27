"""Ordered in-memory index. Keys must have a consistent total ordering."""
from dataclasses import dataclass
from typing import Generic, Iterator, TypeVar

K = TypeVar("K")
V = TypeVar("V")


@dataclass(slots=True)
class _Node(Generic[K, V]):
    key: K
    value: V
    left: "_Node[K, V] | None" = None
    right: "_Node[K, V] | None" = None
    height: int = 1


def _height(node):
    return node.height if node else 0


def _refresh(node):
    node.height = 1 + max(_height(node.left), _height(node.right))


def _rotate_left(node):
    top = node.right
    node.right = top.left
    top.left = node
    _refresh(node)
    _refresh(top)
    return top


def _rotate_right(node):
    top = node.left
    node.left = top.right
    top.right = node
    _refresh(node)
    _refresh(top)
    return top


def _balance(node):
    _refresh(node)
    factor = _height(node.left) - _height(node.right)
    if factor > 1:
        if _height(node.left.left) < _height(node.left.right):
            node.left = _rotate_left(node.left)
        return _rotate_right(node)
    if factor < -1:
        if _height(node.right.right) < _height(node.right.left):
            node.right = _rotate_right(node.right)
        return _rotate_left(node)
    return node


class CourseAVL(Generic[K, V]):
    """Unique-key AVL map; put replaces an existing value.

    Range bounds are inclusive. Composite keys can distinguish multiple
    offerings, e.g. (term, course_code, nrc), without changing domain models.
    """

    def __init__(self):
        self._root: _Node[K, V] | None = None
        self._size = 0

    def __len__(self) -> int:
        return self._size

    def put(self, key: K, value: V) -> None:
        def insert(node):
            if node is None:
                self._size += 1
                return _Node(key, value)
            if key < node.key:
                node.left = insert(node.left)
            elif key > node.key:
                node.right = insert(node.right)
            else:
                node.value = value
                return node
            return _balance(node)
        self._root = insert(self._root)

    def get(self, key: K) -> V:
        node = self._root
        while node is not None:
            if key < node.key:
                node = node.left
            elif key > node.key:
                node = node.right
            else:
                return node.value
        raise KeyError(key)

    def delete(self, key: K) -> None:
        def remove(node, target):
            if node is None:
                raise KeyError(target)
            if target < node.key:
                node.left = remove(node.left, target)
            elif target > node.key:
                node.right = remove(node.right, target)
            else:
                if node.left is None:
                    return node.right
                if node.right is None:
                    return node.left
                successor = node.right
                while successor.left is not None:
                    successor = successor.left
                node.key, node.value = successor.key, successor.value
                node.right = remove(node.right, successor.key)
            return _balance(node)
        self._root = remove(self._root, key)
        self._size -= 1

    def range_items(self, lower: K, upper: K) -> Iterator[tuple[K, V]]:
        if upper < lower:
            raise ValueError("upper bound must not precede lower bound")

        def visit(node):
            if node is None:
                return
            if lower < node.key:
                yield from visit(node.left)
            if lower <= node.key <= upper:
                yield node.key, node.value
            if node.key < upper:
                yield from visit(node.right)
        return visit(self._root)

    def assert_valid(self) -> None:
        """Raise AssertionError if ordering, balance, heights or size diverge."""
        def check(node, lower, upper):
            if node is None:
                return 0, 0
            assert lower is None or lower < node.key
            assert upper is None or node.key < upper
            left_height, left_count = check(node.left, lower, node.key)
            right_height, right_count = check(node.right, node.key, upper)
            assert abs(left_height - right_height) <= 1
            assert node.height == 1 + max(left_height, right_height)
            return node.height, 1 + left_count + right_count
        _, count = check(self._root, None, None)
        assert count == self._size
