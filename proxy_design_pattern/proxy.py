"""
Proxy Design Pattern - Advanced Implementation
Real-world scenario: Database Query Service
Stacked proxies: Protection → Caching → Logging → Real Service
"""
from __future__ import annotations
import hashlib
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional


# ---------------------------------------------------------------------------
# Subject Interface
# ---------------------------------------------------------------------------

class DatabaseService(ABC):
    @abstractmethod
    def query(self, sql: str, params: tuple = ()) -> list[dict]: ...

    @abstractmethod
    def execute(self, sql: str, params: tuple = ()) -> int: ...


# ---------------------------------------------------------------------------
# Real Subject
# ---------------------------------------------------------------------------

class RealDatabaseService(DatabaseService):
    """Simulates an actual database with fake data."""

    _fake_data = {
        "users": [
            {"id": 1, "name": "Alice", "role": "admin", "email": "alice@example.com"},
            {"id": 2, "name": "Bob",   "role": "user",  "email": "bob@example.com"},
            {"id": 3, "name": "Carol", "role": "user",  "email": "carol@example.com"},
        ],
        "orders": [
            {"id": 1, "user_id": 1, "total": 150.00, "status": "completed"},
            {"id": 2, "user_id": 2, "total": 89.99,  "status": "pending"},
        ],
    }

    def query(self, sql: str, params: tuple = ()) -> list[dict]:
        time.sleep(0.05)  # simulate DB latency
        sql_lower = sql.lower()
        for table, rows in self._fake_data.items():
            if table in sql_lower:
                return list(rows)
        return []

    def execute(self, sql: str, params: tuple = ()) -> int:
        time.sleep(0.02)
        return 1  # rows affected


# ---------------------------------------------------------------------------
# Proxy 1: Logging Proxy
# ---------------------------------------------------------------------------

@dataclass
class AuditEntry:
    timestamp: datetime
    sql: str
    params: tuple
    duration_ms: float
    result_count: int
    user: str = "system"


class LoggingProxy(DatabaseService):
    def __init__(self, service: DatabaseService):
        self._service = service
        self._audit_log: list[AuditEntry] = []

    def query(self, sql: str, params: tuple = ()) -> list[dict]:
        start = time.perf_counter()
        result = self._service.query(sql, params)
        elapsed = (time.perf_counter() - start) * 1000
        entry = AuditEntry(datetime.now(), sql, params, elapsed, len(result))
        self._audit_log.append(entry)
        print(f"  [Log] QUERY | {elapsed:.1f}ms | {len(result)} rows | SQL: {sql[:60]}")
        return result

    def execute(self, sql: str, params: tuple = ()) -> int:
        start = time.perf_counter()
        result = self._service.execute(sql, params)
        elapsed = (time.perf_counter() - start) * 1000
        self._audit_log.append(AuditEntry(datetime.now(), sql, params, elapsed, result))
        print(f"  [Log] EXEC  | {elapsed:.1f}ms | {result} rows affected | SQL: {sql[:60]}")
        return result

    def print_audit(self) -> None:
        print("\n  --- Audit Log ---")
        for e in self._audit_log:
            print(f"  {e.timestamp.strftime('%H:%M:%S')} | {e.duration_ms:.1f}ms | {e.sql[:50]}")


# ---------------------------------------------------------------------------
# Proxy 2: Caching Proxy
# ---------------------------------------------------------------------------

@dataclass
class CacheEntry:
    result: list[dict]
    created_at: float
    hits: int = 0


