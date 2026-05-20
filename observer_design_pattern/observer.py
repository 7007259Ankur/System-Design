"""
Observer Design Pattern - Advanced Implementation
Real-world scenario: Stock Market System
Stocks publish price changes; multiple observers react differently.
"""
from __future__ import annotations
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Callable, Optional


# ---------------------------------------------------------------------------
# Event model
# ---------------------------------------------------------------------------

class EventType(Enum):
    PRICE_CHANGE  = "price_change"
