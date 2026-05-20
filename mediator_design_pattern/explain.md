# Mediator Design Pattern

## What is it?

Mediator is a behavioral pattern that reduces chaotic dependencies between objects by making them communicate indirectly through a mediator object. Instead of objects referring to each other directly, they all talk to the mediator.

## When to Use

- Many objects communicate in complex ways, creating tight coupling
- Reusing a component is difficult because it refers to many other components
- You find yourself creating many subclasses just to reuse behavior in different contexts

## Structure

```
ComponentA ──→ Mediator ←── ComponentB
ComponentC ──→           ←── ComponentD
```

Without mediator: O(n²) connections
With mediator: O(n) connections

## Mediator vs Observer

| | Mediator | Observer |
|---|---|---|
| Direction | Bidirectional coordination | One-to-many notification |
| Coupling | Components know mediator | Publishers don't know subscribers |
| Use case | Orchestration | Event broadcasting |

## Example in `mediator.py`

An air traffic control system — Aircraft communicate only through the ATC tower (mediator). The tower coordinates landing, takeoff, and runway assignments. Aircraft never talk to each other directly.
