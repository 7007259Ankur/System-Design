"""
Command Design Pattern - Advanced Implementation
Real-world scenario: Text Editor with Undo/Redo
Every user action is a Command object — stored, executed,
undone, redone, and grouped into macros.
"""

from __future__ import annotations
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Receiver — the object that actually does the work
# ---------------------------------------------------------------------------

class TextEditor:
    """
    The Receiver. Contains the document state and low-level operations.
    Commands call these methods — it knows nothing about Command objects.
    """

    def __init__(self, initial_text: str = ""):
        self._text = initial_text
        self._cursor = len(initial_text)
        self._clipboard: str = ""
        self._format_tags: list[tuple[int, int, str]] = []  # (start, end, tag)

    # --- Core operations (called by commands) ---

    def insert(self, position: int, text: str) -> None:
        self._text = self._text[:position] + text + self._text[position:]
        self._cursor = position + len(text)

    def delete(self, position: int, length: int) -> str:
        deleted = self._text[position:position + length]
        self._text = self._text[:position] + self._text[position + length:]
        self._cursor = position
        return deleted

    def replace(self, position: int, length: int, new_text: str) -> str:
        old_text = self._text[position:position + length]
        self._text = self._text[:position] + new_text + self._text[position + length:]
        self._cursor = position + len(new_text)
        return old_text

    def add_format(self, start: int, end: int, tag: str) -> None:
        self._format_tags.append((start, end, tag))

    def remove_format(self, start: int, end: int, tag: str) -> None:
        self._format_tags = [
            t for t in self._format_tags
            if not (t[0] == start and t[1] == end and t[2] == tag)
        ]

    def move_cursor(self, position: int) -> int:
        old = self._cursor
        self._cursor = max(0, min(len(self._text), position))
        return old

    def copy_to_clipboard(self, start: int, end: int) -> None:
        self._clipboard = self._text[start:end]

    # --- State accessors ---

    @property
    def text(self) -> str:
        return self._text

    @property
    def cursor(self) -> int:
        return self._cursor

    @property
    def clipboard(self) -> str:
        return self._clipboard

    def display(self) -> None:
        cursor_text = self._text[:self._cursor] + "│" + self._text[self._cursor:]
        print(f'\n  Document: "{cursor_text}"')
        if self._format_tags:
            print(f"  Formats:  {self._format_tags}")
        print(f"  Length:   {len(self._text)} chars | Cursor: {self._cursor}\n")


# ---------------------------------------------------------------------------
# Command Interface
# ---------------------------------------------------------------------------

class Command(ABC):
    def __init__(self):
        self.timestamp = datetime.now()
        self._executed = False

    @abstractmethod
    def execute(self) -> None:
        ...

    @abstractmethod
    def undo(self) -> None:
        ...

    @property
    def name(self) -> str:
        return self.__class__.__name__

    def __str__(self) -> str:
        return f"{self.name} @ {self.timestamp.strftime('%H:%M:%S.%f')[:-3]}"


# ---------------------------------------------------------------------------
# Concrete Commands
# ---------------------------------------------------------------------------

class InsertTextCommand(Command):
    def __init__(self, editor: TextEditor, position: int, text: str):
        super().__init__()
        self._editor = editor
        self._position = position
        self._text = text

    def execute(self) -> None:
        self._editor.insert(self._position, self._text)
        logger.info(f"INSERT '{self._text}' at pos {self._position}")
        self._executed = True

    def undo(self) -> None:
        self._editor.delete(self._position, len(self._text))
        logger.info(f"UNDO INSERT '{self._text}' at pos {self._position}")

    @property
    def name(self) -> str:
        return f"Insert('{self._text[:20]}')"


class DeleteTextCommand(Command):
    def __init__(self, editor: TextEditor, position: int, length: int):
        super().__init__()
        self._editor = editor
        self._position = position
        self._length = length
        self._deleted_text: str = ""

    def execute(self) -> None:
        self._deleted_text = self._editor.delete(self._position, self._length)
        logger.info(f"DELETE {self._length} chars at pos {self._position} → '{self._deleted_text}'")
        self._executed = True

    def undo(self) -> None:
        self._editor.insert(self._position, self._deleted_text)
        logger.info(f"UNDO DELETE → restored '{self._deleted_text}' at pos {self._position}")

    @property
    def name(self) -> str:
        return f"Delete({self._length} chars)"


class ReplaceTextCommand(Command):
    def __init__(self, editor: TextEditor, position: int, length: int, new_text: str):
        super().__init__()
        self._editor = editor
        self._position = position
        self._length = length
        self._new_text = new_text
        self._old_text: str = ""

    def execute(self) -> None:
        self._old_text = self._editor.replace(self._position, self._length, self._new_text)
        logger.info(f"REPLACE '{self._old_text}' → '{self._new_text}' at pos {self._position}")
        self._executed = True

    def undo(self) -> None:
        self._editor.replace(self._position, len(self._new_text), self._old_text)
        logger.info(f"UNDO REPLACE → restored '{self._old_text}'")

    @property
    def name(self) -> str:
        return f"Replace('{self._old_text[:15]}' → '{self._new_text[:15]}')"


