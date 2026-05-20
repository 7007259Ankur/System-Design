# Builder Design Pattern

## What is it?

Builder is a creational pattern that constructs complex objects step by step. It separates the construction process from the representation, so the same construction process can produce different representations.

## When to Use

- Object construction requires many steps or configurations
- You want to construct different representations of the same object
- You need to avoid "telescoping constructors" (constructors with many parameters)
- Construction must be done in a specific order

## Structure

```
Director → Builder (interface)
              └── build_part_a()
              └── build_part_b()
              └── get_result()

ConcreteBuilderX → ProductX
ConcreteBuilderY → ProductY
```

## Builder vs Factory

| | Builder | Factory |
|---|---|---|
| Focus | Step-by-step construction | Single-step creation |
| Result | Complex object built incrementally | Object returned immediately |
| Control | Client controls steps via Director | Factory controls everything |

## Example in `builder.py`

A query builder for SQL — SELECT, INSERT, UPDATE, DELETE. Build complex queries step by step with joins, conditions, ordering, pagination. The Director provides preset query templates.
