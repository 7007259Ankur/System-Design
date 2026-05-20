# Template Method Design Pattern

## What is it?

The Template Method pattern is a behavioral design pattern that defines the skeleton of an algorithm in a base class, deferring some steps to subclasses. Subclasses can override specific steps without changing the overall algorithm structure.

The base class says "here's the order of steps" — subclasses fill in the details.

## When to Use

- Multiple classes share the same algorithm structure but differ in specific steps
- You want to avoid code duplication across similar classes
- You want to control which parts of an algorithm subclasses can override
- You're implementing a framework where users extend specific hooks

## Structure

```
AbstractClass
  +-- template_method()   <- final, defines the skeleton
  +-- step1()             <- abstract, must override
  +-- step2()             <- abstract, must override
  +-- hook()              <- optional override (has default)

ConcreteClassA(AbstractClass)  <- overrides step1, step2
ConcreteClassB(AbstractClass)  <- overrides step1, step2
```

- template_method: The invariant part — calls steps in order
- Abstract steps: Must be implemented by subclasses
- Hooks: Optional overrides with default (empty) implementations

## Template Method vs Strategy

| | Template Method | Strategy |
|---|---|---|
| Mechanism | Inheritance | Composition |
| Algorithm skeleton | Fixed in base class | Defined per strategy |
| Vary steps | Override methods | Swap whole object |
| Runtime swap | No | Yes |

## Real-World Analogy

A recipe. The steps are always: prep ingredients, cook, plate, serve. But the specific cooking steps differ per dish. The recipe template is fixed; the dish-specific steps vary.

## Pros

- Eliminates code duplication — common steps live in one place
- Easy to extend — just subclass and override specific steps
- Hooks give optional customization without forcing overrides

## Cons

- Relies on inheritance — tighter coupling than Strategy
- Liskov Substitution Principle can be violated if subclasses change behavior too drastically
- Hard to follow if the template has many steps

## Example in `template_method.py`

Models a data pipeline with fixed steps: `extract -> validate -> transform -> load -> notify`. Concrete pipelines: `CSVtoDatabasePipeline`, `APItoWarehousePipeline`, `JSONtoElasticsearchPipeline` — each overrides only the steps that differ.
