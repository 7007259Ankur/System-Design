"""
Flyweight Design Pattern - Advanced Implementation
Real-world scenario: Game Particle System
Thousands of particles share intrinsic state (texture, color, sprite).
Extrinsic state (position, velocity) is passed at render time.
"""
from __future__ import annotations
import random
import sys
from dataclasses import dataclass
from typing import Optional


# ---------------------------------------------------------------------------
# Flyweight — stores intrinsic (shared, immutable) state
# ---------------------------------------------------------------------------

class ParticleType:
    """
    Flyweight object. Shared among thousands of particles.
    Contains only data that is the same for all particles of this type.
    """

    def __init__(self, name: str, color: str, sprite: str,
                 texture_path: str, size: int, blend_mode: str):
        self.name = name
        self.color = color
        self.sprite = sprite
        self.texture_path = texture_path
        self.size = size
        self.blend_mode = blend_mode
        # Simulate texture data in memory (intrinsic, shared)
        self._texture_data = bytes(size * size * 4)  # RGBA pixels

    def render(self, x: float, y: float, vx: float, vy: float,
               alpha: float, scale: float) -> str:
        """Render using shared intrinsic state + passed extrinsic state."""
        return (f"[{self.name}] sprite={self.sprite} color={self.color} "
                f"pos=({x:.1f},{y:.1f}) vel=({vx:.1f},{vy:.1f}) "
                f"alpha={alpha:.2f} scale={scale:.2f}")

    def memory_size(self) -> int:
        """Approximate memory footprint of this flyweight."""
        return sys.getsizeof(self) + len(self._texture_data)

    def __repr__(self) -> str:
        return f"ParticleType({self.name})"


# ---------------------------------------------------------------------------
# Flyweight Factory — caches and reuses flyweights
# ---------------------------------------------------------------------------

class ParticleTypeFactory:
    _cache: dict[str, ParticleType] = {}

    @classmethod
    def get(cls, name: str, color: str, sprite: str,
            texture_path: str, size: int = 32, blend_mode: str = "alpha") -> ParticleType:
        key = f"{name}:{color}:{sprite}"
        if key not in cls._cache:
            cls._cache[key] = ParticleType(name, color, sprite, texture_path, size, blend_mode)
            print(f"  FlyweightFactory: created new ParticleType '{name}' (key={key})")
        return cls._cache[key]

    @classmethod
    def cache_size(cls) -> int:
        return len(cls._cache)

    @classmethod
    def total_flyweight_memory(cls) -> int:
        return sum(pt.memory_size() for pt in cls._cache.values())

    @classmethod
    def list_types(cls) -> list[str]:
        return list(cls._cache.keys())


# ---------------------------------------------------------------------------
# Context — stores extrinsic (unique per particle) state
# ---------------------------------------------------------------------------

@dataclass
class Particle:
    """
    Lightweight context object. Stores only what's unique per particle.
    Delegates rendering to the shared flyweight.
    """
    x: float
    y: float
    vx: float
    vy: float
    alpha: float
    scale: float
    particle_type: ParticleType  # reference to shared flyweight

    def update(self, dt: float) -> None:
        """Update extrinsic state (physics)."""
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.alpha = max(0.0, self.alpha - 0.01 * dt)

    def render(self) -> str:
        return self.particle_type.render(
            self.x, self.y, self.vx, self.vy, self.alpha, self.scale
        )

    def is_alive(self) -> bool:
        return self.alpha > 0.0


# ---------------------------------------------------------------------------
# Particle System — manages thousands of particles
# ---------------------------------------------------------------------------

class ParticleSystem:
    def __init__(self):
        self._particles: list[Particle] = []
        self._factory = ParticleTypeFactory()

    def _get_type(self, effect: str) -> ParticleType:
        configs = {
            "bullet":    ("Bullet",    "yellow", "*", "textures/bullet.png",    8,  "additive"),
            "explosion": ("Explosion", "orange", "✸", "textures/explosion.png", 64, "additive"),
            "smoke":     ("Smoke",     "gray",   "◌", "textures/smoke.png",     32, "alpha"),
            "spark":     ("Spark",     "white",  "·", "textures/spark.png",     4,  "additive"),
            "debris":    ("Debris",    "brown",  "▪", "textures/debris.png",    16, "alpha"),
            "rain":      ("Rain",      "cyan",   "|", "textures/rain.png",      2,  "alpha"),
        }
        cfg = configs.get(effect, configs["spark"])
        return ParticleTypeFactory.get(*cfg)

    def emit(self, effect: str, count: int, x: float, y: float) -> None:
        ptype = self._get_type(effect)
        for _ in range(count):
            self._particles.append(Particle(
                x=x + random.uniform(-10, 10),
                y=y + random.uniform(-10, 10),
                vx=random.uniform(-50, 50),
                vy=random.uniform(-100, 0),
                alpha=random.uniform(0.7, 1.0),
                scale=random.uniform(0.5, 2.0),
                particle_type=ptype,  # shared flyweight
            ))

    def update(self, dt: float) -> None:
        for p in self._particles:
            p.update(dt)
        self._particles = [p for p in self._particles if p.is_alive()]

    def render_sample(self, n: int = 5) -> None:
        for p in self._particles[:n]:
            print(f"  {p.render()}")

    def memory_report(self) -> None:
        particle_mem = sys.getsizeof(Particle.__dataclass_fields__) * len(self._particles)
        flyweight_mem = ParticleTypeFactory.total_flyweight_memory()
        naive_mem = (particle_mem + flyweight_mem) * len(self._particles)

        print(f"\n  Active particles:      {len(self._particles):,}")
        print(f"  Flyweight types:       {ParticleTypeFactory.cache_size()}")
        print(f"  Flyweight memory:      {flyweight_mem:,} bytes (shared)")
        print(f"  Particle context mem:  ~{particle_mem:,} bytes")
        print(f"  Naive (no flyweight):  ~{naive_mem:,} bytes")
        print(f"  Memory saved:          ~{naive_mem - particle_mem - flyweight_mem:,} bytes")


# ---------------------------------------------------------------------------
# Demo
# ---------------------------------------------------------------------------

def main():
    print("=" * 55)
    print("  Flyweight Pattern — Game Particle System Demo")
    print("=" * 55)

    system = ParticleSystem()

    print("\n>>> Emitting particles (flyweights created once, reused)")
    system.emit("bullet",    500,  100, 200)
    system.emit("explosion", 200,  300, 150)
    system.emit("smoke",     300,  300, 150)
    system.emit("spark",    1000,  300, 150)
    system.emit("debris",    200,  300, 150)
    system.emit("rain",     2000,  500, 0)
    # Emit more bullets — no new flyweight created
    system.emit("bullet",    500,  200, 300)
    system.emit("explosion", 300,  400, 200)

    print(f"\n  Flyweight types in cache: {ParticleTypeFactory.cache_size()}")
    print(f"  Types: {ParticleTypeFactory.list_types()}")

    print("\n>>> Sample renders (extrinsic state differs, intrinsic shared)")
    system.render_sample(6)

    print("\n>>> Memory report")
    system.memory_report()

    print("\n>>> After update (dead particles removed)")
    system.update(dt=100)
    print(f"  Alive particles: {len(system._particles):,}")
    print(f"  Flyweight types still in cache: {ParticleTypeFactory.cache_size()} (unchanged)")


if __name__ == "__main__":
    main()
