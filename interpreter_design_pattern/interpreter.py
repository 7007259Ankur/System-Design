"""
Interpreter Design Pattern - Advanced Implementation
Real-world scenario: Boolean Rule Engine / Feature Flag DSL
Grammar rules become classes. Complex access-control expressions
are built as ASTs and evaluated against a context.
"""

from __future__ import annotations
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Context — holds variable bindings for interpretation
# ---------------------------------------------------------------------------

class Context:
    def __init__(self, variables: dict[str, Any]):
        self._vars = variables

    def get(self, name: str) -> Any:
        if name not in self._vars:
            raise KeyError(f"Variable '{name}' not found in context")
        return self._vars[name]

    def set(self, name: str, value: Any) -> None:
        self._vars[name] = value

    def __repr__(self) -> str:
        return f"Context({self._vars})"


# ---------------------------------------------------------------------------
# Abstract Expression
# ---------------------------------------------------------------------------

class Expression(ABC):
    @abstractmethod
    def interpret(self, context: Context) -> Any:
        """Evaluate this expression against the given context."""
        ...

    @abstractmethod
    def __str__(self) -> str: ...


# ---------------------------------------------------------------------------
# Terminal Expressions (leaf nodes)
# ---------------------------------------------------------------------------

class LiteralExpression(Expression):
    """A constant value: True, False, 42, 'admin'"""

    def __init__(self, value: Any):
        self._value = value

    def interpret(self, context: Context) -> Any:
        return self._value

    def __str__(self) -> str:
        return repr(self._value)


class VariableExpression(Expression):
    """Looks up a variable name in the context."""

    def __init__(self, name: str):
        self._name = name

    def interpret(self, context: Context) -> Any:
        return context.get(self._name)

    def __str__(self) -> str:
        return self._name


# ---------------------------------------------------------------------------
# Non-Terminal Expressions (composite nodes)
# ---------------------------------------------------------------------------

class AndExpression(Expression):
    def __init__(self, left: Expression, right: Expression):
        self._left = left
        self._right = right

    def interpret(self, context: Context) -> bool:
        return bool(self._left.interpret(context)) and bool(self._right.interpret(context))

    def __str__(self) -> str:
        return f"({self._left} AND {self._right})"


class OrExpression(Expression):
    def __init__(self, left: Expression, right: Expression):
        self._left = left
        self._right = right

    def interpret(self, context: Context) -> bool:
        return bool(self._left.interpret(context)) or bool(self._right.interpret(context))

    def __str__(self) -> str:
        return f"({self._left} OR {self._right})"


class NotExpression(Expression):
    def __init__(self, expr: Expression):
        self._expr = expr

    def interpret(self, context: Context) -> bool:
        return not bool(self._expr.interpret(context))

    def __str__(self) -> str:
        return f"NOT({self._expr})"


class EqualsExpression(Expression):
    def __init__(self, left: Expression, right: Expression):
        self._left = left
        self._right = right

    def interpret(self, context: Context) -> bool:
        return self._left.interpret(context) == self._right.interpret(context)

    def __str__(self) -> str:
        return f"({self._left} == {self._right})"


class GreaterThanExpression(Expression):
    def __init__(self, left: Expression, right: Expression):
        self._left = left
        self._right = right

    def interpret(self, context: Context) -> bool:
        return self._left.interpret(context) > self._right.interpret(context)

    def __str__(self) -> str:
        return f"({self._left} > {self._right})"


class LessThanExpression(Expression):
    def __init__(self, left: Expression, right: Expression):
        self._left = left
        self._right = right

    def interpret(self, context: Context) -> bool:
        return self._left.interpret(context) < self._right.interpret(context)

    def __str__(self) -> str:
        return f"({self._left} < {self._right})"


class InExpression(Expression):
    """Checks if a variable's value is in a list of literals."""

    def __init__(self, variable: Expression, values: list[Any]):
        self._variable = variable
        self._values = values

    def interpret(self, context: Context) -> bool:
        return self._variable.interpret(context) in self._values

    def __str__(self) -> str:
        return f"({self._variable} IN {self._values})"


# ---------------------------------------------------------------------------
# Rule — wraps an expression with a name and description
# ---------------------------------------------------------------------------

@dataclass
class Rule:
    name: str
    description: str
    expression: Expression

    def evaluate(self, context: Context) -> bool:
        result = bool(self.expression.interpret(context))
        logger.info(f"Rule '{self.name}': {result} | expr: {self.expression}")
        return result


