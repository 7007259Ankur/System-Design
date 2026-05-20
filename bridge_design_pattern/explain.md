# Bridge Design Pattern

## What is it?

Bridge is a structural pattern that splits a large class (or set of closely related classes) into two separate hierarchies — abstraction and implementation — which can be developed independently.

The key idea: prefer composition over inheritance to avoid an exponential class explosion.

## When to Use

- You want to avoid a permanent binding between abstraction and implementation
- Both abstraction and implementation should be extensible via subclassing
- Changes in implementation should not affect client code
- You have a class explosion from combining multiple dimensions (e.g., Shape × Color × Platform)

## Structure

```
Abstraction ──────────────→ Implementor (interface)
  └── refined_operation()      └── operation_impl()

RefinedAbstraction        ConcreteImplementorA
                          ConcreteImplementorB
```

## Bridge vs Adapter

| | Bridge | Adapter |
|---|---|---|
| Intent | Designed upfront to separate concerns | Retrofitted to make incompatible things work |
| Timing | Design time | After the fact |

## Example in `bridge.py`

A rendering engine — shapes (Circle, Rectangle, Triangle) × renderers (SVGRenderer, CanvasRenderer, ASCIIRenderer). Add new shapes or renderers independently without touching existing code.
