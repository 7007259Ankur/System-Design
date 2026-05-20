"""
Bridge Design Pattern - Advanced Implementation
Real-world scenario: Shape Rendering Engine
Shapes and renderers evolve independently — add either without touching the other.
"""
from __future__ import annotations
import math
from abc import ABC, abstractmethod
from dataclasses import dataclass


# ---------------------------------------------------------------------------
# Implementor Interface — the rendering backend
# ---------------------------------------------------------------------------

class Renderer(ABC):
    @abstractmethod
    def render_circle(self, x: float, y: float, radius: float, color: str) -> str: ...
    @abstractmethod
    def render_rectangle(self, x: float, y: float, w: float, h: float, color: str) -> str: ...
    @abstractmethod
    def render_triangle(self, points: list[tuple], color: str) -> str: ...
    @abstractmethod
    def render_line(self, x1: float, y1: float, x2: float, y2: float, color: str) -> str: ...

    @property
    @abstractmethod
    def name(self) -> str: ...


# ---------------------------------------------------------------------------
# Concrete Implementors
# ---------------------------------------------------------------------------

class SVGRenderer(Renderer):
    name = "SVG"

    def render_circle(self, x, y, radius, color) -> str:
        return f'<circle cx="{x}" cy="{y}" r="{radius}" fill="{color}"/>'

    def render_rectangle(self, x, y, w, h, color) -> str:
        return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{color}"/>'

    def render_triangle(self, points, color) -> str:
        pts = " ".join(f"{p[0]},{p[1]}" for p in points)
        return f'<polygon points="{pts}" fill="{color}"/>'

    def render_line(self, x1, y1, x2, y2, color) -> str:
        return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}"/>'


class CanvasRenderer(Renderer):
    name = "Canvas"

    def render_circle(self, x, y, radius, color) -> str:
        return (f"ctx.beginPath(); ctx.arc({x},{y},{radius},0,2*Math.PI); "
                f"ctx.fillStyle='{color}'; ctx.fill();")

    def render_rectangle(self, x, y, w, h, color) -> str:
        return f"ctx.fillStyle='{color}'; ctx.fillRect({x},{y},{w},{h});"

    def render_triangle(self, points, color) -> str:
        p = points
        return (f"ctx.beginPath(); ctx.moveTo({p[0][0]},{p[0][1]}); "
                f"ctx.lineTo({p[1][0]},{p[1][1]}); ctx.lineTo({p[2][0]},{p[2][1]}); "
                f"ctx.closePath(); ctx.fillStyle='{color}'; ctx.fill();")

    def render_line(self, x1, y1, x2, y2, color) -> str:
        return (f"ctx.beginPath(); ctx.moveTo({x1},{y1}); ctx.lineTo({x2},{y2}); "
                f"ctx.strokeStyle='{color}'; ctx.stroke();")


class ASCIIRenderer(Renderer):
    name = "ASCII"

    def render_circle(self, x, y, radius, color) -> str:
        return f"[ASCII Circle @ ({x},{y}) r={radius} color={color}]  O"

    def render_rectangle(self, x, y, w, h, color) -> str:
        return f"[ASCII Rect @ ({x},{y}) {w}x{h} color={color}]  ▭"

    def render_triangle(self, points, color) -> str:
        return f"[ASCII Triangle pts={points} color={color}]  △"

    def render_line(self, x1, y1, x2, y2, color) -> str:
        return f"[ASCII Line ({x1},{y1})->({x2},{y2}) color={color}]  -"


# ---------------------------------------------------------------------------
# Abstraction — Shape hierarchy
# ---------------------------------------------------------------------------