class CachingProxy(DatabaseService):
    def __init__(self, service: DatabaseService, ttl_seconds: float = 30.0):
        self._service = service
        self._cache: dict[str, CacheEntry] = {}
        self._ttl = ttl_seconds
        self._hits = 0
        self._misses = 0

    def _cache_key(self, sql: str, params: tuple) -> str:
        raw = f"{sql}:{params}"
        return hashlib.md5(raw.encode()).hexdigest()

    def _is_valid(self, entry: CacheEntry) -> bool:
        return (time.time() - entry.created_at) < self._ttl

    def query(self, sql: str, params: tuple = ()) -> list[dict]:
        key = self._cache_key(sql, params)
        if key in self._cache and self._is_valid(self._cache[key]):
            self._cache[key].hits += 1
            self._hits += 1
            print(f"  [Cache] HIT  (hits={self._cache[key].hits}) | {sql[:50]}")
            return list(self._cache[key].result)

        self._misses += 1
        print(f"  [Cache] MISS | {sql[:50]}")
        result = self._service.query(sql, params)
        self._cache[key] = CacheEntry(result=result, created_at=time.time())
        return result

    def execute(self, sql: str, params: tuple = ()) -> int:
        # Invalidate cache on writes
        self._cache.clear()
        print(f"  [Cache] INVALIDATED (write operation)")
        return self._service.execute(sql, params)

    def stats(self) -> dict:
        return {"hits": self._hits, "misses": self._misses,
                "ratio": self._hits / (self._hits + self._misses) if (self._hits + self._misses) else 0,
                "cached_queries": len(self._cache)}


# ---------------------------------------------------------------------------
# Proxy 3: Protection Proxy
# ---------------------------------------------------------------------------

@dataclass
class User:
    name: str
    role: str  # admin, user, readonly


class ProtectionProxy(DatabaseService):
    _write_roles = {"admin"}
    _read_roles = {"admin", "user", "readonly"}

    def __init__(self, service: DatabaseService, user: User):
        self._service = service
        self._user = user

    def _check_read(self) -> None:
        if self._user.role not in self._read_roles:
            raise PermissionError(f"User '{self._user.name}' (role={self._user.role}) has no read access")

    def _check_write(self) -> None:
        if self._user.role not in self._write_roles:
            raise PermissionError(f"User '{self._user.name}' (role={self._user.role}) has no write access")

    def query(self, sql: str, params: tuple = ()) -> list[dict]:
        self._check_read()
        print(f"  [Auth] READ granted for '{self._user.name}' (role={self._user.role})")
        return self._service.query(sql, params)

    def execute(self, sql: str, params: tuple = ()) -> int:
        self._check_write()
        print(f"  [Auth] WRITE granted for '{self._user.name}' (role={self._user.role})")
        return self._service.execute(sql, params)


# ---------------------------------------------------------------------------
# Demo
# ---------------------------------------------------------------------------

def main():
    print("=" * 55)
    print("  Proxy Pattern — Database Service Demo")
    print("=" * 55)

    real_db = RealDatabaseService()

    # Stack: Protection → Caching → Logging → Real DB
    def build_stack(user: User) -> DatabaseService:
        return ProtectionProxy(
            CachingProxy(
                LoggingProxy(real_db),
                ttl_seconds=10
            ),
            user=user
        )

    # --- Admin user ---
    print("\n>>> Admin user queries")
    admin = User("Alice", "admin")
    db = build_stack(admin)

    db.query("SELECT * FROM users")
    db.query("SELECT * FROM users")   # cache hit
    db.query("SELECT * FROM orders")
    db.execute("UPDATE users SET active=1 WHERE id=1")
    db.query("SELECT * FROM users")   # cache invalidated, miss again

    # --- Readonly user ---
    print("\n>>> Readonly user (read OK, write blocked)")
    readonly = User("Guest", "readonly")
    db2 = build_stack(readonly)
    db2.query("SELECT * FROM orders")

    try:
        db2.execute("DELETE FROM orders WHERE id=1")
    except PermissionError as e:
        print(f"  [Auth] BLOCKED: {e}")

    # --- Cache stats ---
    cache_proxy = CachingProxy(LoggingProxy(real_db), ttl_seconds=10)
    for _ in range(5):
        cache_proxy.query("SELECT * FROM users")
    print(f"\n  Cache stats: {cache_proxy.stats()}")


if __name__ == "__main__":
    main()
