"""
Chain of Responsibility Design Pattern - Advanced Implementation
Real-world scenario: HTTP Middleware Pipeline
Each middleware handles or passes the request down the chain.
"""
from __future__ import annotations
import hashlib
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


# ---------------------------------------------------------------------------
# Request / Response models
# ---------------------------------------------------------------------------

@dataclass
class HttpRequest:
    method: str
    path: str
    headers: dict = field(default_factory=dict)
    body: dict = field(default_factory=dict)
    user: Optional[str] = None
    role: Optional[str] = None
    ip: str = "127.0.0.1"
    request_id: str = field(default_factory=lambda: hashlib.md5(
        str(time.time()).encode()).hexdigest()[:8])


@dataclass
class HttpResponse:
    status: int
    body: dict = field(default_factory=dict)
    headers: dict = field(default_factory=dict)

    @classmethod
    def ok(cls, body: dict = None) -> HttpResponse:
        return cls(200, body or {"status": "ok"})

    @classmethod
    def error(cls, status: int, message: str) -> HttpResponse:
        return cls(status, {"error": message})

    def __str__(self) -> str:
        return f"HTTP {self.status} | {self.body}"


# ---------------------------------------------------------------------------
# Handler Interface
# ---------------------------------------------------------------------------

class Middleware(ABC):
    def __init__(self):
        self._next: Optional[Middleware] = None

    def set_next(self, handler: Middleware) -> Middleware:
        self._next = handler
        return handler  # allows chaining: a.set_next(b).set_next(c)

    def pass_to_next(self, request: HttpRequest) -> HttpResponse:
        if self._next:
            return self._next.handle(request)
        return HttpResponse.ok({"message": "Request processed successfully"})

    @abstractmethod
    def handle(self, request: HttpRequest) -> HttpResponse: ...

    @property
    def name(self) -> str:
        return self.__class__.__name__


# ---------------------------------------------------------------------------
# Concrete Handlers
# ---------------------------------------------------------------------------

class RequestLoggerMiddleware(Middleware):
    def __init__(self):
        super().__init__()
        self._log: list[str] = []

    def handle(self, request: HttpRequest) -> HttpResponse:
        start = time.perf_counter()
        print(f"  [Logger] -> {request.method} {request.path} | id={request.request_id} | ip={request.ip}")
        response = self.pass_to_next(request)
        elapsed = (time.perf_counter() - start) * 1000
        entry = f"{datetime.now().strftime('%H:%M:%S')} {request.method} {request.path} {response.status} {elapsed:.1f}ms"
        self._log.append(entry)
        print(f"  [Logger] <- {response.status} | {elapsed:.1f}ms")
        return response


class RateLimiterMiddleware(Middleware):
    def __init__(self, max_requests: int = 5, window_seconds: float = 60):
        super().__init__()
        self._max = max_requests
        self._window = window_seconds
        self._requests: dict[str, list[float]] = {}

    def handle(self, request: HttpRequest) -> HttpResponse:
        ip = request.ip
        now = time.time()
        window_start = now - self._window
        hits = self._requests.get(ip, [])
        hits = [t for t in hits if t > window_start]
        hits.append(now)
        self._requests[ip] = hits

        if len(hits) > self._max:
            print(f"  [RateLimit] BLOCKED {ip} ({len(hits)}/{self._max} requests)")
            return HttpResponse.error(429, "Too Many Requests")

        print(f"  [RateLimit] OK {ip} ({len(hits)}/{self._max})")
        return self.pass_to_next(request)


class AuthenticationMiddleware(Middleware):
    _valid_tokens = {
        "token-admin-123": ("alice", "admin"),
        "token-user-456":  ("bob",   "user"),
        "token-guest-789": ("guest", "readonly"),
    }

    def handle(self, request: HttpRequest) -> HttpResponse:
        token = request.headers.get("Authorization", "").replace("Bearer ", "")
        if not token:
            print(f"  [Auth] REJECTED — no token")
            return HttpResponse.error(401, "Unauthorized — missing token")

        if token not in self._valid_tokens:
            print(f"  [Auth] REJECTED — invalid token")
            return HttpResponse.error(401, "Unauthorized — invalid token")

        request.user, request.role = self._valid_tokens[token]
        print(f"  [Auth] OK — user='{request.user}' role='{request.role}'")
        return self.pass_to_next(request)


