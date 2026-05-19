"""
Factory Method Design Pattern - Advanced Implementation
Real-world scenario: Multi-channel Notification System
The factory method lets us add new notification channels without
touching existing delivery or routing logic.
"""

from __future__ import annotations
import logging
import time
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

class Priority(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


class DeliveryStatus(Enum):
    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"
    RETRYING = "retrying"


@dataclass
class NotificationPayload:
    recipient: str
    subject: str
    body: str
    priority: Priority = Priority.MEDIUM
    metadata: dict = field(default_factory=dict)


@dataclass
class DeliveryReport:
    notification_id: str
    channel: str
    recipient: str
    status: DeliveryStatus
    attempts: int = 1
    timestamp: datetime = field(default_factory=datetime.now)
    error: str = ""

    def __str__(self) -> str:
        return (
            f"[{self.channel}] {self.status.value.upper()} → {self.recipient} "
            f"(attempts: {self.attempts}) | ID: {self.notification_id}"
        )


# ---------------------------------------------------------------------------
# Product Interface — what every notification must implement
# ---------------------------------------------------------------------------

class Notification(ABC):
    def __init__(self, payload: NotificationPayload):
        self.payload = payload
        self.notification_id = str(uuid.uuid4())[:8]

    @abstractmethod
    def send(self) -> DeliveryReport:
        """Send the notification and return a delivery report."""
        ...

    @abstractmethod
    def channel_name(self) -> str:
        ...

    def _make_report(self, status: DeliveryStatus, attempts: int = 1, error: str = "") -> DeliveryReport:
        return DeliveryReport(
            notification_id=self.notification_id,
            channel=self.channel_name(),
            recipient=self.payload.recipient,
            status=status,
            attempts=attempts,
            error=error,
        )


# ---------------------------------------------------------------------------
# Concrete Products
# ---------------------------------------------------------------------------

class EmailNotification(Notification):
    def channel_name(self) -> str:
        return "Email"

    def send(self) -> DeliveryReport:
        logger.info(f"Email → {self.payload.recipient} | Subject: {self.payload.subject}")
        # Simulate SMTP send
        time.sleep(0.01)
        logger.info(f"Email delivered successfully to {self.payload.recipient}")
        return self._make_report(DeliveryStatus.SENT)


class SMSNotification(Notification):
    MAX_LENGTH = 160

    def channel_name(self) -> str:
        return "SMS"

    def send(self) -> DeliveryReport:
        body = self.payload.body
        if len(body) > self.MAX_LENGTH:
            body = body[:self.MAX_LENGTH - 3] + "..."
            logger.warning(f"SMS body truncated to {self.MAX_LENGTH} chars")
        logger.info(f"SMS → {self.payload.recipient} | Message: {body[:40]}...")
        time.sleep(0.01)
        return self._make_report(DeliveryStatus.SENT)


class PushNotification(Notification):
    def channel_name(self) -> str:
        return "Push"

    def send(self) -> DeliveryReport:
        device_token = self.payload.metadata.get("device_token", "unknown-device")
        logger.info(f"Push → device:{device_token} | Title: {self.payload.subject}")
        time.sleep(0.01)
        return self._make_report(DeliveryStatus.SENT)


class SlackNotification(Notification):
    def channel_name(self) -> str:
        return "Slack"

    def send(self) -> DeliveryReport:
        slack_channel = self.payload.metadata.get("slack_channel", "#general")
        logger.info(f"Slack → {slack_channel} | {self.payload.subject}: {self.payload.body[:60]}")
        time.sleep(0.01)
        return self._make_report(DeliveryStatus.SENT)


class WebhookNotification(Notification):
    def channel_name(self) -> str:
        return "Webhook"

    def send(self) -> DeliveryReport:
        url = self.payload.metadata.get("webhook_url", "https://example.com/hook")
        logger.info(f"Webhook POST → {url} | payload size: {len(self.payload.body)} bytes")
        time.sleep(0.01)
        return self._make_report(DeliveryStatus.SENT)


# ---------------------------------------------------------------------------
# Creator (abstract) — declares the factory method
# ---------------------------------------------------------------------------

class NotificationFactory(ABC):
    """
    The Creator. Subclasses override `create_notification` to produce
    the right product. The `deliver` method is the template that uses it.
    """

    MAX_RETRIES = 3

    @abstractmethod
    def create_notification(self, payload: NotificationPayload) -> Notification:
        """Factory method — subclasses decide what to instantiate."""
        ...

    def deliver(self, payload: NotificationPayload) -> DeliveryReport:
        """
        Template method that uses the factory method.
        Handles retry logic regardless of notification type.
        """
        notification = self.create_notification(payload)
        attempts = 0

        while attempts < self.MAX_RETRIES:
            attempts += 1
            try:
                report = notification.send()
                report.attempts = attempts
                return report
            except Exception as e:
                logger.warning(f"Attempt {attempts} failed: {e}")
                if attempts < self.MAX_RETRIES:
                    logger.info(f"Retrying in {attempts}s...")
                    time.sleep(attempts)

        return DeliveryReport(
            notification_id=str(uuid.uuid4())[:8],
            channel=notification.channel_name(),
            recipient=payload.recipient,
            status=DeliveryStatus.FAILED,
            attempts=attempts,
            error="Max retries exceeded",
        )


# ---------------------------------------------------------------------------
# Concrete Creators — each overrides the factory method
# ---------------------------------------------------------------------------

class EmailNotificationFactory(NotificationFactory):
    def create_notification(self, payload: NotificationPayload) -> Notification:
        return EmailNotification(payload)


class SMSNotificationFactory(NotificationFactory):
    def create_notification(self, payload: NotificationPayload) -> Notification:
        return SMSNotification(payload)


class PushNotificationFactory(NotificationFactory):
    def create_notification(self, payload: NotificationPayload) -> Notification:
        return PushNotification(payload)


class SlackNotificationFactory(NotificationFactory):
    def create_notification(self, payload: NotificationPayload) -> Notification:
        return SlackNotification(payload)


class WebhookNotificationFactory(NotificationFactory):
    def create_notification(self, payload: NotificationPayload) -> Notification:
        return WebhookNotification(payload)


# ---------------------------------------------------------------------------
# Registry — maps channel names to factories (Open/Closed Principle)
# ---------------------------------------------------------------------------

class NotificationFactoryRegistry:
    _factories: dict[str, NotificationFactory] = {
        "email": EmailNotificationFactory(),
        "sms": SMSNotificationFactory(),
        "push": PushNotificationFactory(),
        "slack": SlackNotificationFactory(),
        "webhook": WebhookNotificationFactory(),
    }

    @classmethod
    def get(cls, channel: str) -> NotificationFactory:
        key = channel.lower()
        if key not in cls._factories:
            raise ValueError(f"Unknown channel '{channel}'. Available: {list(cls._factories)}")
        return cls._factories[key]

    @classmethod
    def register(cls, channel: str, factory: NotificationFactory) -> None:
        cls._factories[channel.lower()] = factory
        logger.info(f"Registered new notification factory: {channel}")


# ---------------------------------------------------------------------------
# Client — NotificationService uses factories, never concrete classes
# ---------------------------------------------------------------------------

class NotificationService:
    def __init__(self):
        self._reports: list[DeliveryReport] = []

    def notify(self, channel: str, payload: NotificationPayload) -> DeliveryReport:
        factory = NotificationFactoryRegistry.get(channel)
        report = factory.deliver(payload)
        self._reports.append(report)
        return report

    def broadcast(self, channels: list[str], payload: NotificationPayload) -> list[DeliveryReport]:
        """Send the same notification across multiple channels."""
        reports = []
        for channel in channels:
            report = self.notify(channel, payload)
            reports.append(report)
        return reports

    def notify_by_priority(self, payload: NotificationPayload) -> list[DeliveryReport]:
        """Route to channels based on priority level."""
        routing = {
            Priority.LOW: ["email"],
            Priority.MEDIUM: ["email", "slack"],
            Priority.HIGH: ["email", "sms", "slack"],
            Priority.CRITICAL: ["email", "sms", "push", "slack"],
        }
        channels = routing.get(payload.priority, ["email"])
        logger.info(f"Priority {payload.priority.name} → routing to: {channels}")
        return self.broadcast(channels, payload)

    def print_summary(self) -> None:
        print("\n--- Delivery Summary ---")
        sent = sum(1 for r in self._reports if r.status == DeliveryStatus.SENT)
        failed = sum(1 for r in self._reports if r.status == DeliveryStatus.FAILED)
        for r in self._reports:
            print(f"  {r}")
        print(f"\n  Total: {len(self._reports)} | Sent: {sent} | Failed: {failed}")
        print("------------------------")


# ---------------------------------------------------------------------------
# Demo
# ---------------------------------------------------------------------------

def main():
    print("=" * 55)
    print("  Factory Method Pattern — Notification System Demo")
    print("=" * 55)

    service = NotificationService()

    # 1. Single channel notifications
    print("\n>>> Single channel sends")
    channels_demo = [
        ("email", "user@example.com", {}),
        ("sms", "+1-555-0100", {}),
        ("push", "user_device_001", {"device_token": "tok_abc123"}),
        ("slack", "team-alerts", {"slack_channel": "#team-alerts"}),
        ("webhook", "https://hooks.example.com", {"webhook_url": "https://hooks.example.com/notify"}),
    ]

    for channel, recipient, meta in channels_demo:
        payload = NotificationPayload(
            recipient=recipient,
            subject="Welcome to the platform",
            body="Your account has been created successfully.",
            metadata=meta,
        )
        report = service.notify(channel, payload)
        print(f"  {report}")

    # 2. Priority-based routing
    print("\n>>> Priority-based routing (CRITICAL alert)")
    critical_payload = NotificationPayload(
        recipient="admin@example.com",
        subject="CRITICAL: Server down",
        body="Production server is not responding. Immediate action required.",
        priority=Priority.CRITICAL,
        metadata={
            "device_token": "tok_admin_device",
            "slack_channel": "#incidents",
        },
    )
    reports = service.notify_by_priority(critical_payload)
    for r in reports:
        print(f"  {r}")

    # 3. Register a custom factory at runtime
    print("\n>>> Registering custom 'InAppNotification' factory")

    class InAppNotification(Notification):
        def channel_name(self) -> str:
            return "InApp"

        def send(self) -> DeliveryReport:
            logger.info(f"InApp → user_id:{self.payload.recipient} | {self.payload.subject}")
            return self._make_report(DeliveryStatus.SENT)

    class InAppNotificationFactory(NotificationFactory):
        def create_notification(self, payload: NotificationPayload) -> Notification:
            return InAppNotification(payload)

    NotificationFactoryRegistry.register("inapp", InAppNotificationFactory())
    payload = NotificationPayload(recipient="user_42", subject="You have a new message", body="Hey, check this out!")
    report = service.notify("inapp", payload)
    print(f"  {report}")

    # Final summary
    service.print_summary()


if __name__ == "__main__":
    main()
