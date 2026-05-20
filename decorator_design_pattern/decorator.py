"""
Decorator Design Pattern - Advanced Implementation
Real-world scenario: Data Stream Pipeline
Stack encryption, compression, buffering, and logging decorators
in any order at runtime.
"""
from __future__ import annotations
import base64
import hashlib
import time
import zlib
from abc import ABC, abstractmethod
from typing import Optional


# ---------------------------------------------------------------------------
# Component Interface
# ---------------------------------------------------------------------------

class DataStream(ABC):
    @abstractmethod
    def write(self, data: bytes) -> int: ...

    @abstractmethod
    def read(self) -> bytes: ...

    @abstractmethod
    def close(self) -> None: ...

    @property
    @abstractmethod
    def name(self) -> str: ...


# ---------------------------------------------------------------------------
# Concrete Component
# ---------------------------------------------------------------------------

class FileDataStream(DataStream):
    def __init__(self, filename: str):
        self._filename = filename
        self._buffer: bytes = b""
        self._closed = False

    def write(self, data: bytes) -> int:
        if self._closed:
            raise IOError("Stream is closed")
        self._buffer += data
        return len(data)

    def read(self) -> bytes:
        return self._buffer

    def close(self) -> None:
        self._closed = True

    @property
    def name(self) -> str:
        return f"FileStream({self._filename})"


class MemoryDataStream(DataStream):
    def __init__(self):
        self._buffer: bytes = b""

    def write(self, data: bytes) -> int:
        self._buffer += data
        return len(data)

    def read(self) -> bytes:
        return self._buffer

    def close(self) -> None:
        pass

    @property
    def name(self) -> str:
        return "MemoryStream"


# ---------------------------------------------------------------------------
# Base Decorator
# ---------------------------------------------------------------------------

class DataStreamDecorator(DataStream):
    def __init__(self, wrapped: DataStream):
        self._wrapped = wrapped

    def write(self, data: bytes) -> int:
        return self._wrapped.write(data)

    def read(self) -> bytes:
        return self._wrapped.read()

    def close(self) -> None:
        self._wrapped.close()

    @property
    def name(self) -> str:
        return self._wrapped.name


# ---------------------------------------------------------------------------
# Concrete Decorators
# ---------------------------------------------------------------------------

class CompressionDecorator(DataStreamDecorator):
    """Compresses data on write, decompresses on read."""

    def __init__(self, wrapped: DataStream, level: int = 6):
        super().__init__(wrapped)
        self._level = level
        self._original_size = 0
        self._compressed_size = 0

    def write(self, data: bytes) -> int:
        self._original_size = len(data)
        compressed = zlib.compress(data, self._level)
        self._compressed_size = len(compressed)
        ratio = (1 - self._compressed_size / self._original_size) * 100 if self._original_size else 0
        print(f"  [Compression] {self._original_size}B -> {self._compressed_size}B ({ratio:.1f}% reduction)")
        return super().write(compressed)

    def read(self) -> bytes:
        compressed = super().read()
        return zlib.decompress(compressed) if compressed else b""

    @property
    def name(self) -> str:
        return f"Compressed({super().name})"


class EncryptionDecorator(DataStreamDecorator):
    """XOR-based encryption (demo purposes — use AES in production)."""

    def __init__(self, wrapped: DataStream, key: str):
        super().__init__(wrapped)
        self._key = key.encode()

    def _xor(self, data: bytes) -> bytes:
        key = self._key
        return bytes(b ^ key[i % len(key)] for i, b in enumerate(data))

    def write(self, data: bytes) -> int:
        encrypted = self._xor(data)
        encoded = base64.b64encode(encrypted)
        print(f"  [Encryption] Encrypted {len(data)}B -> {len(encoded)}B (base64)")
        return super().write(encoded)

    def read(self) -> bytes:
        encoded = super().read()
        if not encoded:
            return b""
        encrypted = base64.b64decode(encoded)
        return self._xor(encrypted)

    @property
    def name(self) -> str:
        return f"Encrypted({super().name})"


