"""
Abstract Factory Design Pattern - Advanced Implementation
Real-world scenario: Cross-platform UI Component Toolkit
Each factory produces a consistent family of UI widgets.
Swap the factory and the entire UI theme changes.
"""
from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass


# ---------------------------------------------------------------------------
# Abstract Products
# ---------------------------------------------------------------------------

class Button(ABC):
    @abstractmethod
    def render(self) -> str: ...
    @abstractmethod
    def on_click(self, handler: str) -> str: ...

class Checkbox(ABC):
    @abstractmethod
    def render(self) -> str: ...
    @abstractmethod
    def toggle(self) -> str: ...

class TextInput(ABC):
    @abstractmethod
    def render(self) -> str: ...
    @abstractmethod
    def validate(self, value: str) -> bool: ...

class ScrollBar(ABC):
    @abstractmethod
    def render(self) -> str: ...
    @abstractmethod
    def scroll(self, delta: int) -> str: ...


# ---------------------------------------------------------------------------
# Windows Family
# ---------------------------------------------------------------------------

class WindowsButton(Button):
    def render(self) -> str:
        return "[Windows Button: ▓▓▓▓▓▓]"
    def on_click(self, handler: str) -> str:
        return f"Windows WM_CLICK -> {handler}()"

class WindowsCheckbox(Checkbox):
    def __init__(self): self._checked = False
    def render(self) -> str:
        return f"[Windows Checkbox: {'☑' if self._checked else '☐'}]"
    def toggle(self) -> str:
        self._checked = not self._checked
        return f"Windows checkbox -> {'checked' if self._checked else 'unchecked'}"

class WindowsTextInput(TextInput):
    def render(self) -> str:
        return "[Windows TextInput: ==============]"
    def validate(self, value: str) -> bool:
        return len(value) <= 255

class WindowsScrollBar(ScrollBar):
    def __init__(self): self._position = 0
    def render(self) -> str:
        return f"[Windows ScrollBar: pos={self._position}]"
    def scroll(self, delta: int) -> str:
        self._position = max(0, self._position + delta)
        return f"Windows scroll -> position {self._position}"


# ---------------------------------------------------------------------------
# macOS Family
# ---------------------------------------------------------------------------

class MacOSButton(Button):
    def render(self) -> str:
        return "( macOS Button *)"
    def on_click(self, handler: str) -> str:
        return f"macOS NSButton action -> {handler}()"

class MacOSCheckbox(Checkbox):
    def __init__(self): self._checked = False
    def render(self) -> str:
        return f"( macOS Checkbox {'OK' if self._checked else '○'} )"
    def toggle(self) -> str:
        self._checked = not self._checked
        return f"macOS checkbox -> {'on' if self._checked else 'off'}"

class MacOSTextInput(TextInput):
    def render(self) -> str:
        return "( macOS TextField: ------------ )"
    def validate(self, value: str) -> bool:
        return len(value) <= 1024

class MacOSScrollBar(ScrollBar):
    def __init__(self): self._position = 0
    def render(self) -> str:
        return f"( macOS ScrollBar: {self._position}% )"
    def scroll(self, delta: int) -> str:
        self._position = max(0, min(100, self._position + delta))
        return f"macOS elastic scroll -> {self._position}%"


# ---------------------------------------------------------------------------
# Linux Family
# ---------------------------------------------------------------------------

class LinuxButton(Button):
    def render(self) -> str:
        return "<Linux Button [GTK]>"
    def on_click(self, handler: str) -> str:
        return f"GTK g_signal_connect -> {handler}()"

class LinuxCheckbox(Checkbox):
    def __init__(self): self._checked = False
    def render(self) -> str:
        return f"<Linux Checkbox [{'X' if self._checked else ' '}]>"
    def toggle(self) -> str:
        self._checked = not self._checked
        return f"GTK toggle -> {self._checked}"

class LinuxTextInput(TextInput):
    def render(self) -> str:
        return "<Linux GtkEntry: |____________|>"
    def validate(self, value: str) -> bool:
        return bool(value.strip())

