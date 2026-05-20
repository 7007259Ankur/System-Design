# Strategy Design Pattern

## What is it?

The Strategy pattern is a behavioral design pattern that defines a family of algorithms, encapsulates each one, and makes them interchangeable. The strategy lets the algorithm vary independently from the clients that use it.

Instead of implementing a single algorithm directly, the context receives instructions on which algorithm to use at runtime.

## When to Use

- You want to swap algorithms or behaviors at runtime
- You have multiple variants of an algorithm and want to avoid conditionals
- You want to isolate the implementation details of an algorithm from the code that uses it
- A class defines many behaviors that appear as multiple conditionals

## Structure

```
Context --> Strategy (interface)
              +--> ConcreteStrategyA
              +--> ConcreteStrategyB
              +--> ConcreteStrategyC
```

- Strategy: Interface common to all supported algorithms
- ConcreteStrategy: Implements the algorithm
- Context: Holds a reference to a strategy, delegates the work to it

## Strategy vs Command vs Template Method

| | Strategy | Command | Template Method |
|---|---|---|---|
| Purpose | Swap algorithms | Encapsulate requests | Define skeleton, vary steps |
| Runtime swap | Yes | Yes | No (compile-time) |
| Uses | Composition | Composition | Inheritance |

## Real-World Analogy

Navigation app. You pick a route strategy: fastest, shortest, avoid tolls, cycling. The app (context) uses whichever strategy you select — the routing logic is swappable without changing the app.

## Pros

- Open/Closed: Add new strategies without changing the context
- Eliminates conditionals for algorithm selection
- Strategies can be reused across different contexts

## Cons

- Clients must be aware of different strategies to pick one
- Overkill if only a couple of algorithms exist

## Example in `strategy.py`

Models a payment checkout system with swappable:
- Sorting strategies: `BubbleSort`, `QuickSort`, `MergeSort`, `TimSort`
- Compression strategies: `GZipCompression`, `ZlibCompression`, `NoCompression`
- Discount strategies: `PercentageDiscount`, `FlatDiscount`, `BuyOneGetOne`, `NoDiscount`
All swappable at runtime with zero changes to the context.
