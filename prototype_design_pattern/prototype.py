"""
Prototype Design Pattern - Advanced Implementation
Real-world scenario: Game Character System
Clone base archetypes and customize — avoid expensive re-initialization.
"""
from __future__ import annotations
import copy
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional


# ---------------------------------------------------------------------------
# Prototype Interface
# ---------------------------------------------------------------------------

class Prototype(ABC):
    @abstractmethod
    def clone(self) -> Prototype:
        """Return a deep copy of this object."""
        ...

    def shallow_clone(self) -> Prototype:
        return copy.copy(self)


# ---------------------------------------------------------------------------
# Domain models
# ---------------------------------------------------------------------------

@dataclass
class Equipment:
    weapon: str
    armor: str
    accessory: str

    def __str__(self) -> str:
        return f"{self.weapon} / {self.armor} / {self.accessory}"


@dataclass
class Stats:
    hp: int
    mp: int
    attack: int
    defense: int
    speed: int
    magic: int

    def __str__(self) -> str:
        return f"HP:{self.hp} MP:{self.mp} ATK:{self.attack} DEF:{self.defense} SPD:{self.speed} MAG:{self.magic}"


# ---------------------------------------------------------------------------
# Concrete Prototype
# ---------------------------------------------------------------------------

class GameCharacter(Prototype):
    def __init__(self, name: str, char_class: str, level: int,
                 stats: Stats, equipment: Equipment, skills: list[str]):
        self.name = name
        self.char_class = char_class
        self.level = level
        self.stats = stats
        self.equipment = equipment
        self.skills = skills
        self.status_effects: list[str] = []
        self.inventory: list[str] = []

    def clone(self) -> GameCharacter:
        """Deep clone — fully independent copy."""
        cloned = copy.deepcopy(self)
        cloned.name = f"{self.name} (clone)"
        return cloned

    def with_name(self, name: str) -> GameCharacter:
        c = self.clone()
        c.name = name
        return c

    def with_level(self, level: int) -> GameCharacter:
        c = self.clone()
        c.level = level
        # Scale stats with level
        factor = level / self.level if self.level else 1
        c.stats = Stats(
            hp=int(self.stats.hp * factor),
            mp=int(self.stats.mp * factor),
            attack=int(self.stats.attack * factor),
            defense=int(self.stats.defense * factor),
            speed=self.stats.speed,
            magic=int(self.stats.magic * factor),
        )
        return c

    def with_equipment(self, equipment: Equipment) -> GameCharacter:
        c = self.clone()
        c.equipment = copy.deepcopy(equipment)
        return c

    def add_skill(self, skill: str) -> GameCharacter:
        c = self.clone()
        c.skills.append(skill)
        return c

    def display(self) -> None:
        print(f"\n  [{self.char_class}] {self.name} (Lv.{self.level})")
        print(f"    Stats:     {self.stats}")
        print(f"    Equipment: {self.equipment}")
        print(f"    Skills:    {', '.join(self.skills)}")


# ---------------------------------------------------------------------------
# Prototype Registry
# ---------------------------------------------------------------------------

class CharacterRegistry:
    """Stores named archetypes. Clone from here instead of building from scratch."""

    _archetypes: dict[str, GameCharacter] = {}

    @classmethod
    def register(cls, key: str, character: GameCharacter) -> None:
        cls._archetypes[key] = character
        print(f"Registry: registered archetype '{key}'")

    @classmethod
    def get(cls, key: str) -> GameCharacter:
        if key not in cls._archetypes:
            raise KeyError(f"No archetype '{key}'. Available: {list(cls._archetypes)}")
        return cls._archetypes[key].clone()

    @classmethod
    def list_archetypes(cls) -> list[str]:
        return list(cls._archetypes.keys())


# ---------------------------------------------------------------------------
# Demo
# ---------------------------------------------------------------------------

def main():
    print("=" * 55)
    print("  Prototype Pattern — Game Character System Demo")
    print("=" * 55)

    # Define base archetypes
    warrior_archetype = GameCharacter(
        name="Warrior", char_class="Warrior", level=1,
        stats=Stats(hp=200, mp=50, attack=80, defense=70, speed=50, magic=20),
        equipment=Equipment("Iron Sword", "Chain Mail", "Shield"),
        skills=["Slash", "Block", "War Cry"],
    )

    mage_archetype = GameCharacter(
        name="Mage", char_class="Mage", level=1,
        stats=Stats(hp=80, mp=200, attack=30, defense=20, speed=60, magic=120),
        equipment=Equipment("Staff", "Robe", "Magic Ring"),
        skills=["Fireball", "Ice Shard", "Mana Shield"],
    )

    archer_archetype = GameCharacter(
        name="Archer", char_class="Archer", level=1,
        stats=Stats(hp=120, mp=80, attack=90, defense=40, speed=100, magic=30),
        equipment=Equipment("Longbow", "Leather Armor", "Quiver"),
        skills=["Arrow Shot", "Multi-Shot", "Eagle Eye"],
    )

    # Register archetypes
    print()
    CharacterRegistry.register("warrior", warrior_archetype)
    CharacterRegistry.register("mage", mage_archetype)
    CharacterRegistry.register("archer", archer_archetype)

    # Clone and customize — no expensive re-initialization
    print("\n>>> Cloning and customizing characters")

    hero = CharacterRegistry.get("warrior").with_name("Aragorn").with_level(20)
    hero.equipment = Equipment("Excalibur", "Dragon Scale Armor", "Amulet of Valor")
    hero.display()

    boss_mage = (CharacterRegistry.get("mage")
                 .with_name("Gandalf")
                 .with_level(50)
                 .add_skill("Meteor")
                 .add_skill("Time Stop"))
    boss_mage.display()

    # Prove deep copy — modifying clone doesn't affect archetype
    print("\n>>> Proving deep copy independence")
    clone1 = CharacterRegistry.get("archer").with_name("Legolas")
    clone2 = CharacterRegistry.get("archer").with_name("Robin Hood")
    clone1.skills.append("Poison Arrow")
    clone2.skills.append("Explosive Arrow")

    print(f"  Legolas skills:    {clone1.skills}")
    print(f"  Robin Hood skills: {clone2.skills}")
    print(f"  Archetype skills:  {archer_archetype.skills}  <- unchanged")

    # Spawn enemy wave by cloning
    print("\n>>> Spawning enemy wave (5 goblins from one archetype)")
    goblin_archetype = GameCharacter(
        name="Goblin", char_class="Enemy", level=5,
        stats=Stats(hp=40, mp=10, attack=25, defense=10, speed=70, magic=5),
        equipment=Equipment("Rusty Dagger", "Rags", "None"),
        skills=["Stab", "Flee"],
    )
    CharacterRegistry.register("goblin", goblin_archetype)

    wave = [CharacterRegistry.get("goblin").with_name(f"Goblin #{i+1}") for i in range(5)]
    for g in wave:
        print(f"  Spawned: {g.name} | HP: {g.stats.hp}")


if __name__ == "__main__":
    main()
