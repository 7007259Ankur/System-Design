# Decorator Design Pattern

## What is it?

Decorator is a structural pattern that attaches new behaviors to objects by wrapping them in decorator objects. It's a flexible alternative to subclassing for extending functionality.

## When to Use

- You want to add behavior to individual objects without affecting others
- Subclassing would lead to an explosion of classes for every combination
- You need to add/remove responsibilities at runtime

## Structure

```
Component (interface)
  ├── ConcreteComponent   — the base object
  └── BaseDecorator       — wraps a Component
        └── ConcreteDecoratorA
        └── ConcreteDecoratorB
```

Decorators can be stacked: `DecoratorA(DecoratorB(ConcreteComponent()))`

## Decorator vs Inheritance

| | Decorator | Inheritance |
|---|---|---|
| When applied | Runtime | Compile time |
| Combinations | Any stack | Fixed hierarchy |
| Flexibility | High | Low |

## Example in `decorator.py`

A data pipeline — read/write streams with encryption, compression, buffering, and logging decorators. Stack them in any order at runtime.
