"""
Memento Design Pattern - Advanced Implementation
Real-world scenario: Game Save System
Save checkpoints, restore to any previous save, auto-save, named slots.
"""
from __future__ import annotations
import copy
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


# ---------------------------------------------------------------------------
# Memento — opaque snapshot (only Originator reads it)
# ---------------------------------------------------------------------------

@dataclass
class GameMemento:
    """Stores a complete snapshot of game state. Caretaker treats this as a black box."""
    _state: dict
    _timestamp: datetime = field(default_factory=datetime.now)
    _label: str = ""

    @property
    def timestamp(self) -> datetime:
        return self._timestamp

    @property
    def label(self) -> str:
        return self._label

    def __repr__(self) -> str:
        ts = self._timestamp.strftime("%H:%M:%S")
        return f"Save[{self._label or 'auto'}@{ts}]"


# ---------------------------------------------------------------------------
# Originator — the game state
# ---------------------------------------------------------------------------

@dataclass
class PlayerState:
    name: str
    level: int
    hp: int
    max_hp: int
    position: tuple
    inventory: list[str]
    gold: int
    skills: list[str]
    quest_flags: dict[str, bool]
    score: int


class GameWorld:
    """
    Originator. Creates and restores mementos.
    Only it knows how to serialize/deserialize its own state.
    """

    def __init__(self, player_name: str):
        self._player = PlayerState(
            name=player_name, level=1, hp=100, max_hp=100,
            position=(0, 0), inventory=["Sword", "Shield"],
            gold=50, skills=["Slash"], quest_flags={}, score=0,
        )
        self._world_seed = 42
        self._enemies_defeated = 0
        self._current_zone = "Starting Village"

    def save(self, label: str = "") -> GameMemento:
        """Create a deep-copy snapshot of current state."""
        state = {
            "player": copy.deepcopy(self._player.__dict__),
            "world_seed": self._world_seed,
            "enemies_defeated": self._enemies_defeated,
            "current_zone": self._current_zone,
        }
        return GameMemento(_state=state, _label=label)

    def restore(self, memento: GameMemento) -> None:
        """Restore state from a memento."""
        state = copy.deepcopy(memento._state)
        self._player = PlayerState(**state["player"])
        self._world_seed = state["world_seed"]
        self._enemies_defeated = state["enemies_defeated"]
        self._current_zone = state["current_zone"]
        print(f"  Restored to: {memento}")

    # Game actions that mutate state
    def level_up(self) -> None:
        self._player.level += 1
        self._player.max_hp += 20
        self._player.hp = self._player.max_hp
        self._player.skills.append(f"Skill_Lv{self._player.level}")
        print(f"  Level up! Now level {self._player.level}")

    def take_damage(self, amount: int) -> None:
        self._player.hp = max(0, self._player.hp - amount)
        print(f"  Took {amount} damage. HP: {self._player.hp}/{self._player.max_hp}")

    def move_to(self, zone: str, position: tuple) -> None:
        self._current_zone = zone
        self._player.position = position
        print(f"  Moved to {zone} at {position}")

    def collect_item(self, item: str, gold: int = 0) -> None:
        self._player.inventory.append(item)
        self._player.gold += gold
        print(f"  Collected '{item}' (+{gold} gold). Total gold: {self._player.gold}")

    def defeat_enemy(self, enemy: str, xp_gold: int = 10) -> None:
        self._enemies_defeated += 1
        self._player.gold += xp_gold
        self._player.score += xp_gold * 10
        print(f"  Defeated {enemy}! +{xp_gold} gold. Score: {self._player.score}")

    def complete_quest(self, quest_id: str) -> None:
        self._player.quest_flags[quest_id] = True
        print(f"  Quest '{quest_id}' completed!")

    def display(self) -> None:
        p = self._player
        print(f"\n  [{p.name}] Lv.{p.level} | HP:{p.hp}/{p.max_hp} | "
              f"Gold:{p.gold} | Score:{p.score}")
        print(f"  Zone: {self._current_zone} @ {p.position}")
        print(f"  Inventory: {p.inventory}")
        print(f"  Skills: {p.skills}")
        print(f"  Quests: {p.quest_flags}")
        print(f"  Enemies defeated: {self._enemies_defeated}")


# ---------------------------------------------------------------------------
# Caretaker — manages save slots, never inspects memento contents
# ---------------------------------------------------------------------------

class SaveManager:
    def __init__(self, max_slots: int = 10):
        self._slots: dict[str, GameMemento] = {}
        self._auto_saves: list[GameMemento] = []
        self._max_auto = 5
        self._max_slots = max_slots

    def save(self, game: GameWorld, slot: str, label: str = "") -> GameMemento:
        memento = game.save(label or slot)
        self._slots[slot] = memento
        print(f"  Saved to slot '{slot}': {memento}")
        return memento

    def auto_save(self, game: GameWorld) -> GameMemento:
        memento = game.save("autosave")
        self._auto_saves.append(memento)
        if len(self._auto_saves) > self._max_auto:
            self._auto_saves.pop(0)
        print(f"  Auto-saved: {memento}")
        return memento

    def load(self, game: GameWorld, slot: str) -> None:
        if slot not in self._slots:
            raise KeyError(f"No save in slot '{slot}'")
        game.restore(self._slots[slot])

    def load_auto(self, game: GameWorld, index: int = -1) -> None:
        if not self._auto_saves:
            raise RuntimeError("No auto-saves available")
        game.restore(self._auto_saves[index])

    def list_saves(self) -> None:
        print("\n  --- Save Slots ---")
        for slot, m in self._slots.items():
            print(f"  [{slot}] {m}")
        print(f"  Auto-saves: {self._auto_saves}")


# ---------------------------------------------------------------------------
# Demo
# ---------------------------------------------------------------------------

def main():
    print("=" * 55)
    print("  Memento Pattern — Game Save System Demo")
    print("=" * 55)

    game = GameWorld("Hero")
    saves = SaveManager()

    print("\n>>> Starting state")
    game.display()

    # Play through some content
    saves.save(game, "slot1", "Before dungeon")
    saves.auto_save(game)

    print("\n>>> Entering dungeon")
    game.move_to("Dark Dungeon", (100, 200))
    game.defeat_enemy("Goblin", 15)
    game.defeat_enemy("Orc", 25)
    game.collect_item("Magic Potion", 0)
    game.level_up()
    saves.auto_save(game)

    print("\n>>> Boss fight")
    game.take_damage(60)
    game.defeat_enemy("Dragon Boss", 100)
    game.collect_item("Dragon Scale Armor", 500)
    game.complete_quest("slay_dragon")
    saves.save(game, "slot2", "After dragon")
    game.display()

    # Oops — made a mistake, restore to before dungeon
    print("\n>>> Restoring to 'Before dungeon' save")
    saves.load(game, "slot1")
    game.display()

    # Restore to after dragon
    print("\n>>> Restoring to 'After dragon' save")
    saves.load(game, "slot2")
    game.display()

    # Auto-save restore
    print("\n>>> Restoring from latest auto-save")
    saves.load_auto(game, -1)
    game.display()

    saves.list_saves()


if __name__ == "__main__":
    main()
