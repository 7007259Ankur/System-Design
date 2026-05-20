# Observer Design Pattern

## What is it?

Observer is a behavioral pattern that defines a one-to-many dependency between objects. When one object (subject/publisher) changes state, all its dependents (observers/subscribers) are notified and updated automatically.

## When to Use

- Changes to one object require changing others, and you don't know how many
- An object should notify other objects without assumptions about who they are
- You need an event system or pub/sub mechanism

## Structure

```
Subject (Publisher)
  ├── attach(observer)
  ├── detach(observer)
  └── notify() → observer.update()

Observer (Subscriber)
  └── update(event)
```

## Observer vs Mediator

| | Observer | Mediator |
|---|---|---|
| Coupling | Publisher doesn't know subscribers | All know the mediator |
| Direction | One-to-many | Many-to-many |
| Use case | Events/notifications | Coordination |

## Example in `observer.py`

A stock market system — stocks publish price changes, multiple subscribers react: PriceAlertObserver, PortfolioTracker, TradingBot, AuditLogger. Supports typed events, priority subscribers, and one-time subscriptions.