class BufferingDecorator(DataStreamDecorator):
    """Buffers writes and flushes when buffer is full or flush() is called."""

    def __init__(self, wrapped: DataStream, buffer_size: int = 64):
        super().__init__(wrapped)
        self._buffer_size = buffer_size
        self._buffer: bytes = b""
        self._flush_count = 0

    def write(self, data: bytes) -> int:
        self._buffer += data
        written = 0
        while len(self._buffer) >= self._buffer_size:
            chunk = self._buffer[:self._buffer_size]
            self._buffer = self._buffer[self._buffer_size:]
            written += super().write(chunk)
            self._flush_count += 1
            print(f"  [Buffer] Auto-flush #{self._flush_count}: {len(chunk)}B chunk")
        return len(data)

    def flush(self) -> int:
        if self._buffer:
            written = super().write(self._buffer)
            print(f"  [Buffer] Manual flush: {len(self._buffer)}B")
            self._buffer = b""
            return written
        return 0

    def close(self) -> None:
        self.flush()
        super().close()

    @property
    def name(self) -> str:
        return f"Buffered({super().name})"


class LoggingDecorator(DataStreamDecorator):
    """Logs all read/write operations with timing."""

    def __init__(self, wrapped: DataStream, label: str = ""):
        super().__init__(wrapped)
        self._label = label or wrapped.name
        self._write_count = 0
        self._read_count = 0
        self._total_written = 0

    def write(self, data: bytes) -> int:
        start = time.perf_counter()
        result = super().write(data)
        elapsed = (time.perf_counter() - start) * 1000
        self._write_count += 1
        self._total_written += len(data)
        checksum = hashlib.md5(data).hexdigest()[:8]
        print(f"  [Log] WRITE #{self._write_count}: {len(data)}B | md5={checksum} | {elapsed:.2f}ms")
        return result

    def read(self) -> bytes:
        start = time.perf_counter()
        data = super().read()
        elapsed = (time.perf_counter() - start) * 1000
        self._read_count += 1
        print(f"  [Log] READ #{self._read_count}: {len(data)}B | {elapsed:.2f}ms")
        return data

    def stats(self) -> dict:
        return {"writes": self._write_count, "reads": self._read_count,
                "total_written": self._total_written}

    @property
    def name(self) -> str:
        return f"Logged({super().name})"


# ---------------------------------------------------------------------------
# Demo
# ---------------------------------------------------------------------------

def main():
    print("=" * 55)
    print("  Decorator Pattern — Data Stream Pipeline Demo")
    print("=" * 55)

    payload = b"Hello, Design Patterns! " * 20  # 480 bytes

    # --- Stack 1: Logging only ---
    print(f"\n>>> Stack 1: Logging only")
    stream = LoggingDecorator(MemoryDataStream())
    stream.write(payload)
    result = stream.read()
    print(f"  Roundtrip OK: {result == payload}")

    # --- Stack 2: Compression + Logging ---
    print(f"\n>>> Stack 2: Compression -> Logging")
    stream = LoggingDecorator(CompressionDecorator(MemoryDataStream()))
    stream.write(payload)
    result = stream.read()
    print(f"  Roundtrip OK: {result == payload}")

    # --- Stack 3: Encryption + Compression + Logging ---
    print(f"\n>>> Stack 3: Encryption -> Compression -> Logging")
    stream = LoggingDecorator(
        EncryptionDecorator(
            CompressionDecorator(MemoryDataStream()),
            key="secret-key-123"
        )
    )
    stream.write(payload)
    result = stream.read()
    print(f"  Roundtrip OK: {result == payload}")

    # --- Stack 4: Full pipeline with buffering ---
    print(f"\n>>> Stack 4: Full pipeline (Buffer -> Encrypt -> Compress -> Log -> File)")
    file_stream = FileDataStream("output.dat")
    stream = BufferingDecorator(
        EncryptionDecorator(
            CompressionDecorator(file_stream),
            key="my-secret"
        ),
        buffer_size=100
    )
    logged = LoggingDecorator(stream)
    logged.write(payload)
    logged.close()
    print(f"  Pipeline name: {logged.name}")

    # --- Demonstrate order matters ---
    print(f"\n>>> Order matters: Compress-then-Encrypt vs Encrypt-then-Compress")
    data = b"Sensitive data that should be compressed and encrypted"

    s1 = EncryptionDecorator(CompressionDecorator(MemoryDataStream()), "key")
    s1.write(data)
    r1 = s1.read()

    s2 = CompressionDecorator(EncryptionDecorator(MemoryDataStream(), "key"))
    s2.write(data)
    r2 = s2.read()

    print(f"  Both roundtrip correctly: {r1 == data and r2 == data}")


if __name__ == "__main__":
    main()
