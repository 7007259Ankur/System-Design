"""
Facade Design Pattern - Advanced Implementation
Real-world scenario: Smart Home Theater System
Multiple complex subsystems are coordinated through a single
clean facade interface. The client never touches subsystems directly.
"""

from __future__ import annotations
import logging
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Subsystem classes — complex, independent, unaware of the facade
# ---------------------------------------------------------------------------

class Amplifier:
    def __init__(self):
        self._on = False
        self._volume = 0
        self._input = None

    def power_on(self):
        self._on = True
        logger.info("Amplifier: powered ON")

    def power_off(self):
        self._on = False
        logger.info("Amplifier: powered OFF")

    def set_volume(self, level: int):
        if not self._on:
            raise RuntimeError("Amplifier is off")
        self._volume = max(0, min(100, level))
        logger.info(f"Amplifier: volume set to {self._volume}")

    def set_input(self, source: str):
        self._input = source
        logger.info(f"Amplifier: input switched to '{source}'")

    def set_surround_mode(self, mode: str):
        logger.info(f"Amplifier: surround mode → {mode}")

    @property
    def volume(self) -> int:
        return self._volume


class DVDPlayer:
    def __init__(self):
        self._on = False
        self._disc: Optional[str] = None

    def power_on(self):
        self._on = True
        logger.info("DVD Player: powered ON")

    def power_off(self):
        self._on = False
        logger.info("DVD Player: powered OFF")

    def load_disc(self, title: str):
        self._disc = title
        logger.info(f"DVD Player: disc loaded → '{title}'")

    def play(self):
        if not self._disc:
            raise RuntimeError("No disc loaded")
        logger.info(f"DVD Player: playing '{self._disc}'")

    def stop(self):
        logger.info("DVD Player: stopped")

    def eject(self):
        logger.info(f"DVD Player: ejecting '{self._disc}'")
        self._disc = None


class Projector:
    def __init__(self):
        self._on = False
        self._mode = "16:9"

    def power_on(self):
        self._on = True
        logger.info("Projector: powered ON — warming up...")
        time.sleep(0.05)  # simulate warm-up
        logger.info("Projector: ready")

    def power_off(self):
        self._on = False
        logger.info("Projector: powered OFF")

    def set_input(self, source: str):
        logger.info(f"Projector: input → {source}")

    def set_aspect_ratio(self, ratio: str):
        self._mode = ratio
        logger.info(f"Projector: aspect ratio → {ratio}")

    def set_brightness(self, level: int):
        logger.info(f"Projector: brightness → {level}%")


class StreamingService:
    def __init__(self):
        self._connected = False
        self._current: Optional[str] = None

    def connect(self):
        logger.info("Streaming: connecting to service...")
        time.sleep(0.02)
        self._connected = True
        logger.info("Streaming: connected")

    def disconnect(self):
        self._connected = False
        logger.info("Streaming: disconnected")

    def search(self, title: str) -> str:
        logger.info(f"Streaming: searching for '{title}'")
        return f"stream://{title.lower().replace(' ', '-')}"

    def play(self, url: str):
        if not self._connected:
            raise RuntimeError("Not connected to streaming service")
        self._current = url
        logger.info(f"Streaming: playing {url}")

    def stop(self):
        self._current = None
        logger.info("Streaming: playback stopped")


class Lights:
    def __init__(self):
        self._brightness = 100

    def dim(self, level: int):
        self._brightness = max(0, min(100, level))
        logger.info(f"Lights: dimmed to {self._brightness}%")

    def full_brightness(self):
        self._brightness = 100
        logger.info("Lights: full brightness")

    def off(self):
        self._brightness = 0
        logger.info("Lights: OFF")

    def set_color(self, color: str):
        logger.info(f"Lights: color → {color}")


class AirConditioner:
    def __init__(self):
        self._on = False
        self._temp = 22

    def power_on(self):
        self._on = True
        logger.info("AC: powered ON")

    def power_off(self):
        self._on = False
        logger.info("AC: powered OFF")

    def set_temperature(self, temp: int):
        self._temp = temp
        logger.info(f"AC: temperature set to {temp}°C")

    def set_mode(self, mode: str):
        logger.info(f"AC: mode → {mode}")


class SurroundSound:
    def __init__(self):
        self._on = False

    def power_on(self):
        self._on = True
        logger.info("Surround Sound: powered ON")

    def power_off(self):
        self._on = False
        logger.info("Surround Sound: powered OFF")

    def calibrate(self):
        logger.info("Surround Sound: auto-calibrating speakers...")
        time.sleep(0.02)
        logger.info("Surround Sound: calibration complete")

    def set_mode(self, mode: str):
        logger.info(f"Surround Sound: mode → {mode}")


# ---------------------------------------------------------------------------
# Scene presets
# ---------------------------------------------------------------------------

class Scene(Enum):
    MOVIE = "movie"
    STREAMING = "streaming"
    PARTY = "party"
    GAMING = "gaming"
    SLEEP = "sleep"


@dataclass
class TheaterState:
    active_scene: Optional[Scene] = None
    current_title: str = ""
    is_running: bool = False


# ---------------------------------------------------------------------------
# Facade — the single entry point that coordinates all subsystems
# ---------------------------------------------------------------------------

