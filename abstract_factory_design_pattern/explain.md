# Abstract Factory Design Pattern

## What is it?

Abstract Factory is a creational pattern that provides an interface for creating **families of related objects** without specifying their concrete classes. Think of it as a factory of factories — each concrete factory produces a consistent set of related products.

## When to Use

- You need to create families of related objects that must be used together
- You want to enforce consistency among products (e.g., all UI components match the same theme)
- You want to swap entire product families without changing client code

## Structure

```
AbstractFactory
  ├── create_product_a() → AbstractProductA
  └── create_product_b() → AbstractProductB

ConcreteFactory1 → ProductA1, ProductB1
ConcreteFactory2 → ProductA2, ProductB2
```

## Abstract Factory vs Factory Method

| | Factory Method | Abstract Factory |
|---|---|---|
| Creates | One product | A family of products |
| How | Subclassing | Composition |
| Scope | Single product hierarchy | Multiple product hierarchies |

## Example in `abstract_factory.py`

A cross-platform UI toolkit — Windows, macOS, Linux themes. Each factory produces a consistent set: Button, Checkbox, TextInput, ScrollBar. Swap the factory and the entire UI family changes.
