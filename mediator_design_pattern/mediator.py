"""
Mediator Design Pattern - Advanced Implementation
Real-world scenario: Air Traffic Control System
Aircraft communicate only through the ATC tower.
"""
from __future__ import annotations
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


# ---------------------------------------------------------------------------
# Domain models
# ---------------------------------------------------------------------------

class AircraftStatus(Enum):
    AIRBORNE   = "airborne"
    LANDING    = "landing"
    LANDED     = "landed"
    TAKEOFF    = "takeoff"
    HOLDING    = "holding"
    EMERGENCY  = "emergency"


@dataclass
class Runway:
    id: str
    length_m: int
    occupied_by: Optional[str] = None

    @property
    def is_free(self) -> bool:
        return self.occupied_by is None

    def occupy(self, callsign: str) -> None:
        self.occupied_by = callsign

    def clear(self) -> None:
        self.occupied_by = None


# ---------------------------------------------------------------------------
# Mediator Interface
# ---------------------------------------------------------------------------

class ATCMediator(ABC):
    @abstractmethod
    def request_landing(self, aircraft: "Aircraft") -> bool: ...

    @abstractmethod
    def request_takeoff(self, aircraft: "Aircraft") -> bool: ...

    @abstractmethod
    def report_emergency(self, aircraft: "Aircraft") -> None: ...

    @abstractmethod
    def notify_landed(self, aircraft: "Aircraft") -> None: ...

    @abstractmethod
    def broadcast(self, sender: "Aircraft", message: str) -> None: ...


# ---------------------------------------------------------------------------
# Colleague — Aircraft
# ---------------------------------------------------------------------------

class Aircraft:
    """
    Colleague. Communicates only through the mediator.
    Never talks to other aircraft directly.
    """

    def __init__(self, callsign: str, aircraft_type: str, mediator: ATCMediator):
        self.callsign = callsign
        self.aircraft_type = aircraft_type
        self.status = AircraftStatus.AIRBORNE
        self.altitude = 10000
        self.fuel_level = 100.0
        self._mediator = mediator

    def request_landing(self) -> None:
        print(f"  [{self.callsign}] Requesting landing clearance")
        granted = self._mediator.request_landing(self)
        if granted:
            self.status = AircraftStatus.LANDING
            print(f"  [{self.callsign}] Landing clearance granted — descending")
        else:
            self.status = AircraftStatus.HOLDING
            print(f"  [{self.callsign}] Holding pattern — runway busy")

    def request_takeoff(self) -> None:
        print(f"  [{self.callsign}] Requesting takeoff clearance")
        granted = self._mediator.request_takeoff(self)
        if granted:
            self.status = AircraftStatus.TAKEOFF
            print(f"  [{self.callsign}] Takeoff clearance granted")
        else:
            print(f"  [{self.callsign}] Takeoff denied — runway occupied")

    def declare_emergency(self) -> None:
        self.status = AircraftStatus.EMERGENCY
        print(f"  [{self.callsign}] MAYDAY MAYDAY MAYDAY — declaring emergency!")
        self._mediator.report_emergency(self)

    def complete_landing(self) -> None:
        self.status = AircraftStatus.LANDED
        self.altitude = 0
        print(f"  [{self.callsign}] Touchdown — runway vacated")
        self._mediator.notify_landed(self)

    def receive_message(self, sender: str, message: str) -> None:
        print(f"  [{self.callsign}] <- ATC/{sender}: {message}")

    def __repr__(self) -> str:
        return f"Aircraft({self.callsign}, {self.status.value})"


# ---------------------------------------------------------------------------
# Concrete Mediator — ATC Tower
# ---------------------------------------------------------------------------