class Shape(ABC):
    def __init__(self, renderer: Renderer, color: str = "black"):
        self._renderer = renderer  # Bridge to implementation
        self._color = color

    @abstractmethod
    def draw(self) -> str: ...

    @abstractmethod
    def area(self) -> float: ...

    @abstractmethod
    def perimeter(self) -> float: ...

    def set_renderer(self, renderer: Renderer) -> None:
        """Switch renderer at runtime — the bridge in action."""
        self._renderer = renderer

    def info(self) -> str:
        return (f"{self.__class__.__name__} | renderer={self._renderer.name} "
                f"| area={self.area():.2f} | perimeter={self.perimeter():.2f}")


# ---------------------------------------------------------------------------
# Refined Abstractions
# ---------------------------------------------------------------------------

class Circle(Shape):
    def __init__(self, x: float, y: float, radius: float,
                 renderer: Renderer, color: str = "blue"):
        super().__init__(renderer, color)
        self.x, self.y, self.radius = x, y, radius

    def draw(self) -> str:
        return self._renderer.render_circle(self.x, self.y, self.radius, self._color)

    def area(self) -> float:
        return math.pi * self.radius ** 2

    def perimeter(self) -> float:
        return 2 * math.pi * self.radius


class Rectangle(Shape):
    def __init__(self, x: float, y: float, width: float, height: float,
                 renderer: Renderer, color: str = "red"):
        super().__init__(renderer, color)
        self.x, self.y, self.width, self.height = x, y, width, height

    def draw(self) -> str:
        return self._renderer.render_rectangle(self.x, self.y, self.width, self.height, self._color)

    def area(self) -> float:
        return self.width * self.height

    def perimeter(self) -> float:
        return 2 * (self.width + self.height)


class Triangle(Shape):
    def __init__(self, points: list[tuple], renderer: Renderer, color: str = "green"):
        super().__init__(renderer, color)
        self.points = points

    def draw(self) -> str:
        return self._renderer.render_triangle(self.points, self._color)

    def area(self) -> float:
        p = self.points
        return abs((p[1][0]-p[0][0])*(p[2][1]-p[0][1]) - (p[2][0]-p[0][0])*(p[1][1]-p[0][1])) / 2

    def perimeter(self) -> float:
        p = self.points
        return sum(math.dist(p[i], p[(i+1) % 3]) for i in range(3))


class Line(Shape):
    def __init__(self, x1: float, y1: float, x2: float, y2: float,
                 renderer: Renderer, color: str = "black"):
        super().__init__(renderer, color)
        self.x1, self.y1, self.x2, self.y2 = x1, y1, x2, y2

    def draw(self) -> str:
        return self._renderer.render_line(self.x1, self.y1, self.x2, self.y2, self._color)

    def area(self) -> float:
        return 0.0

    def perimeter(self) -> float:
        return math.dist((self.x1, self.y1), (self.x2, self.y2))


# ---------------------------------------------------------------------------
# Demo
# ---------------------------------------------------------------------------

def main():
    print("=" * 55)
    print("  Bridge Pattern — Shape Rendering Engine Demo")
    print("=" * 55)

    renderers = [SVGRenderer(), CanvasRenderer(), ASCIIRenderer()]
    shapes_config = [
        ("Circle",    lambda r: Circle(100, 100, 50, r, "blue")),
        ("Rectangle", lambda r: Rectangle(10, 10, 200, 100, r, "red")),
        ("Triangle",  lambda r: Triangle([(150,10),(250,190),(50,190)], r, "green")),
        ("Line",      lambda r: Line(0, 0, 100, 100, r, "black")),
    ]

    for renderer in renderers:
        print(f"\n>>> Renderer: {renderer.name}")
        for name, factory in shapes_config:
            shape = factory(renderer)
            print(f"  {shape.info()}")
            print(f"    {shape.draw()}")

    # Demonstrate switching renderer at runtime
    print("\n>>> Switching renderer at runtime (Circle: SVG -> Canvas -> ASCII)")
    circle = Circle(50, 50, 30, SVGRenderer(), "purple")
    for renderer in renderers:
        circle.set_renderer(renderer)
        print(f"  [{renderer.name}] {circle.draw()}")


if __name__ == "__main__":
    main()
