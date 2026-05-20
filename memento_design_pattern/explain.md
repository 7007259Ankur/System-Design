# Memento Design Pattern

## What is it?

Memento is a behavioral pattern that lets you save and restore the previous state of an object without revealing the details of its implementation. The state is stored in a memento object that only the originator can read.

## When to Use

- You need to implement undo/redo (when Command pattern is too heavy)
- You need snapshots of an object's state
- Direct access to the object's fields would expose implementation details

## Roles

- Originator: the object whose state needs saving
- Memento: stores a snapshot of the originator's state (opaque to others)
- Caretaker: stores mementos but never inspects their contents

## Memento vs Command

| | Memento | Command |
|---|---|---|
| Stores | State snapshot | Action + reverse action |
| Undo mechanism | Restore snapshot | Execute reverse operation |
| Best for | Full state rollback | Fine-grained action reversal |

## Example in `memento.py`

A game save system — player position, health, inventory, level. Save checkpoints, restore to any previous save. Includes auto-save, named saves, and a save slot manager with metadata.
