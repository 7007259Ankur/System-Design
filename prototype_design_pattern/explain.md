# Prototype Design Pattern

## What is it?

Prototype is a creational pattern that lets you copy existing objects without making your code dependent on their classes. Instead of instantiating a new object from scratch, you clone an existing one and modify only what's needed.

## When to Use

- Object creation is expensive (DB calls, complex initialization)
- You need many similar objects with slight variations
- You want to avoid subclassing just to create variations
- The class to instantiate is specified at runtime

## Deep vs Shallow Copy

- Shallow copy: copies the object but shares references to nested objects
- Deep copy: recursively copies everything — fully independent clone

## Example in `prototype.py`

A game character system — Warriors, Mages, Archers. Clone base archetypes and customize stats, equipment, and skills. Includes a prototype registry for named archetypes and deep copy handling for nested mutable state.
