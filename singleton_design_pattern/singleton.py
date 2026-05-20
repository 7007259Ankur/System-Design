"""
Singleton Design Pattern - Advanced Implementation
Demonstrates: Classic, Thread-safe, Metaclass, and Borg variants.
Real-world scenario: App Config Manager + DB Connection Pool
"""
from __future__ import annotations
import threading
import time
from typing import Any, Optional


# ---------------------------------------------------------------------------
# Variant 1: Thread-safe Singleton with double-checked locking
# ---------------------------------------------------------------------------

class AppConfig:
    """
    Thread-safe singleton configuration manager.
    Only one instance exists across the entire application.
    """
    _instance: Optional[AppConfig] = None
    _lock: threading.Lock = threading.Lock()

    def __new__(cls) -> AppConfig:
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:  # double-checked locking
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._config: dict[str, Any] = {
            "app_name": "DesignPatterns",
            "version": "1.0.0",
            "debug": False,
            "db_host": "localhost",
            "db_port": 5432,
            "max_connections": 10,
            "log_level": "INFO",
        }
        self._initialized = True
        print(f"AppConfig initialized (id={id(self)})")

    def get(self, key: str, default: Any = None) -> Any:
        return self._config.get(key, default)

    def set(self, key: str, value: Any) -> None:
        self._config[key] = value

    def update(self, **kwargs) -> None:
        self._config.update(kwargs)

    def __repr__(self) -> str:
        return f"AppConfig(id={id(self)}, keys={list(self._config.keys())})"


# ---------------------------------------------------------------------------
# Variant 2: Metaclass Singleton
# ---------------------------------------------------------------------------

class SingletonMeta(type):
    _instances: dict[type, Any] = {}
    _lock: threading.Lock = threading.Lock()

    def __call__(cls, *args, **kwargs):
        with cls._lock:
            if cls not in cls._instances:
                instance = super().__call__(*args, **kwargs)
                cls._instances[cls] = instance
        return cls._instances[cls]


class DatabaseConnectionPool(metaclass=SingletonMeta):
    """
    Metaclass-based singleton connection pool.
    Manages a fixed pool of reusable DB connections.
    """

    def __init__(self, max_size: int = 5):
        self._max_size = max_size
        self._pool: list[dict] = []
        self._in_use: list[dict] = []
        self._lock = threading.Lock()
        self._create_connections()
        print(f"ConnectionPool initialized with {max_size} connections (id={id(self)})")

    def _create_connections(self) -> None:
        for i in range(self._max_size):
            self._pool.append({"id": i + 1, "host": "localhost", "active": False})

    def acquire(self) -> Optional[dict]:
        with self._lock:
            if not self._pool:
                print("  Pool exhausted — no connections available")
                return None
            conn = self._pool.pop(0)
            conn["active"] = True
            self._in_use.append(conn)
            print(f"  Acquired connection #{conn['id']} | pool remaining: {len(self._pool)}")
            return conn

    def release(self, conn: dict) -> None:
        with self._lock:
            conn["active"] = False
            self._in_use.remove(conn)
            self._pool.append(conn)
            print(f"  Released connection #{conn['id']} | pool available: {len(self._pool)}")

    @property
    def stats(self) -> dict:
        return {"available": len(self._pool), "in_use": len(self._in_use), "total": self._max_size}


# ---------------------------------------------------------------------------
# Variant 3: Borg Pattern (shared state, multiple instances)
# ---------------------------------------------------------------------------

class Logger:
    """
    Borg pattern — all instances share the same state dict.
    Unlike Singleton, you can create multiple instances but they all behave as one.
    """
    _shared_state: dict = {"entries": [], "level": "INFO"}

    def __init__(self):
        self.__dict__ = self._shared_state

    def log(self, level: str, message: str) -> None:
        entry = f"[{level}] {message}"
        self.entries.append(entry)
        print(f"  Logger: {entry}")

    def set_level(self, level: str) -> None:
        self.level = level

    def get_history(self) -> list[str]:
        return self.entries


# ---------------------------------------------------------------------------
# Demo
# ---------------------------------------------------------------------------

def main():
    print("=" * 55)
    print("  Singleton Pattern — Config, Pool, Logger Demo")
    print("=" * 55)

    # --- AppConfig: same instance every time ---
    print("\n>>> Thread-safe Singleton (AppConfig)")
    cfg1 = AppConfig()
    cfg2 = AppConfig()
    print(f"  cfg1 is cfg2: {cfg1 is cfg2}")
    cfg1.set("debug", True)
    print(f"  cfg2.debug = {cfg2.get('debug')}  <- same instance")

    # Prove thread safety
    instances = []
    def create_config():
        instances.append(AppConfig())

    threads = [threading.Thread(target=create_config) for _ in range(10)]
    for t in threads: t.start()
    for t in threads: t.join()
    unique = set(id(i) for i in instances)
    print(f"  10 threads created {len(unique)} unique instance(s) OK")

    # --- ConnectionPool ---
    print("\n>>> Metaclass Singleton (ConnectionPool)")
    pool1 = DatabaseConnectionPool(max_size=3)
    pool2 = DatabaseConnectionPool(max_size=99)  # ignored — already initialized
    print(f"  pool1 is pool2: {pool1 is pool2}")
    print(f"  pool2.max_size = {pool2._max_size}  <- still 3")

    c1 = pool1.acquire()
    c2 = pool1.acquire()
    print(f"  Stats: {pool1.stats}")
    pool1.release(c1)
    print(f"  Stats: {pool1.stats}")
    pool1.release(c2)

    # --- Borg Logger ---
    print("\n>>> Borg Pattern (Logger)")
    log_a = Logger()
    log_b = Logger()
    log_a.log("INFO", "Application started")
    log_b.log("WARNING", "Low memory")
    log_a.set_level("DEBUG")
    print(f"  log_b.level = '{log_b.level}'  <- shared state")
    print(f"  log_a is log_b: {log_a is log_b}  <- different objects, same state")
    print(f"  Shared history: {log_b.get_history()}")


if __name__ == "__main__":
    main()
