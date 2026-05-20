# Iterator Design Pattern

## What is it?

Iterator is a behavioral pattern that lets you traverse elements of a collection without exposing its underlying representation (list, stack, tree, graph, etc.).

## When to Use

- You want a standard way to traverse different types of collections
- You want to hide the internal structure of a collection
- You need multiple simultaneous traversals of the same collection
- You want to provide different traversal strategies for the same collection

## Python Note

Python has built-in iterator protocol (`__iter__`, `__next__`). The pattern is deeply embedded in the language. This implementation shows custom iterators beyond the basics — tree traversal, filtered iterators, lazy generators.

## Example in `iterator.py`

A binary search tree with multiple iterator strategies: in-order, pre-order, post-order, level-order (BFS), and a filtered iterator. Also demonstrates a lazy range iterator and a paginated collection iterator.
