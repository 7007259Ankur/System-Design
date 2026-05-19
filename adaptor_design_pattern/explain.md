# Adapter Design Pattern

## What is it?

The Adapter pattern is a structural design pattern that allows objects with incompatible interfaces to work together. It acts as a bridge between two incompatible interfaces — like a power adapter that lets you plug a US device into a European socket.

## When to Use

- You want to use an existing class but its interface doesn't match what you need
- You want to create a reusable class that cooperates with classes that don't have compatible interfaces
- You need to integrate third-party or legacy code without modifying it

## Structure

```
Client → Target Interface → Adapter → Adaptee
```

- Target: The interface the client expects
- Adaptee: The existing class with an incompatible interface
- Adapter: Wraps the Adaptee and translates calls to the Target interface
- Client: Works with the Target interface

## Types

### 1. Object Adapter (uses composition)
The adapter holds a reference to the adaptee object and delegates calls to it.

### 2. Class Adapter (uses multiple inheritance)
The adapter inherits from both the target and the adaptee. Python supports this via multiple inheritance.

## Real-World Analogy

Think of a payment gateway integration. Your app expects a unified `pay()` method, but each payment provider (Stripe, PayPal, Razorpay) has its own SDK with different method names and signatures. The Adapter wraps each provider and exposes a consistent interface to your app.

## Pros

- Single Responsibility Principle: Separates interface conversion from business logic
- Open/Closed Principle: Add new adapters without breaking existing code
- Works with legacy code without modifying it

## Cons

- Increases overall code complexity
- Sometimes it's simpler to just change the service class to match the interface

## Example in `adaptor.py`

The code demonstrates a real-world payment processing system where:
- Multiple payment providers (Stripe, PayPal, Razorpay) each have different APIs
- An `PaymentAdapter` interface unifies them
- A `PaymentProcessor` client works with any provider through the adapter
- Includes logging, error handling, transaction history, and a factory pattern
