# Singleton Design Pattern

## What is it?

Singleton is a creational pattern that ensures a class has only one instance and provides a global access point to it. The class controls its own instantiation and prevents any other code from creating additional instances.

## When to Use

- Exactly one object is needed to coordinate actions (config, logger, connection pool)
- You need controlled access to a shared resource
- Global state needs to be managed in one place

## Pitfalls

- Makes unit testing harder (global state)
- Can hide dependencies
- Needs thread-safety in concurrent environments

## Variations

- Classic (lazy initialization)
- Thread-safe (with locks)
- Metaclass-based
- Borg pattern (shared state, multiple instances)

## Example in `singleton.py`

A thread-safe application configuration manager and a database connection pool. Demonstrates classic singleton, metaclass singleton, and thread-safety with locks.
