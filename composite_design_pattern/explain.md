# Composite Design Pattern

## What is it?

Composite is a structural pattern that lets you compose objects into tree structures and then work with these structures as if they were individual objects. Clients treat individual objects and compositions uniformly.

## When to Use

- You need to represent part-whole hierarchies (file systems, UI trees, org charts)
- You want clients to treat individual objects and groups of objects the same way
- You need recursive tree structures

## Structure

```
Component (interface)
  ├── Leaf          — no children, does the actual work
  └── Composite     — has children, delegates to them
        └── children: list[Component]
```

## Example in `composite.py`

A file system — Files and Directories. Both implement the same interface. Calculate size, search, list, and delete recursively. A directory containing directories containing files — all treated uniformly.
