# State Design Pattern

## What is it?

The State pattern is a behavioral design pattern that lets an object alter its behavior when its internal state changes. The object will appear to change its class. Instead of giant if/elif chains checking state, each state is its own class with its own behavior.

## When to Use

- An object's behavior depends on its state and must change at runtime
- You have large conditionals that switch behavior based on state
- State transitions have complex rules that need to be encapsulated
- You're modeling a finite state machine (FSM)

## Structure

```
Context --> State (interface)
              +--> ConcreteStateA (handle(), on_enter(), on_exit())
              +--> ConcreteStateB
              +--> ConcreteStateC
```

- Context: Holds a reference to the current state, delegates behavior to it
- State: Interface declaring methods for each action
- ConcreteState: Implements behavior for that specific state, triggers transitions

## Real-World Analogy

A vending machine. It behaves differently depending on whether it's idle, has money inserted, is dispensing, or is out of stock. Each state handles button presses differently.

## Pros

- Eliminates large conditionals
- Each state is isolated — easy to add new states
- State transitions are explicit and traceable

## Cons

- Can be overkill for simple state machines
- Many small classes if states are numerous

## Example in `state.py`

Models an order lifecycle: `Pending -> Confirmed -> Processing -> Shipped -> Delivered` (or `Cancelled`/`Refunded`). Each state controls which transitions are valid and what actions are allowed.
