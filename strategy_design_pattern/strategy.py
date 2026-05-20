"""
Strategy Design Pattern - Advanced Implementation
Real-world scenario: E-commerce checkout with swappable
discount, tax, and shipping strategies — all interchangeable
at runtime with zero changes to the checkout context.
"""

from __future__ import annotations
import logging
import time
import random
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Domain model
# ---------------------------------------------------------------------------

@dataclass
class CartItem:
    name: str
    price: float
    qty: int
    category: str = "general"

    @property
    def subtotal(self) -> float:
        return self.price * self.qty


@dataclass
class OrderSummary:
    items: list[CartItem]
    subtotal: float
    discount: float
    tax: float
    shipping: float
    total: float
    discount_label: str = ""
    shipping_label: str = ""

    def display(self) -> None:
        print(f"\n  {'Item':<25} {'Qty':>4} {'Price':>8} {'Subtotal':>10}")
        print(f"  {'-'*51}")
        for item in self.items:
            print(f"  {item.name:<25} {item.qty:>4} ${item.price:>7.2f} ${item.subtotal:>9.2f}")
        print(f"  {'-'*51}")
        print(f"  {'Subtotal':<40} ${self.subtotal:>9.2f}")
        if self.discount:
            print(f"  {'Discount (' + self.discount_label + ')':<40} -${self.discount:>8.2f}")
        print(f"  {'Tax':<40} ${self.tax:>9.2f}")
        print(f"  {'Shipping (' + self.shipping_label + ')':<40} ${self.shipping:>9.2f}")
        print(f"  {'='*51}")
        print(f"  {'TOTAL':<40} ${self.total:>9.2f}\n")


# ---------------------------------------------------------------------------
# Strategy 1: Discount
# ---------------------------------------------------------------------------

class DiscountStrategy(ABC):
    @abstractmethod
    def apply(self, items: list[CartItem], subtotal: float) -> tuple[float, str]:
        """Returns (discount_amount, label)"""
        ...


class NoDiscount(DiscountStrategy):
    def apply(self, items, subtotal):
        return 0.0, "none"


class PercentageDiscount(DiscountStrategy):
    def __init__(self, percent: float):
        self._percent = percent

    def apply(self, items, subtotal):
        discount = round(subtotal * self._percent / 100, 2)
        return discount, f"{self._percent}% off"


class FlatDiscount(DiscountStrategy):
    def __init__(self, amount: float, min_order: float = 0):
        self._amount = amount
        self._min = min_order

    def apply(self, items, subtotal):
        if subtotal < self._min:
            logger.info(f"Flat discount requires min order ${self._min:.2f}")
            return 0.0, "not eligible"
        return min(self._amount, subtotal), f"${self._amount:.0f} flat"


class BuyOneGetOne(DiscountStrategy):
    """50% off the cheapest item in each pair of same-category items."""

    def apply(self, items, subtotal):
        discount = 0.0
        by_category: dict[str, list[CartItem]] = {}
        for item in items:
            by_category.setdefault(item.category, []).append(item)

        for cat, cat_items in by_category.items():
            sorted_items = sorted(cat_items, key=lambda x: x.price)
            free_count = sum(i.qty for i in sorted_items) // 2
            for item in sorted_items:
                take = min(free_count, item.qty)
                discount += take * item.price * 0.5
                free_count -= take
                if free_count <= 0:
                    break

        return round(discount, 2), "BOGO 50%"


# ---------------------------------------------------------------------------
# Strategy 2: Tax
# ---------------------------------------------------------------------------

class TaxStrategy(ABC):
    @abstractmethod
    def calculate(self, subtotal: float, discount: float) -> float: ...


class StandardTax(TaxStrategy):
    def __init__(self, rate: float = 0.08):
        self._rate = rate

    def calculate(self, subtotal, discount):
        return round((subtotal - discount) * self._rate, 2)


class TaxExempt(TaxStrategy):
    def calculate(self, subtotal, discount):
        return 0.0


class TieredTax(TaxStrategy):
    """Different rates for different taxable amount brackets."""

    def calculate(self, subtotal, discount):
        taxable = subtotal - discount
        if taxable <= 100:
            return round(taxable * 0.05, 2)
        elif taxable <= 500:
            return round(taxable * 0.08, 2)
        else:
            return round(taxable * 0.12, 2)


# ---------------------------------------------------------------------------
# Strategy 3: Shipping
# ---------------------------------------------------------------------------

