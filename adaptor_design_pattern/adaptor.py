"""
Adapter Design Pattern - Advanced Implementation
Real-world scenario: Unified Payment Gateway
Each payment provider has a different API. The Adapter pattern gives us
a consistent interface to work with all of them.
"""

from __future__ import annotations
import logging
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Domain models
# ---------------------------------------------------------------------------

class PaymentStatus(Enum):
    SUCCESS = "success"
    FAILED = "failed"
    PENDING = "pending"


@dataclass
class PaymentResult:
    transaction_id: str
    status: PaymentStatus
    amount: float
    currency: str
    provider: str
    timestamp: datetime = field(default_factory=datetime.now)
    message: str = ""

    def __str__(self) -> str:
        return (
            f"[{self.provider}] {self.status.value.upper()} | "
            f"{self.currency} {self.amount:.2f} | TX: {self.transaction_id}"
        )


# ---------------------------------------------------------------------------
# Target Interface — what our app expects
# ---------------------------------------------------------------------------

class PaymentAdapter(ABC):
    """The unified interface all adapters must implement."""

    @abstractmethod
    def pay(self, amount: float, currency: str, token: str) -> PaymentResult:
        ...

    @abstractmethod
    def refund(self, transaction_id: str, amount: float) -> PaymentResult:
        ...

    @abstractmethod
    def get_provider_name(self) -> str:
        ...


# ---------------------------------------------------------------------------
# Adaptees — third-party SDKs with incompatible interfaces
# ---------------------------------------------------------------------------

class StripeSDK:
    """Simulates the real Stripe Python SDK."""

    def create_charge(self, amount_cents: int, currency: str, source: str) -> dict:
        logger.info(f"Stripe: charging {amount_cents} cents ({currency})")
        return {
            "id": f"ch_{uuid.uuid4().hex[:16]}",
            "status": "succeeded",
            "amount": amount_cents,
            "currency": currency,
        }

    def create_refund(self, charge_id: str, amount_cents: int) -> dict:
        logger.info(f"Stripe: refunding charge {charge_id}")
        return {"id": f"re_{uuid.uuid4().hex[:16]}", "status": "succeeded", "amount": amount_cents}


class PayPalSDK:
    """Simulates the PayPal REST SDK."""

    def execute_payment(self, total: str, currency_code: str, nonce: str) -> dict:
        logger.info(f"PayPal: executing payment of {total} {currency_code}")
        return {
            "paymentID": f"PAY-{uuid.uuid4().hex[:20].upper()}",
            "state": "approved",
            "total": total,
            "currency": currency_code,
        }

    def issue_refund(self, payment_id: str, total: str) -> dict:
        logger.info(f"PayPal: issuing refund for {payment_id}")
        return {"refundID": f"REF-{uuid.uuid4().hex[:16].upper()}", "state": "completed"}


class RazorpaySDK:
    """Simulates the Razorpay Python SDK."""

    def capture_payment(self, amount_paise: int, curr: str, payment_token: str) -> dict:
        logger.info(f"Razorpay: capturing {amount_paise} paise ({curr})")
        return {
            "razorpay_payment_id": f"pay_{uuid.uuid4().hex[:14]}",
            "razorpay_status": "captured",
            "amount": amount_paise,
        }

    def reverse_payment(self, payment_id: str, amount_paise: int) -> dict:
        logger.info(f"Razorpay: reversing payment {payment_id}")
        return {"id": f"rfd_{uuid.uuid4().hex[:14]}", "status": "processed"}


# ---------------------------------------------------------------------------
# Concrete Adapters — bridge between our interface and each SDK
# ---------------------------------------------------------------------------

class StripeAdapter(PaymentAdapter):
    def __init__(self, sdk: Optional[StripeSDK] = None):
        self._sdk = sdk or StripeSDK()

    def get_provider_name(self) -> str:
        return "Stripe"

    def pay(self, amount: float, currency: str, token: str) -> PaymentResult:
        try:
            amount_cents = int(amount * 100)  # Stripe works in cents
            response = self._sdk.create_charge(amount_cents, currency.lower(), token)
            return PaymentResult(
                transaction_id=response["id"],
                status=PaymentStatus.SUCCESS if response["status"] == "succeeded" else PaymentStatus.FAILED,
                amount=amount,
                currency=currency,
                provider=self.get_provider_name(),
            )
        except Exception as e:
            return PaymentResult(
                transaction_id="N/A", status=PaymentStatus.FAILED,
                amount=amount, currency=currency,
                provider=self.get_provider_name(), message=str(e),
            )

    def refund(self, transaction_id: str, amount: float) -> PaymentResult:
        response = self._sdk.create_refund(transaction_id, int(amount * 100))
        return PaymentResult(
            transaction_id=response["id"],
            status=PaymentStatus.SUCCESS if response["status"] == "succeeded" else PaymentStatus.FAILED,
            amount=amount, currency="USD", provider=self.get_provider_name(),
        )


class PayPalAdapter(PaymentAdapter):
    def __init__(self, sdk: Optional[PayPalSDK] = None):
        self._sdk = sdk or PayPalSDK()

    def get_provider_name(self) -> str:
        return "PayPal"

    def pay(self, amount: float, currency: str, token: str) -> PaymentResult:
        try:
            response = self._sdk.execute_payment(str(amount), currency.upper(), token)
            return PaymentResult(
                transaction_id=response["paymentID"],
                status=PaymentStatus.SUCCESS if response["state"] == "approved" else PaymentStatus.FAILED,
                amount=amount, currency=currency, provider=self.get_provider_name(),
            )
        except Exception as e:
            return PaymentResult(
                transaction_id="N/A", status=PaymentStatus.FAILED,
                amount=amount, currency=currency,
                provider=self.get_provider_name(), message=str(e),
            )

    def refund(self, transaction_id: str, amount: float) -> PaymentResult:
        response = self._sdk.issue_refund(transaction_id, str(amount))
        return PaymentResult(
            transaction_id=response["refundID"],
            status=PaymentStatus.SUCCESS if response["state"] == "completed" else PaymentStatus.FAILED,
            amount=amount, currency="USD", provider=self.get_provider_name(),
        )


