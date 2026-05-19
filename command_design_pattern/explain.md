# Command Design Pattern

## What is it?

The Command pattern is a behavioral design pattern that turns a request into a standalone object containing all the information about that request. This lets you parameterize methods with different requests, delay or queue execution, and support undoable operations.

In short: wrap actions in objects so you can store, pass, queue, and reverse them.

## When to Use

- You need undo/redo functionality
- You want to queue or schedule operations
- You need to log or audit every action taken
- You want to support transactional behavior (do/rollback)
- You want to decouple the sender of a request from the object that handles it

## Structure

```
Client → Invoker → Command (interface)
                      └── execute()
                      └── undo()
                   ConcreteCommandA → Receiver
                   ConcreteCommandB → Receiver
```

- Command: Interface with `execute()` and `undo()`
- ConcreteCommand: Implements the command, holds reference to Receiver
- Receiver: The object that actually does the work
- Invoker: Triggers commands, maintains history for undo/redo
- Client: Creates and configures command objects

## Command vs Strategy vs Chain of Responsibility

| | Command | Strategy | Chain of Responsibility |
|---|---|---|---|
| Purpose | Encapsulate a request as object | Swap algorithms | Pass request along a chain |
| Undo support | Yes | No | No |
| History/queue | Yes | No | No |
| Decouples | Sender from receiver | Context from algorithm | Sender from handler |

## Real-World Analogy

A restaurant order. The waiter (Invoker) takes your order (Command) and passes it to the kitchen (Receiver). The order slip is a command object — it can be queued, re-executed, or cancelled. The waiter doesn't cook; the kitchen doesn't take orders directly.

## Pros

- Single Responsibility: Decouple classes that invoke operations from classes that perform them
- Open/Closed: Add new commands without changing existing code
- Undo/redo, transaction rollback, and operation queuing come naturally
- Commands can be serialized and stored

## Cons

- Code can get complex with many small command classes
- Overkill for simple one-off operations

## Example in `command.py`

Models a text editor with full undo/redo support:
- `TextEditor` is the Receiver — holds the document state
- Commands: `InsertTextCommand`, `DeleteTextCommand`, `ReplaceTextCommand`, `FormatTextCommand`, `MoveCarsorCommand`
- `EditorInvoker` maintains a history stack for undo/redo
- `MacroCommand` groups multiple commands into one (composite command)
- Includes command history log, batch execution, and transaction rollback