class FormatTextCommand(Command):
    def __init__(self, editor: TextEditor, start: int, end: int, tag: str):
        super().__init__()
        self._editor = editor
        self._start = start
        self._end = end
        self._tag = tag

    def execute(self) -> None:
        self._editor.add_format(self._start, self._end, self._tag)
        logger.info(f"FORMAT [{self._start}:{self._end}] with <{self._tag}>")
        self._executed = True

    def undo(self) -> None:
        self._editor.remove_format(self._start, self._end, self._tag)
        logger.info(f"UNDO FORMAT [{self._start}:{self._end}] <{self._tag}>")

    @property
    def name(self) -> str:
        return f"Format(<{self._tag}> [{self._start}:{self._end}])"


class MoveCursorCommand(Command):
    def __init__(self, editor: TextEditor, position: int):
        super().__init__()
        self._editor = editor
        self._position = position
        self._previous_position: int = 0

    def execute(self) -> None:
        self._previous_position = self._editor.move_cursor(self._position)
        logger.info(f"MOVE CURSOR {self._previous_position} → {self._editor.cursor}")
        self._executed = True

    def undo(self) -> None:
        self._editor.move_cursor(self._previous_position)
        logger.info(f"UNDO MOVE CURSOR → {self._previous_position}")

    @property
    def name(self) -> str:
        return f"MoveCursor(→ {self._position})"


# ---------------------------------------------------------------------------
# Macro Command — composite: groups multiple commands into one undoable unit
# ---------------------------------------------------------------------------

class MacroCommand(Command):
    """
    Composite Command. Executes a sequence of commands as a single unit.
    Undo reverses them in reverse order.
    """

    def __init__(self, name: str, commands: list[Command]):
        super().__init__()
        self._name = name
        self._commands = commands

    def execute(self) -> None:
        logger.info(f"MACRO '{self._name}' — executing {len(self._commands)} commands")
        for cmd in self._commands:
            cmd.execute()
        self._executed = True

    def undo(self) -> None:
        logger.info(f"MACRO '{self._name}' — undoing {len(self._commands)} commands")
        for cmd in reversed(self._commands):
            cmd.undo()

    @property
    def name(self) -> str:
        return f"Macro('{self._name}')"


# ---------------------------------------------------------------------------
# Invoker — manages execution, history, undo/redo stacks
# ---------------------------------------------------------------------------

class EditorInvoker:
    """
    The Invoker. Executes commands and maintains undo/redo history.
    Knows nothing about what the commands actually do.
    """

    def __init__(self, max_history: int = 50):
        self._undo_stack: list[Command] = []
        self._redo_stack: list[Command] = []
        self._max_history = max_history
        self._execution_log: list[str] = []

    def execute(self, command: Command) -> None:
        command.execute()
        self._undo_stack.append(command)
        self._redo_stack.clear()  # new action clears redo history
        self._execution_log.append(f"EXEC  {command}")
        if len(self._undo_stack) > self._max_history:
            self._undo_stack.pop(0)

    def undo(self) -> Optional[Command]:
        if not self._undo_stack:
            logger.warning("Nothing to undo.")
            return None
        command = self._undo_stack.pop()
        command.undo()
        self._redo_stack.append(command)
        self._execution_log.append(f"UNDO  {command}")
        return command

    def redo(self) -> Optional[Command]:
        if not self._redo_stack:
            logger.warning("Nothing to redo.")
            return None
        command = self._redo_stack.pop()
        command.execute()
        self._undo_stack.append(command)
        self._execution_log.append(f"REDO  {command}")
        return command

    def undo_all(self) -> None:
        logger.info(f"Undoing all {len(self._undo_stack)} commands...")
        while self._undo_stack:
            self.undo()

    def print_history(self) -> None:
        print("\n--- Command History ---")
        for entry in self._execution_log:
            print(f"  {entry}")
        print(f"\n  Undo stack: {len(self._undo_stack)} | Redo stack: {len(self._redo_stack)}")
        print("-----------------------")


# ---------------------------------------------------------------------------
# Demo
# ---------------------------------------------------------------------------

def main():
    print("=" * 55)
    print("  Command Pattern — Text Editor with Undo/Redo")
    print("=" * 55)

    editor = TextEditor()
    invoker = EditorInvoker()

    # --- Basic operations ---
    print("\n>>> Basic insert, delete, replace")

    invoker.execute(InsertTextCommand(editor, 0, "Hello, World!"))
    editor.display()

    invoker.execute(InsertTextCommand(editor, 7, "Beautiful "))
    editor.display()

    invoker.execute(DeleteTextCommand(editor, 0, 6))  # remove "Hello,"
    editor.display()

    invoker.execute(ReplaceTextCommand(editor, 0, 1, "A"))  # " " → "A"
    editor.display()

    # --- Formatting ---
    print(">>> Applying formatting")
    invoker.execute(FormatTextCommand(editor, 0, 9, "bold"))
    invoker.execute(FormatTextCommand(editor, 2, 7, "italic"))
    editor.display()

    # --- Undo / Redo ---
    print(">>> Undo last 3 actions")
    invoker.undo()
    invoker.undo()
    invoker.undo()
    editor.display()

    print(">>> Redo 2 actions")
    invoker.redo()
    invoker.redo()
    editor.display()

    # --- Macro command ---
    print(">>> Macro: 'Heading Style' (insert + format + move cursor)")
    macro = MacroCommand("Heading Style", [
        InsertTextCommand(editor, 0, "# "),
        FormatTextCommand(editor, 0, len(editor.text) + 2, "h1"),
        MoveCursorCommand(editor, 0),
    ])
    invoker.execute(macro)
    editor.display()

    print(">>> Undo the entire macro in one step")
    invoker.undo()
    editor.display()

    # --- Full history ---
    invoker.print_history()


if __name__ == "__main__":
    main()