class RazorpayAdapter(PaymentAdapter):
    def __init__(self, sdk: Optional[RazorpaySDK] = None):
        self._sdk = sdk or RazorpaySDK()

    def get_provider_name(self) -> str:
        return "Razorpay"

    def pay(self, amount: float, currency: str, token: str) -> PaymentResult:
        try:
            amount_paise = int(amount * 100)  # Razorpay works in paise
            response = self._sdk.capture_payment(amount_paise, currency.upper(), token)
            return PaymentResult(
                transaction_id=response["razorpay_payment_id"],
                status=PaymentStatus.SUCCESS if response["razorpay_status"] == "captured" else PaymentStatus.FAILED,
                amount=amount, currency=currency, provider=self.get_provider_name(),
            )
        except Exception as e:
            return PaymentResult(
                transaction_id="N/A", status=PaymentStatus.FAILED,
                amount=amount, currency=currency,
                provider=self.get_provider_name(), message=str(e),
            )

    def refund(self, transaction_id: str, amount: float) -> PaymentResult:
        response = self._sdk.reverse_payment(transaction_id, int(amount * 100))
        return PaymentResult(
            transaction_id=response["id"],
            status=PaymentStatus.SUCCESS if response["status"] == "processed" else PaymentStatus.FAILED,
            amount=amount, currency="INR", provider=self.get_provider_name(),
        )


# ---------------------------------------------------------------------------
# Factory — creates the right adapter by name
# ---------------------------------------------------------------------------

class PaymentAdapterFactory:
    _registry: dict[str, type[PaymentAdapter]] = {
        "stripe": StripeAdapter,
        "paypal": PayPalAdapter,
        "razorpay": RazorpayAdapter,
    }

    @classmethod
    def create(cls, provider: str) -> PaymentAdapter:
        key = provider.lower()
        if key not in cls._registry:
            raise ValueError(f"Unknown provider '{provider}'. Available: {list(cls._registry)}")
        return cls._registry[key]()

    @classmethod
    def register(cls, name: str, adapter_class: type[PaymentAdapter]) -> None:
        """Allows registering new adapters at runtime (Open/Closed Principle)."""
        cls._registry[name.lower()] = adapter_class
        logger.info(f"Registered new payment adapter: {name}")


# ---------------------------------------------------------------------------
# Client — works only with the PaymentAdapter interface, never with SDKs directly
# ---------------------------------------------------------------------------

class PaymentProcessor:
    def __init__(self, adapter: PaymentAdapter):
        self._adapter = adapter
        self._history: list[PaymentResult] = []

    def checkout(self, amount: float, currency: str, token: str) -> PaymentResult:
        logger.info(f"Processing payment via {self._adapter.get_provider_name()}...")
        result = self._adapter.pay(amount, currency, token)
        self._history.append(result)
        return result

    def refund_last(self) -> Optional[PaymentResult]:
        successful = [r for r in self._history if r.status == PaymentStatus.SUCCESS]
        if not successful:
            logger.warning("No successful transactions to refund.")
            return None
        last = successful[-1]
        result = self._adapter.refund(last.transaction_id, last.amount)
        self._history.append(result)
        return result

    def print_history(self) -> None:
        print("\n--- Transaction History ---")
        for tx in self._history:
            print(f"  {tx}")
        print("-" * 28)


# ---------------------------------------------------------------------------
# Demo
# ---------------------------------------------------------------------------

def main():
    print("=" * 50)
    print("  Adapter Pattern — Payment Gateway Demo")
    print("=" * 50)

    providers = ["stripe", "paypal", "razorpay"]

    for provider_name in providers:
        print(f"\n>>> Provider: {provider_name.upper()}")
        adapter = PaymentAdapterFactory.create(provider_name)
        processor = PaymentProcessor(adapter)

        result = processor.checkout(amount=99.99, currency="USD", token="tok_test_abc123")
        print(f"  Payment  → {result}")

        refund = processor.refund_last()
        if refund:
            print(f"  Refund   → {refund}")

        processor.print_history()

    # Demonstrate runtime adapter registration
    print("\n>>> Registering a custom 'MockPay' adapter at runtime...")

    class MockPaySDK:
        def charge(self, amount, token):
            return {"id": f"mock_{uuid.uuid4().hex[:8]}", "ok": True}

    class MockPayAdapter(PaymentAdapter):
        def __init__(self):
            self._sdk = MockPaySDK()

        def get_provider_name(self):
            return "MockPay"

        def pay(self, amount, currency, token):
            r = self._sdk.charge(amount, token)
            return PaymentResult(r["id"], PaymentStatus.SUCCESS, amount, currency, self.get_provider_name())

        def refund(self, transaction_id, amount):
            return PaymentResult(f"ref_{transaction_id}", PaymentStatus.SUCCESS, amount, "USD", self.get_provider_name())

    PaymentAdapterFactory.register("mockpay", MockPayAdapter)
    adapter = PaymentAdapterFactory.create("mockpay")
    processor = PaymentProcessor(adapter)
    result = processor.checkout(49.00, "USD", "mock_token")
    print(f"  MockPay  → {result}")


if __name__ == "__main__":
    main()
