"""
Composite Design Pattern - Advanced Implementation
Real-world scenario: File System
Files and Directories implement the same interface.
Traverse, calculate size, search, and delete recursively.
"""
from __future__ import annotations
import fnmatch
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


# ---------------------------------------------------------------------------
# Component Interface
# ---------------------------------------------------------------------------

class FileSystemNode(ABC):
    def __init__(self, name: str):
        self.name = name
        self.created_at = datetime.now()
        self._parent: Optional[Directory] = None

    @abstractmethod
    def size(self) -> int: ...

    @abstractmethod
    def display(self, indent: int = 0) -> None: ...

    @abstractmethod
    def search(self, pattern: str) -> list[FileSystemNode]: ...

    @abstractmethod
    def node_count(self) -> int: ...

    @property
    def path(self) -> str:
        if self._parent is None:
            return self.name
        return f"{self._parent.path}/{self.name}"

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.name})"


# ---------------------------------------------------------------------------
# Leaf
# ---------------------------------------------------------------------------

class File(FileSystemNode):
    def __init__(self, name: str, content: str = "", size_bytes: Optional[int] = None):
        super().__init__(name)
        self.content = content
        self._size = size_bytes if size_bytes is not None else len(content.encode())
        self.extension = name.rsplit(".", 1)[-1] if "." in name else ""

    def size(self) -> int:
        return self._size

    def display(self, indent: int = 0) -> None:
        size_str = self._format_size(self._size)
        print(f"{'  ' * indent}[FILE] {self.name} ({size_str})")

    def search(self, pattern: str) -> list[FileSystemNode]:
        return [self] if fnmatch.fnmatch(self.name, pattern) else []

    def node_count(self) -> int:
        return 1

    @staticmethod
    def _format_size(size: int) -> str:
        for unit in ["B", "KB", "MB", "GB"]:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} TB"


# ---------------------------------------------------------------------------
# Composite
# ---------------------------------------------------------------------------

class Directory(FileSystemNode):
    def __init__(self, name: str):
        super().__init__(name)
        self._children: list[FileSystemNode] = []

    def add(self, *nodes: FileSystemNode) -> Directory:
        for node in nodes:
            node._parent = self
            self._children.append(node)
        return self

    def remove(self, name: str) -> Optional[FileSystemNode]:
        for i, child in enumerate(self._children):
            if child.name == name:
                child._parent = None
                return self._children.pop(i)
        return None

    def get(self, name: str) -> Optional[FileSystemNode]:
        for child in self._children:
            if child.name == name:
                return child
        return None

    def size(self) -> int:
        return sum(child.size() for child in self._children)

    def display(self, indent: int = 0) -> None:
        size_str = File._format_size(self.size())
        print(f"{'  ' * indent}[DIR] {self.name}/ ({size_str}, {len(self._children)} items)")
        for child in self._children:
            child.display(indent + 1)

    def search(self, pattern: str) -> list[FileSystemNode]:
        results = []
        if fnmatch.fnmatch(self.name, pattern):
            results.append(self)
        for child in self._children:
            results.extend(child.search(pattern))
        return results

    def node_count(self) -> int:
        return 1 + sum(child.node_count() for child in self._children)

    def list_by_extension(self, ext: str) -> list[File]:
        results = []
        for child in self._children:
            if isinstance(child, File) and child.extension == ext:
                results.append(child)
            elif isinstance(child, Directory):
                results.extend(child.list_by_extension(ext))
        return results

    def total_files(self) -> int:
        count = 0
        for child in self._children:
            if isinstance(child, File):
                count += 1
            elif isinstance(child, Directory):
                count += child.total_files()
        return count

    @property
    def children(self) -> list[FileSystemNode]:
        return list(self._children)


# ---------------------------------------------------------------------------
# Demo
# ---------------------------------------------------------------------------

def main():
    print("=" * 55)
    print("  Composite Pattern — File System Demo")
    print("=" * 55)

    # Build a file system tree
    root = Directory("project")
    root.add(
        File("README.md", "# My Project\nA design patterns demo.", 1024),
        File("requirements.txt", "flask\nsqlalchemy\npytest", 512),
    )

    src = Directory("src")
    src.add(
        File("main.py", "from app import create_app", 2048),
        File("config.py", "DEBUG = True\nDB_URL = '...'", 1536),
    )

    models = Directory("models")
    models.add(
        File("user.py", "class User: ...", 4096),
        File("product.py", "class Product: ...", 3072),
        File("order.py", "class Order: ...", 5120),
    )
    src.add(models)

    tests = Directory("tests")
    tests.add(
        File("test_user.py", "def test_create_user(): ...", 2048),
        File("test_product.py", "def test_product(): ...", 1024),
        File("conftest.py", "import pytest", 512),
    )

    static = Directory("static")
    css = Directory("css")
    css.add(File("main.css", "body { margin: 0; }", 8192))
    js = Directory("js")
    js.add(
        File("app.js", "const app = {};", 16384),
        File("utils.js", "export const fmt = () => {};", 4096),
    )
    static.add(css, js)

    root.add(src, tests, static)

    # Display tree
    print("\n>>> File system tree")
    root.display()

    # Stats — uniform interface on both files and directories
    print(f"\n>>> Stats")
    print(f"  Total size:  {File._format_size(root.size())}")
    print(f"  Total nodes: {root.node_count()}")
    print(f"  Total files: {root.total_files()}")

    # Search
    print("\n>>> Search for '*.py' files")
    py_files = root.search("*.py")
    for f in py_files:
        print(f"  {f.path}")

    print("\n>>> Search for 'test_*'")
    test_files = root.search("test_*")
    for f in test_files:
        print(f"  {f.path}")

    # List by extension
    print("\n>>> All .js files")
    js_files = root.list_by_extension("js")
    for f in js_files:
        print(f"  {f.path} ({File._format_size(f.size())})")

    # Remove a node
    print("\n>>> Remove 'conftest.py' from tests/")
    removed = tests.remove("conftest.py")
    print(f"  Removed: {removed}")
    print(f"  Tests dir now has {len(tests.children)} items")


if __name__ == "__main__":
    main()
