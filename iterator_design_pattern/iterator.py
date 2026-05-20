"""
Iterator Design Pattern - Advanced Implementation
Real-world scenario: Binary Search Tree with multiple traversal strategies
In-order, pre-order, post-order, level-order, filtered, and paginated iterators.
"""
from __future__ import annotations
from abc import ABC, abstractmethod
from collections import deque
from typing import Generic, Iterator, Optional, TypeVar

T = TypeVar("T")


# ---------------------------------------------------------------------------
# BST Node
# ---------------------------------------------------------------------------

class BSTNode(Generic[T]):
    def __init__(self, value: T):
        self.value = value
        self.left: Optional[BSTNode[T]] = None
        self.right: Optional[BSTNode[T]] = None


# ---------------------------------------------------------------------------
# Iterator Interface
# ---------------------------------------------------------------------------

class TreeIterator(ABC, Generic[T]):
    @abstractmethod
    def __iter__(self) -> Iterator[T]: ...

    def to_list(self) -> list[T]:
        return list(self)

    def filter(self, predicate) -> list[T]:
        return [v for v in self if predicate(v)]


# ---------------------------------------------------------------------------
# Concrete Iterators
# ---------------------------------------------------------------------------

class InOrderIterator(TreeIterator[T]):
    """Left → Root → Right — produces sorted output for BST."""

    def __init__(self, root: Optional[BSTNode[T]]):
        self._root = root

    def __iter__(self) -> Iterator[T]:
        yield from self._traverse(self._root)

    def _traverse(self, node: Optional[BSTNode[T]]) -> Iterator[T]:
        if node:
            yield from self._traverse(node.left)
            yield node.value
            yield from self._traverse(node.right)


class PreOrderIterator(TreeIterator[T]):
    """Root → Left → Right — useful for copying/serializing the tree."""

    def __init__(self, root: Optional[BSTNode[T]]):
        self._root = root

    def __iter__(self) -> Iterator[T]:
        yield from self._traverse(self._root)

    def _traverse(self, node: Optional[BSTNode[T]]) -> Iterator[T]:
        if node:
            yield node.value
            yield from self._traverse(node.left)
            yield from self._traverse(node.right)


class PostOrderIterator(TreeIterator[T]):
    """Left → Right → Root — useful for deletion."""

    def __init__(self, root: Optional[BSTNode[T]]):
        self._root = root

    def __iter__(self) -> Iterator[T]:
        yield from self._traverse(self._root)

    def _traverse(self, node: Optional[BSTNode[T]]) -> Iterator[T]:
        if node:
            yield from self._traverse(node.left)
            yield from self._traverse(node.right)
            yield node.value


class LevelOrderIterator(TreeIterator[T]):
    """BFS — level by level."""

    def __init__(self, root: Optional[BSTNode[T]]):
        self._root = root

    def __iter__(self) -> Iterator[T]:
        if not self._root:
            return
        queue: deque[BSTNode[T]] = deque([self._root])
        while queue:
            node = queue.popleft()
            yield node.value
            if node.left:
                queue.append(node.left)
            if node.right:
                queue.append(node.right)

    def by_level(self) -> list[list[T]]:
        """Returns values grouped by level."""
        if not self._root:
            return []
        result = []
        queue: deque[BSTNode[T]] = deque([self._root])
        while queue:
            level_size = len(queue)
            level = []
            for _ in range(level_size):
                node = queue.popleft()
                level.append(node.value)
                if node.left: queue.append(node.left)
                if node.right: queue.append(node.right)
            result.append(level)
        return result


class ReverseInOrderIterator(TreeIterator[T]):
    """Right → Root → Left — descending order for BST."""

    def __init__(self, root: Optional[BSTNode[T]]):
        self._root = root

    def __iter__(self) -> Iterator[T]:
        yield from self._traverse(self._root)

    def _traverse(self, node: Optional[BSTNode[T]]) -> Iterator[T]:
        if node:
            yield from self._traverse(node.right)
            yield node.value
            yield from self._traverse(node.left)


# ---------------------------------------------------------------------------
# Paginated Iterator — wraps any iterator with pagination
# ---------------------------------------------------------------------------

class PaginatedIterator(Generic[T]):
    def __init__(self, iterator: TreeIterator[T], page_size: int):
        self._items = iterator.to_list()
        self._page_size = page_size
        self._total = len(self._items)

    def page(self, page_num: int) -> list[T]:
        start = (page_num - 1) * self._page_size
        return self._items[start:start + self._page_size]

    @property
    def total_pages(self) -> int:
        return (self._total + self._page_size - 1) // self._page_size

    @property
    def total_items(self) -> int:
        return self._total