class ATCTower(ATCMediator):
    def __init__(self, airport_name: str):
        self.airport_name = airport_name
        self._aircraft: dict[str, Aircraft] = {}
        self._runways: list[Runway] = [
            Runway("RWY-01L", 3500),
            Runway("RWY-01R", 3000),
        ]
        self._landing_queue: list[str] = []
        self._event_log: list[str] = []

    def register(self, aircraft: Aircraft) -> None:
        self._aircraft[aircraft.callsign] = aircraft
        self._log(f"Registered {aircraft.callsign} ({aircraft.aircraft_type})")

    def _free_runway(self) -> Optional[Runway]:
        return next((r for r in self._runways if r.is_free), None)

    def _log(self, message: str) -> None:
        entry = f"[ATC/{self.airport_name}] {message}"
        self._event_log.append(entry)
        print(f"  {entry}")

    def request_landing(self, aircraft: Aircraft) -> bool:
        runway = self._free_runway()
        if runway:
            runway.occupy(aircraft.callsign)
            self._log(f"Landing clearance -> {aircraft.callsign} on {runway.id}")
            self._broadcast_to_others(aircraft, f"Traffic: {aircraft.callsign} on final for {runway.id}")
            return True
        self._landing_queue.append(aircraft.callsign)
        self._log(f"No runway available — {aircraft.callsign} in holding queue (pos {len(self._landing_queue)})")
        return False

    def request_takeoff(self, aircraft: Aircraft) -> bool:
        runway = self._free_runway()
        if runway:
            runway.occupy(aircraft.callsign)
            self._log(f"Takeoff clearance -> {aircraft.callsign} on {runway.id}")
            return True
        self._log(f"Takeoff denied for {aircraft.callsign} — all runways occupied")
        return False

    def report_emergency(self, aircraft: Aircraft) -> None:
        self._log(f"EMERGENCY declared by {aircraft.callsign} — clearing all runways")
        for runway in self._runways:
            if runway.occupied_by and runway.occupied_by != aircraft.callsign:
                self._log(f"Instructing {runway.occupied_by} to abort and go around")
                if runway.occupied_by in self._aircraft:
                    self._aircraft[runway.occupied_by].receive_message("TOWER", "Abort landing — go around immediately")
            runway.clear()
        runway = self._runways[0]
        runway.occupy(aircraft.callsign)
        self._log(f"Emergency runway {runway.id} cleared for {aircraft.callsign}")
        self._broadcast_to_others(aircraft, f"Emergency traffic — {aircraft.callsign} on final")

    def notify_landed(self, aircraft: Aircraft) -> None:
        for runway in self._runways:
            if runway.occupied_by == aircraft.callsign:
                runway.clear()
                self._log(f"{runway.id} cleared after {aircraft.callsign} landed")
                break
        # Process holding queue
        if self._landing_queue:
            next_callsign = self._landing_queue.pop(0)
            if next_callsign in self._aircraft:
                self._log(f"Calling {next_callsign} from holding — runway available")
                self._aircraft[next_callsign].receive_message("TOWER", "Cleared to land — runway available")

    def broadcast(self, sender: Aircraft, message: str) -> None:
        self._broadcast_to_others(sender, message)

    def _broadcast_to_others(self, sender: Aircraft, message: str) -> None:
        for callsign, aircraft in self._aircraft.items():
            if callsign != sender.callsign:
                aircraft.receive_message(sender.callsign, message)

    def print_status(self) -> None:
        print(f"\n  --- {self.airport_name} Status ---")
        for r in self._runways:
            status = f"occupied by {r.occupied_by}" if r.occupied_by else "FREE"
            print(f"  {r.id}: {status}")
        print(f"  Holding queue: {self._landing_queue or 'empty'}")
        for cs, ac in self._aircraft.items():
            print(f"  {cs}: {ac.status.value}")


# ---------------------------------------------------------------------------
# Demo
# ---------------------------------------------------------------------------

def main():
    print("=" * 55)
    print("  Mediator Pattern — Air Traffic Control Demo")
    print("=" * 55)

    tower = ATCTower("HEATHROW")

    # Register aircraft
    ba101  = Aircraft("BA101",  "Boeing 747",  tower)
    ua202  = Aircraft("UA202",  "Airbus A320", tower)
    dl303  = Aircraft("DL303",  "Boeing 737",  tower)
    em404  = Aircraft("EM404",  "Cessna 172",  tower)

    for ac in [ba101, ua202, dl303, em404]:
        tower.register(ac)

    # Scenario 1: Normal landings
    print("\n>>> Scenario 1: Multiple landing requests")
    ba101.request_landing()   # gets RWY-01L
    ua202.request_landing()   # gets RWY-01R
    dl303.request_landing()   # goes to holding queue
    em404.request_landing()   # goes to holding queue

    tower.print_status()

    # BA101 lands — frees runway, DL303 gets called
    print("\n>>> BA101 completes landing")
    ba101.complete_landing()
    tower.print_status()

    # Scenario 2: Emergency
    print("\n>>> Scenario 2: Emergency declaration")
    em404.declare_emergency()
    tower.print_status()

    # Scenario 3: Takeoff
    print("\n>>> Scenario 3: Takeoff request")
    ba101.request_takeoff()


if __name__ == "__main__":
    main()