class HomeTheaterFacade:
    """
    Facade that wraps 7 subsystems behind simple, intent-driven methods.
    The client never needs to know about Amplifier, Projector, etc.
    """

    def __init__(self):
        # Subsystems — instantiated and owned by the facade
        self._amp = Amplifier()
        self._dvd = DVDPlayer()
        self._projector = Projector()
        self._streaming = StreamingService()
        self._lights = Lights()
        self._ac = AirConditioner()
        self._surround = SurroundSound()
        self._state = TheaterState()

    # --- Public facade methods (what the client actually calls) ---

    def watch_movie(self, title: str, volume: int = 60) -> None:
        """One call sets up the entire room for a DVD movie."""
        print(f"\n[Scene: MOVIE] Preparing to watch '{title}'...")
        self._lights.dim(10)
        self._ac.power_on()
        self._ac.set_temperature(20)
        self._ac.set_mode("cool")
        self._amp.power_on()
        self._amp.set_input("DVD")
        self._amp.set_surround_mode("Dolby Atmos")
        self._amp.set_volume(volume)
        self._surround.power_on()
        self._surround.calibrate()
        self._surround.set_mode("cinema")
        self._projector.power_on()
        self._projector.set_input("HDMI-1")
        self._projector.set_aspect_ratio("16:9")
        self._projector.set_brightness(80)
        self._dvd.power_on()
        self._dvd.load_disc(title)
        self._dvd.play()
        self._state = TheaterState(active_scene=Scene.MOVIE, current_title=title, is_running=True)
        print(f"[Scene: MOVIE] Enjoy '{title}'!\n")

    def end_movie(self) -> None:
        """Tears down the movie setup and restores the room."""
        print("\n[Scene: END] Shutting down theater...")
        self._dvd.stop()
        self._dvd.eject()
        self._dvd.power_off()
        self._projector.power_off()
        self._surround.power_off()
        self._amp.power_off()
        self._ac.power_off()
        self._lights.full_brightness()
        self._state = TheaterState()
        print("[Scene: END] Theater shut down. Lights on.\n")

    def watch_stream(self, title: str, volume: int = 55) -> None:
        """Sets up for streaming — no DVD player needed."""
        print(f"\n[Scene: STREAMING] Setting up stream for '{title}'...")
        self._lights.dim(15)
        self._ac.power_on()
        self._ac.set_temperature(21)
        self._amp.power_on()
        self._amp.set_input("HDMI-2")
        self._amp.set_surround_mode("DTS:X")
        self._amp.set_volume(volume)
        self._surround.power_on()
        self._surround.set_mode("cinema")
        self._projector.power_on()
        self._projector.set_input("HDMI-2")
        self._projector.set_aspect_ratio("21:9")
        self._projector.set_brightness(75)
        self._streaming.connect()
        url = self._streaming.search(title)
        self._streaming.play(url)
        self._state = TheaterState(active_scene=Scene.STREAMING, current_title=title, is_running=True)
        print(f"[Scene: STREAMING] Streaming '{title}'!\n")

    def party_mode(self) -> None:
        """Transforms the room into a party setup."""
        print("\n[Scene: PARTY] Activating party mode...")
        self._lights.set_color("RGB cycle")
        self._lights.dim(40)
        self._amp.power_on()
        self._amp.set_input("Bluetooth")
        self._amp.set_surround_mode("Stereo")
        self._amp.set_volume(85)
        self._surround.power_on()
        self._surround.set_mode("music")
        self._ac.power_on()
        self._ac.set_temperature(18)
        self._ac.set_mode("fan")
        self._state = TheaterState(active_scene=Scene.PARTY, is_running=True)
        print("[Scene: PARTY] Let's go!\n")

    def gaming_mode(self, volume: int = 70) -> None:
        """Low-latency setup optimized for gaming."""
        print("\n[Scene: GAMING] Switching to gaming mode...")
        self._lights.dim(30)
        self._lights.set_color("blue")
        self._amp.power_on()
        self._amp.set_input("HDMI-3")
        self._amp.set_surround_mode("Game")
        self._amp.set_volume(volume)
        self._projector.power_on()
        self._projector.set_input("HDMI-3")
        self._projector.set_aspect_ratio("16:9")
        self._projector.set_brightness(90)
        self._ac.power_on()
        self._ac.set_temperature(19)
        self._state = TheaterState(active_scene=Scene.GAMING, is_running=True)
        print("[Scene: GAMING] Game on!\n")

    def sleep_mode(self) -> None:
        """Gradually winds everything down."""
        print("\n[Scene: SLEEP] Winding down...")
        if self._state.is_running:
            self._streaming.stop() if self._state.active_scene == Scene.STREAMING else None
            self._dvd.stop() if self._state.active_scene == Scene.MOVIE else None
        self._amp.set_volume(10)
        time.sleep(0.02)
        self._amp.power_off()
        self._surround.power_off()
        self._projector.power_off()
        self._ac.set_temperature(23)
        self._ac.set_mode("sleep")
        self._lights.off()
        self._state = TheaterState(active_scene=Scene.SLEEP)
        print("[Scene: SLEEP] Good night.\n")

    def status(self) -> None:
        scene = self._state.active_scene.value if self._state.active_scene else "none"
        title = f" — '{self._state.current_title}'" if self._state.current_title else ""
        print(f"\n[Status] Scene: {scene}{title} | Running: {self._state.is_running}")


# ---------------------------------------------------------------------------
# Demo
# ---------------------------------------------------------------------------

def main():
    print("=" * 55)
    print("  Facade Pattern — Smart Home Theater Demo")
    print("=" * 55)

    theater = HomeTheaterFacade()

    # Client calls are dead simple — one method, everything coordinated
    theater.watch_movie("Inception", volume=65)
    theater.status()

    theater.end_movie()
    theater.status()

    theater.watch_stream("The Dark Knight", volume=60)
    theater.status()

    theater.sleep_mode()
    theater.status()

    theater.party_mode()
    theater.status()

    theater.gaming_mode(volume=75)
    theater.status()


if __name__ == "__main__":
    main()