# ---------------------------------------------------------------------------
# BST with iterator factory
# ---------------------------------------------------------------------------

class BinarySearchTree(Generic[T]):
    def __init__(self):
        self._root: Optional[BSTNode[T]] = None
        self._size = 0

    def insert(self, value: T) -> BinarySearchTree[T]:
        self._root = self._insert(self._root, value)
        self._size += 1
        return self

    def _insert(self, node: Optional[BSTNode[T]], value: T) -> BSTNode[T]:
        if node is None:
            return BSTNode(value)
        if value < node.value:
            node.left = self._insert(node.left, value)
        elif value > node.value:
            node.right = self._insert(node.right, value)
        return node

    def contains(self, value: T) -> bool:
        node = self._root
        while node:
            if value == node.value: return True
            node = node.left if value < node.value else node.right
        return False

    # Iterator factory methods
    def in_order(self) -> InOrderIterator[T]:
        return InOrderIterator(self._root)

    def pre_order(self) -> PreOrderIterator[T]:
        return PreOrderIterator(self._root)

    def post_order(self) -> PostOrderIterator[T]:
        return PostOrderIterator(self._root)

    def level_order(self) -> LevelOrderIterator[T]:
        return LevelOrderIterator(self._root)

    def reverse_order(self) -> ReverseInOrderIterator[T]:
        return ReverseInOrderIterator(self._root)

    def paginated(self, page_size: int) -> PaginatedIterator[T]:
        return PaginatedIterator(self.in_order(), page_size)

    def __len__(self) -> int:
        return self._size


# ---------------------------------------------------------------------------
# Lazy Range Iterator (bonus — pure iterator pattern)
# ---------------------------------------------------------------------------

class LazyRange:
    """Memory-efficient range that generates values on demand."""

    def __init__(self, start: int, stop: int, step: int = 1):
        self._start = start
        self._stop = stop
        self._step = step

    def __iter__(self) -> Iterator[int]:
        current = self._start
        while current < self._stop:
            yield current
            current += self._step

    def __len__(self) -> int:
        return max(0, (self._stop - self._start + self._step - 1) // self._step)

    def filter(self, predicate) -> Iterator[int]:
        return (v for v in self if predicate(v))


# ---------------------------------------------------------------------------
# Demo
# ---------------------------------------------------------------------------

def main():
    print("=" * 55)
    print("  Iterator Pattern — BST Traversal Demo")
    print("=" * 55)

    bst: BinarySearchTree[int] = BinarySearchTree()
    values = [50, 30, 70, 20, 40, 60, 80, 10, 25, 35, 45, 55, 65, 75, 90]
    for v in values:
        bst.insert(v)

    print(f"\n  Inserted {len(bst)} values: {sorted(values)}")

    print(f"\n>>> In-order (sorted):    {bst.in_order().to_list()}")
    print(f">>> Pre-order:            {bst.pre_order().to_list()}")
    print(f">>> Post-order:           {bst.post_order().to_list()}")
    print(f">>> Reverse order (desc): {bst.reverse_order().to_list()}")

    print(f"\n>>> Level-order (BFS):    {bst.level_order().to_list()}")
    print(f">>> By level:")
    for i, level in enumerate(bst.level_order().by_level()):
        print(f"    Level {i}: {level}")

    print(f"\n>>> Filtered (in-order, even numbers only):")
    evens = bst.in_order().filter(lambda x: x % 2 == 0)
    print(f"    {evens}")

    print(f"\n>>> Filtered (in-order, > 50):")
    large = bst.in_order().filter(lambda x: x > 50)
    print(f"    {large}")

    print(f"\n>>> Paginated (page_size=5)")
    pager = bst.paginated(page_size=5)
    print(f"    Total: {pager.total_items} items | {pager.total_pages} pages")
    for p in range(1, pager.total_pages + 1):
        print(f"    Page {p}: {pager.page(p)}")

    print(f"\n>>> Lazy range (0..20, step=3, filter even)")
    lazy = LazyRange(0, 20, 3)
    print(f"    All:    {list(lazy)}")
    print(f"    Even:   {list(lazy.filter(lambda x: x % 2 == 0))}")


if __name__ == "__main__":
    main()
