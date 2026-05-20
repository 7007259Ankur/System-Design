# Interpreter Design Pattern

## What is it?

The Interpreter pattern is a behavioral design pattern that defines a grammar for a language and provides an interpreter to deal with that grammar. Each rule in the grammar becomes a class, and the interpreter evaluates expressions by composing these classes into a tree (AST).

## When to Use

- You need to interpret sentences in a simple language or DSL
- The grammar is simple and performance is not critical
- You want to represent grammar rules as a class hierarchy
- Examples: SQL parsers, math expression evaluators, config DSLs, rule engines

## Structure

```
AbstractExpression
  +-- TerminalExpression     (leaf nodes: numbers, variables)
  +-- NonTerminalExpression  (composite nodes: +, -, AND, OR)

Context  -- holds variable bindings
Client   -- builds the AST and calls interpret()
```

- AbstractExpression: `interpret(context)` interface
- TerminalExpression: Leaf — interprets a literal or variable
- NonTerminalExpression: Composite — interprets by combining sub-expressions
- Context: Stores variable values used during interpretation

## Interpreter vs Visitor

| | Interpreter | Visitor |
|---|---|---|
| Purpose | Evaluate grammar expressions | Add operations to object structure |
| Structure | AST of expression objects | Separate visitor traverses elements |
| Grammar changes | Add new expression class | Add new visitor |

## Real-World Analogy

A calculator. "3 + 5 * 2" is parsed into an AST: Add(3, Multiply(5, 2)). Each node knows how to evaluate itself. The interpreter walks the tree and returns the result.

## Pros

- Easy to extend grammar — add a new expression class
- Each grammar rule is isolated in its own class
- AST can be reused and re-evaluated with different contexts

## Cons

- Complex grammars lead to many classes
- Performance can be poor for large expressions
- For complex languages, use a proper parser generator instead

## Example in `interpreter.py`

Implements a boolean rule engine DSL used in feature flags / access control:
- Terminal: `VariableExpression`, `LiteralExpression`
- Non-terminal: `AndExpression`, `OrExpression`, `NotExpression`, `GreaterThanExpression`, `EqualsExpression`
- Evaluates rules like: `role == admin AND (age > 18 OR beta_user == true)`
