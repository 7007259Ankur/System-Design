"""
State Design Pattern - Advanced Implementation
Real-world scenario: E-commerce Order Lifecycle
Each order state controls its own valid transitions and actions.
No if/elif chains — behavior is fully delegated to state objects.
"""

from __future__ import annotations
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Context
# ---------------------------------------------------------------------------

@dataclass
class OrderItem:
    name: str
    qty: int
    price: float

    @property
    def total(self) -> float:
        return self.qty * self.price


class Order:
    """Context — delegates all behavior to the current state."""

    def __init__(self, order_id: str, items: list[OrderItem]):
        self.order_id = order_id
        self.items = items
        self.created_at = datetime.now()
        self._state: OrderState = PendingState(self)
        self._history: list[str] = []
        self._tracking_number: Optional[str] = None
        self._refund_amount: float = 0.0
        self._log(f"Order created with {len(items)} item(s)")

    # --- Delegated actions (each calls the current state) ---

    def confirm(self) -> None:
        self._state.confirm()

    def process(self) -> None:
        self._state.process()

    def ship(self, tracking: str) -> None:
        self._state.ship(tracking)

    def deliver(self) -> None:
        self._state.deliver()

    def cancel(self) -> None:
        self._state.cancel()

    def request_refund(self) -> None:
        self._state.request_refund()

    # --- State management ---

    def transition_to(self, state: OrderState) -> None:
        self._log(f"State: {self.state_name} -> {state.name}")
        self._state = state

    def _log(self, msg: str) -> None:
        entry = f"[{datetime.now().strftime('%H:%M:%S')}] {msg}"
        self._history.append(entry)
        logger.info(f"Order {self.order_id}: {msg}")

    @property
    def state_name(self) -> str:
        return self._state.name

    @property
    def total(self) -> float:
        return sum(i.total for i in self.items)

    def print_summary(self) -> None:
        print(f"\n  Order: {self.order_id} | State: {self.state_name} | Total: ${self.total:.2f}")
        for item in self.items:
            print(f"    - {item.name} x{item.qty} @ ${item.price:.2f}")
        if self._tracking_number:
            print(f"  Tracking: {self._tracking_number}")
        if self._refund_amount:
            print(f"  Refund: ${self._refund_amount:.2f}")
        print("  History:")
        for h in self._history:
            print(f"    {h}")


# ---------------------------------------------------------------------------
# State Interface
# ---------------------------------------------------------------------------

class OrderState(ABC):
    def __init__(self, order: Order):
        self._order = order

    @property
    @abstractmethod
    def name(self) -> str: ...

    def confirm(self) -> None:
        self._invalid("confirm")

    def process(self) -> None:
        self._invalid("process")

    def ship(self, tracking: str) -> None:
        self._invalid("ship")

    def deliver(self) -> None:
        self._invalid("deliver")

    def cancel(self) -> None:
        self._invalid("cancel")

    def request_refund(self) -> None:
        self._invalid("request_refund")

    def _invalid(self, action: str) -> None:
        logger.warning(f"Action '{action}' not allowed in state '{self.name}'")


# ---------------------------------------------------------------------------
# Concrete States
# ---------------------------------------------------------------------------

class PendingState(OrderState):
    @property
    def name(self) -> str:
        return "Pending"

    def confirm(self) -> None:
        logger.info("Payment verified. Confirming order...")
        self._order.transition_to(ConfirmedState(self._order))

    def cancel(self) -> None:
        logger.info("Order cancelled before confirmation.")
        self._order.transition_to(CancelledState(self._order))


class ConfirmedState(OrderState):
    @property
    def name(self) -> str:
        return "Confirmed"

    def process(self) -> None:
        logger.info("Warehouse picking items...")
        self._order.transition_to(ProcessingState(self._order))

    def cancel(self) -> None:
        logger.info("Order cancelled after confirmation. Full refund issued.")
        self._order._refund_amount = self._order.total
        self._order.transition_to(CancelledState(self._order))


class ProcessingState(OrderState):
    @property
    def name(self) -> str:
        return "Processing"

    def ship(self, tracking: str) -> None:
        logger.info(f"Package handed to courier. Tracking: {tracking}")
        self._order._tracking_number = tracking
        self._order.transition_to(ShippedState(self._order))

    def cancel(self) -> None:
        logger.info("Order cancelled during processing. Full refund issued.")
        self._order._refund_amount = self._order.total
        self._order.transition_to(CancelledState(self._order))


class ShippedState(OrderState):
    @property
    def name(self) -> str:
        return "Shipped"

    def deliver(self) -> None:
        logger.info("Package delivered to customer.")
        self._order.transition_to(DeliveredState(self._order))


class DeliveredState(OrderState):
    @property
    def name(self) -> str:
        return "Delivered"

    def request_refund(self) -> None:
        logger.info("Refund requested. Processing return...")
        self._order._refund_amount = self._order.total
        self._order.transition_to(RefundedState(self._order))


class CancelledState(OrderState):
    @property
    def name(self) -> str:
        return "Cancelled"


class RefundedState(OrderState):
    @property
    def name(self) -> str:
        return "Refunded"


# ---------------------------------------------------------------------------
# Demo
# ---------------------------------------------------------------------------

def main():
    print("=" * 55)
    print("  State Pattern -- E-commerce Order Lifecycle Demo")
    print("=" * 55)

    # Happy path
    print("\n>>> Scenario 1: Full happy path")
    order1 = Order("ORD-001", [
        OrderItem("Laptop", 1, 999.99),
        OrderItem("Mouse", 2, 29.99),
    ])
    order1.confirm()
    order1.process()
    order1.ship("TRK-ABC123")
    order1.deliver()
    order1.print_summary()

    # Refund after delivery
    print("\n>>> Scenario 2: Refund after delivery")
    order2 = Order("ORD-002", [OrderItem("Headphones", 1, 149.99)])
    order2.confirm()
    order2.process()
    order2.ship("TRK-XYZ789")
    order2.deliver()
    order2.request_refund()
    order2.print_summary()

    # Cancel early
    print("\n>>> Scenario 3: Cancel during processing")
    order3 = Order("ORD-003", [OrderItem("Keyboard", 1, 79.99)])
    order3.confirm()
    order3.process()
    order3.cancel()
    order3.print_summary()

    # Invalid transitions
    print("\n>>> Scenario 4: Invalid transitions (gracefully rejected)")
    order4 = Order("ORD-004", [OrderItem("Monitor", 1, 399.99)])
    order4.deliver()    # invalid — still Pending
    order4.ship("X")    # invalid — still Pending
    order4.confirm()
    order4.deliver()    # invalid — Confirmed, not Shipped
    order4.print_summary()


if __name__ == "__main__":
    main()
