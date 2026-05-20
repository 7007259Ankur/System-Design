# Chain of Responsibility Design Pattern

## What is it?

Chain of Responsibility is a behavioral pattern that passes a request along a chain of handlers. Each handler decides to process the request or pass it to the next handler in the chain.

## When to Use

- More than one object may handle a request, and the handler isn't known a priori
- You want to issue a request to one of several objects without specifying the receiver explicitly
- The set of objects that can handle a request should be specified dynamically

## Structure

```
Client → Handler1 → Handler2 → Handler3 → null
           ↓           ↓           ↓
        handle()    handle()    handle()
        or pass     or pass     or stop
```

## Chain of Responsibility vs Command

| | Chain of Responsibility | Command |
|---|---|---|
| Handlers | Multiple may handle | One handles |
| Request | Passed along | Encapsulated as object |
| Result | First/any match handles | Always executed |

## Example in `chain.py`

An HTTP middleware pipeline — authentication, rate limiting, input validation, authorization, logging, and business logic handlers. Each middleware either handles/rejects the request or passes it to the next handler.