class LinuxScrollBar(ScrollBar):
    def __init__(self): self._position = 0
    def render(self) -> str:
        return f"<Linux GtkScrollbar: {self._position}>"
    def scroll(self, delta: int) -> str:
        self._position = max(0, self._position + delta)
        return f"GTK scroll-value-changed -> {self._position}"


# ---------------------------------------------------------------------------
# Abstract Factory
# ---------------------------------------------------------------------------

class UIFactory(ABC):
    @abstractmethod
    def create_button(self) -> Button: ...
    @abstractmethod
    def create_checkbox(self) -> Checkbox: ...
    @abstractmethod
    def create_text_input(self) -> TextInput: ...
    @abstractmethod
    def create_scrollbar(self) -> ScrollBar: ...

    @property
    @abstractmethod
    def theme_name(self) -> str: ...


# ---------------------------------------------------------------------------
# Concrete Factories
# ---------------------------------------------------------------------------

class WindowsUIFactory(UIFactory):
    theme_name = "Windows 11"
    def create_button(self) -> Button: return WindowsButton()
    def create_checkbox(self) -> Checkbox: return WindowsCheckbox()
    def create_text_input(self) -> TextInput: return WindowsTextInput()
    def create_scrollbar(self) -> ScrollBar: return WindowsScrollBar()

class MacOSUIFactory(UIFactory):
    theme_name = "macOS Sonoma"
    def create_button(self) -> Button: return MacOSButton()
    def create_checkbox(self) -> Checkbox: return MacOSCheckbox()
    def create_text_input(self) -> TextInput: return MacOSTextInput()
    def create_scrollbar(self) -> ScrollBar: return MacOSScrollBar()

class LinuxUIFactory(UIFactory):
    theme_name = "Linux GTK4"
    def create_button(self) -> Button: return LinuxButton()
    def create_checkbox(self) -> Checkbox: return LinuxCheckbox()
    def create_text_input(self) -> TextInput: return LinuxTextInput()
    def create_scrollbar(self) -> ScrollBar: return LinuxScrollBar()


# ---------------------------------------------------------------------------
# Client — Application uses only the abstract factory interface
# ---------------------------------------------------------------------------

class LoginForm:
    """Client code — works with any UI factory without knowing concrete classes."""

    def __init__(self, factory: UIFactory):
        self._factory = factory
        self._submit_btn = factory.create_button()
        self._remember_me = factory.create_checkbox()
        self._username = factory.create_text_input()
        self._password = factory.create_text_input()
        self._scrollbar = factory.create_scrollbar()

    def render(self) -> None:
        print(f"\n  -- Login Form [{self._factory.theme_name}] --")
        print(f"  Username:    {self._username.render()}")
        print(f"  Password:    {self._password.render()}")
        print(f"  Remember me: {self._remember_me.render()}")
        print(f"  Submit:      {self._submit_btn.render()}")
        print(f"  Scroll:      {self._scrollbar.render()}")

    def submit(self, username: str, password: str) -> None:
        if not self._username.validate(username):
            print("  X Invalid username")
            return
        print(f"  {self._submit_btn.on_click('on_login')}")
        print(f"  {self._remember_me.toggle()}")
        print(f"  {self._scrollbar.scroll(10)}")
        print(f"  OK Submitted as '{username}'")


# ---------------------------------------------------------------------------
# Factory selector
# ---------------------------------------------------------------------------

def get_factory(platform: str) -> UIFactory:
    factories = {
        "windows": WindowsUIFactory(),
        "macos": MacOSUIFactory(),
        "linux": LinuxUIFactory(),
    }
    return factories.get(platform.lower(), LinuxUIFactory())


def main():
    print("=" * 50)
    print("  Abstract Factory — Cross-Platform UI Demo")
    print("=" * 50)

    for platform in ["windows", "macos", "linux"]:
        factory = get_factory(platform)
        form = LoginForm(factory)
        form.render()
        form.submit("user@example.com", "secret")


if __name__ == "__main__":
    main()