class ShippingStrategy(ABC):
    @abstractmethod
    def calculate(self, items: list[CartItem], subtotal: float) -> tuple[float, str]: ...


class StandardShipping(ShippingStrategy):
    def calculate(self, items, subtotal):
        return (0.0, "Free Standard") if subtotal >= 50 else (5.99, "Standard")


class ExpressShipping(ShippingStrategy):
    def calculate(self, items, subtotal):
        weight = sum(i.qty for i in items)
        cost = 12.99 + (weight * 0.5)
        return round(cost, 2), "Express (2-day)"


class OvernightShipping(ShippingStrategy):
    def calculate(self, items, subtotal):
        return 29.99, "Overnight"


class PickupShipping(ShippingStrategy):
    def calculate(self, items, subtotal):
        return 0.0, "In-store Pickup"


# ---------------------------------------------------------------------------
# Context — Checkout
# ---------------------------------------------------------------------------

class Checkout:
    """
    Context. Holds strategy references and delegates calculations.
    Strategies are fully swappable at runtime.
    """

    def __init__(
        self,
        discount_strategy: DiscountStrategy = None,
        tax_strategy: TaxStrategy = None,
        shipping_strategy: ShippingStrategy = None,
    ):
        self._discount = discount_strategy or NoDiscount()
        self._tax = tax_strategy or StandardTax()
        self._shipping = shipping_strategy or StandardShipping()

    # Runtime strategy swap
    def set_discount(self, strategy: DiscountStrategy) -> None:
        logger.info(f"Discount strategy -> {strategy.__class__.__name__}")
        self._discount = strategy

    def set_tax(self, strategy: TaxStrategy) -> None:
        logger.info(f"Tax strategy -> {strategy.__class__.__name__}")
        self._tax = strategy

    def set_shipping(self, strategy: ShippingStrategy) -> None:
        logger.info(f"Shipping strategy -> {strategy.__class__.__name__}")
        self._shipping = strategy

    def calculate(self, items: list[CartItem]) -> OrderSummary:
        subtotal = round(sum(i.subtotal for i in items), 2)
        discount, discount_label = self._discount.apply(items, subtotal)
        tax = self._tax.calculate(subtotal, discount)
        shipping, shipping_label = self._shipping.calculate(items, subtotal)
        total = round(subtotal - discount + tax + shipping, 2)

        return OrderSummary(
            items=items,
            subtotal=subtotal,
            discount=discount,
            tax=tax,
            shipping=shipping,
            total=total,
            discount_label=discount_label,
            shipping_label=shipping_label,
        )


# ---------------------------------------------------------------------------
# Demo
# ---------------------------------------------------------------------------

def main():
    print("=" * 55)
    print("  Strategy Pattern -- Checkout System Demo")
    print("=" * 55)

    cart = [
        CartItem("Laptop",    999.99, 1, "electronics"),
        CartItem("Mouse",      29.99, 2, "electronics"),
        CartItem("T-Shirt",    19.99, 3, "clothing"),
        CartItem("Jeans",      49.99, 2, "clothing"),
    ]

    checkout = Checkout()

    print("\n>>> Strategy 1: No discount + Standard tax + Standard shipping")
    checkout.set_discount(NoDiscount())
    checkout.set_tax(StandardTax(0.08))
    checkout.set_shipping(StandardShipping())
    checkout.calculate(cart).display()

    print(">>> Strategy 2: 15% discount + Tiered tax + Express shipping")
    checkout.set_discount(PercentageDiscount(15))
    checkout.set_tax(TieredTax())
    checkout.set_shipping(ExpressShipping())
    checkout.calculate(cart).display()

    print(">>> Strategy 3: $50 flat discount + Tax exempt + Overnight")
    checkout.set_discount(FlatDiscount(50, min_order=100))
    checkout.set_tax(TaxExempt())
    checkout.set_shipping(OvernightShipping())
    checkout.calculate(cart).display()

    print(">>> Strategy 4: BOGO 50% + Standard tax + In-store pickup")
    checkout.set_discount(BuyOneGetOne())
    checkout.set_tax(StandardTax(0.1))
    checkout.set_shipping(PickupShipping())
    checkout.calculate(cart).display()

    print(">>> Strategy 5: Small cart — flat discount not eligible")
    small_cart = [CartItem("Pen", 2.99, 1, "stationery")]
    checkout.set_discount(FlatDiscount(10, min_order=50))
    checkout.set_tax(StandardTax())
    checkout.set_shipping(StandardShipping())
    checkout.calculate(small_cart).display()


if __name__ == "__main__":
    main()