class AuthorizationMiddleware(Middleware):
    _permissions = {
        "/admin":        {"admin"},
        "/users":        {"admin", "user"},
        "/orders":       {"admin", "user"},
        "/public":       {"admin", "user", "readonly"},
    }

    def handle(self, request: HttpRequest) -> HttpResponse:
        allowed_roles = self._permissions.get(request.path, {"admin"})
        if request.role not in allowed_roles:
            print(f"  [Authz] FORBIDDEN — role='{request.role}' cannot access {request.path}")
            return HttpResponse.error(403, f"Forbidden — role '{request.role}' not allowed")
        print(f"  [Authz] ALLOWED — role='{request.role}' -> {request.path}")
        return self.pass_to_next(request)


class InputValidationMiddleware(Middleware):
    _required_fields = {
        ("POST", "/users"):  ["name", "email"],
        ("POST", "/orders"): ["user_id", "items"],
    }

    def handle(self, request: HttpRequest) -> HttpResponse:
        key = (request.method, request.path)
        required = self._required_fields.get(key, [])
        missing = [f for f in required if f not in request.body]
        if missing:
            print(f"  [Validation] FAILED — missing fields: {missing}")
            return HttpResponse.error(400, f"Missing required fields: {missing}")
        print(f"  [Validation] OK")
        return self.pass_to_next(request)


class BusinessLogicHandler(Middleware):
    """Terminal handler — actually processes the request."""

    def handle(self, request: HttpRequest) -> HttpResponse:
        print(f"  [Business] Processing {request.method} {request.path} for user='{request.user}'")
        responses = {
            "/users":  {"users": [{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}]},
            "/orders": {"orders": [{"id": 1, "total": 99.99}]},
            "/admin":  {"dashboard": "admin panel data"},
            "/public": {"message": "Welcome!"},
        }
        data = responses.get(request.path, {"result": "processed"})
        return HttpResponse.ok(data)


# ---------------------------------------------------------------------------
# Pipeline builder
# ---------------------------------------------------------------------------

def build_pipeline() -> Middleware:
    logger   = RequestLoggerMiddleware()
    limiter  = RateLimiterMiddleware(max_requests=10)
    auth_n   = AuthenticationMiddleware()
    valid    = InputValidationMiddleware()
    auth_z   = AuthorizationMiddleware()
    business = BusinessLogicHandler()

    logger.set_next(limiter).set_next(auth_n).set_next(valid).set_next(auth_z).set_next(business)
    return logger


# ---------------------------------------------------------------------------
# Demo
# ---------------------------------------------------------------------------

def main():
    print("=" * 55)
    print("  Chain of Responsibility — HTTP Middleware Demo")
    print("=" * 55)

    pipeline = build_pipeline()

    scenarios = [
        ("Admin accesses /admin", HttpRequest(
            "GET", "/admin",
            headers={"Authorization": "Bearer token-admin-123"}
        )),
        ("User accesses /users", HttpRequest(
            "GET", "/users",
            headers={"Authorization": "Bearer token-user-456"}
        )),
        ("Readonly tries /admin (forbidden)", HttpRequest(
            "GET", "/admin",
            headers={"Authorization": "Bearer token-guest-789"}
        )),
        ("No token (unauthorized)", HttpRequest(
            "GET", "/users", headers={}
        )),
        ("POST /users with missing fields", HttpRequest(
            "POST", "/users",
            headers={"Authorization": "Bearer token-admin-123"},
            body={"name": "Dave"}  # missing email
        )),
        ("POST /users valid", HttpRequest(
            "POST", "/users",
            headers={"Authorization": "Bearer token-admin-123"},
            body={"name": "Dave", "email": "dave@example.com"}
        )),
        ("Public endpoint (readonly OK)", HttpRequest(
            "GET", "/public",
            headers={"Authorization": "Bearer token-guest-789"}
        )),
    ]

    for label, request in scenarios:
        print(f"\n>>> {label}")
        response = pipeline.handle(request)
        print(f"  Result: {response}")


if __name__ == "__main__":
    main()
