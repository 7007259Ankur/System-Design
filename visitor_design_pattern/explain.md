# Visitor Design Pattern

## What is it?

The Visitor pattern is a behavioral design pattern that lets you add new operations to existing object structures without modifying those objects. You separate the algorithm from the objects it operates on by moving the logic into a separate "visitor" object.

The key trick is **double dispatch** — the element calls back the visitor with itself, so the right visitor method gets invoked based on both the visitor type and the element type.

## When to Use

- You need to perform many distinct, unrelated operations on an object structure without polluting those classes
- The object structure rarely changes, but you frequently add new operations
- You want to gather related operations into a single class instead of spreading them across many classes
- You need to accumulate state while traversing a complex structure

## Structure

```
Client → ObjectStructure (contains Elements)
              └── ElementA.accept(visitor) → visitor.visit_element_a(self)
              └── ElementB.accept(visitor) → visitor.visit_element_b(self)

Visitor (interface)
  └── visit_element_a(ElementA)
  └── visit_element_b(ElementB)

ConcreteVisitorX  ← implements all visit methods
ConcreteVisitorY  ← implements all visit methods
```

- Element: Declares `accept(visitor)` method
- ConcreteElement: Calls `visitor.visit_X(self)` — the double dispatch
- Visitor: Interface declaring a `visit_X` method for each element type
- ConcreteVisitor: Implements the actual operation for each element type
- ObjectStructure: Holds elements and lets visitors traverse them

## Double Dispatch Explained

Normal method calls are single dispatch — resolved by the type of one object (the receiver).  
Visitor uses double dispatch — the method called depends on **both** the visitor type and the element type.

```python
element.accept(visitor)          # dispatch 1: which element?
  → visitor.visit_circle(self)   # dispatch 2: which visitor?
```

## Visitor vs Strategy vs Command

| | Visitor | Strategy | Command |
|---|---|---|---|
| Operates on | Object structure (many types) | Single context | Single receiver |
| Adding ops | New visitor class | New strategy class | New command class |
| Adding elements | Must update all visitors | N/A | N/A |
| Double dispatch | Yes | No | No |

## Real-World Analogy

A tax auditor visiting different types of assets (property, stocks, business). Each asset type knows how to "accept" an auditor. The auditor knows how to calculate tax differently for each asset type. Add a new auditor (e.g., insurance assessor) without touching any asset class.

## Pros

- Open/Closed: Add new operations (visitors) without modifying element classes
- Single Responsibility: Related operations are grouped in one visitor
- Accumulate state across a traversal naturally

## Cons

- Adding a new element type requires updating every visitor
- Visitors may need access to private state of elements (breaks encapsulation)
- Can be overkill for simple structures

## Example in `visitor.py`

Models a document AST (Abstract Syntax Tree) with:
- Elements: `Document`, `Heading`, `Paragraph`, `Table`, `CodeBlock`, `Image`
- Visitors: `HTMLExportVisitor`, `MarkdownExportVisitor`, `WordCountVisitor`, `SEOAnalyzerVisitor`
- Each visitor traverses the same document structure and produces a different output
- Add a new export format without touching any document element class
