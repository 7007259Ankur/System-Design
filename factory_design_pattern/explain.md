# Factory Method Design Pattern

## What is it?

The Factory Method pattern is a creational design pattern that defines an interface for creating objects, but lets subclasses decide which class to instantiate. Instead of calling `new SomeClass()` directly, you call a factory method that returns the object — the caller doesn't need to know the concrete class.

## When to Use

- You don't know ahead of time what class you need to instantiate
- You want subclasses to control what objects get created
- You want to encapsulate object creation logic in one place
- You need to return different implementations based on input/config

## Structure

```
Creator (abstract)
  └── factory_method() → Product (abstract)

ConcreteCreatorA → ConcreteProductA
ConcreteCreatorB → ConcreteProductB
```

- Product: The interface for objects the factory creates
- ConcreteProduct: Actual implementations of the product
- Creator: Declares the factory method (may have a default implementation)
- ConcreteCreator: Overrides the factory method to return a specific product

## Factory Method vs Abstract Factory vs Simple Factory

| | Simple Factory | Factory Method | Abstract Factory |
|---|---|---|---|
| What | A single function/class that creates objects | Subclasses decide what to create | Families of related objects |
| Extensibility | Modify existing code | Add new subclass | Add new factory |
| Complexity | Low | Medium | High |

## Real-World Analogy

A logistics company ships by truck or ship. The base `Logistics` class has a `create_transport()` factory method. `RoadLogistics` returns a `Truck`, `SeaLogistics` returns a `Ship`. The delivery code works the same regardless of transport type.

## Pros

- Single Responsibility: Object creation is in one place
- Open/Closed Principle: Add new products without changing existing code
- Loose coupling between creator and concrete products

## Cons

- Can lead to many subclasses
- Slightly more complex than a simple constructor call

## Example in `factory.py`

Demonstrates a notification system where:
- `Notification` is the product interface
- `EmailNotification`, `SMSNotification`, `PushNotification`, `SlackNotification` are concrete products
- `NotificationFactory` is the abstract creator with a factory method
- Concrete factories produce specific notification types
- A `NotificationService` uses the factory without knowing concrete classes
- Includes priority queuing, retry logic, and delivery tracking