# ---------------------------------------------------------------------------
# Rule Engine — evaluates multiple rules against a context
# ---------------------------------------------------------------------------

class RuleEngine:
    def __init__(self):
        self._rules: list[Rule] = []

    def add_rule(self, rule: Rule) -> "RuleEngine":
        self._rules.append(rule)
        return self

    def evaluate_all(self, context: Context) -> dict[str, bool]:
        results = {}
        for rule in self._rules:
            results[rule.name] = rule.evaluate(context)
        return results

    def evaluate_any(self, context: Context) -> bool:
        return any(rule.evaluate(context) for rule in self._rules)

    def evaluate_all_pass(self, context: Context) -> bool:
        return all(rule.evaluate(context) for rule in self._rules)


# ---------------------------------------------------------------------------
# DSL helpers — make building expressions more readable
# ---------------------------------------------------------------------------

def var(name: str) -> VariableExpression:
    return VariableExpression(name)

def lit(value: Any) -> LiteralExpression:
    return LiteralExpression(value)

def and_(left: Expression, right: Expression) -> AndExpression:
    return AndExpression(left, right)

def or_(left: Expression, right: Expression) -> OrExpression:
    return OrExpression(left, right)

def not_(expr: Expression) -> NotExpression:
    return NotExpression(expr)

def eq(left: Expression, right: Expression) -> EqualsExpression:
    return EqualsExpression(left, right)

def gt(left: Expression, right: Expression) -> GreaterThanExpression:
    return GreaterThanExpression(left, right)

def lt(left: Expression, right: Expression) -> LessThanExpression:
    return LessThanExpression(left, right)

def in_(variable: Expression, values: list) -> InExpression:
    return InExpression(variable, values)


# ---------------------------------------------------------------------------
# Demo
# ---------------------------------------------------------------------------

def main():
    print("=" * 60)
    print("  Interpreter Pattern -- Boolean Rule Engine Demo")
    print("=" * 60)

    # --- Build rules as expression ASTs ---

    # Rule 1: User must be admin OR superuser
    admin_rule = Rule(
        name="is_privileged",
        description="User has admin or superuser role",
        expression=or_(
            eq(var("role"), lit("admin")),
            eq(var("role"), lit("superuser"))
        )
    )

    # Rule 2: User must be 18+ AND account must be verified
    age_rule = Rule(
        name="age_verified",
        description="User is 18+ and account is verified",
        expression=and_(
            gt(var("age"), lit(17)),
            eq(var("verified"), lit(True))
        )
    )

    # Rule 3: Feature flag — beta users OR premium tier
    feature_rule = Rule(
        name="feature_access",
        description="Access to beta feature",
        expression=or_(
            eq(var("beta_user"), lit(True)),
            in_(var("tier"), ["premium", "enterprise"])
        )
    )

    # Rule 4: Complex — (admin AND verified) OR (age > 21 AND NOT banned)
    complex_rule = Rule(
        name="full_access",
        description="Full platform access",
        expression=or_(
            and_(eq(var("role"), lit("admin")), eq(var("verified"), lit(True))),
            and_(gt(var("age"), lit(21)), not_(eq(var("banned"), lit(True))))
        )
    )

    engine = RuleEngine()
    engine.add_rule(admin_rule)
    engine.add_rule(age_rule)
    engine.add_rule(feature_rule)
    engine.add_rule(complex_rule)

    # --- Test with different user contexts ---
    users = [
        {"name": "Alice",   "role": "admin",    "age": 30, "verified": True,  "beta_user": False, "tier": "enterprise", "banned": False},
        {"name": "Bob",     "role": "user",     "age": 16, "verified": True,  "beta_user": True,  "tier": "free",       "banned": False},
        {"name": "Charlie", "role": "user",     "age": 25, "verified": False, "beta_user": False, "tier": "premium",    "banned": False},
        {"name": "Dave",    "role": "superuser","age": 22, "verified": True,  "beta_user": False, "tier": "free",       "banned": True},
    ]

    for user in users:
        name = user.pop("name")
        ctx = Context(user)
        print(f"\n>>> User: {name} | {user}")
        results = engine.evaluate_all(ctx)
        for rule_name, passed in results.items():
            status = "PASS" if passed else "FAIL"
            print(f"  [{status}] {rule_name}")

    # --- Show expression trees ---
    print("\n>>> Expression Trees (AST representation)")
    for rule in [admin_rule, age_rule, feature_rule, complex_rule]:
        print(f"  {rule.name}: {rule.expression}")


if __name__ == "__main__":
    main()
