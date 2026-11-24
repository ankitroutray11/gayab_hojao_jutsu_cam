"""
Gayab Hojao Jutsu Cam - Audio SFX Engine
Non-blocking asynchronous audio playback using pygame with winsound fallback.
"""

import os
import threading
from pathlib import Path

SOUNDS_DIR = Path(__file__).resolve().parent / "sounds"

# Pre-defined sound paths
SOUND_POOF = SOUNDS_DIR / "smoke_poof.wav"
SOUND_TELEPORT = SOUNDS_DIR / "teleport_ki.wav"
SOUND_DISSOLVE = SOUNDS_DIR / "particle_dissolve.wav"
SOUND_REAPPEAR = SOUNDS_DIR / "reappear.wav"

_PYGAME_AVAILABLE = False
try:
    import pygame
    pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
    _PYGAME_AVAILABLE = True
except Exception:
    _PYGAME_AVAILABLE = False

_CACHED_SOUNDS = {}

def _get_pygame_sound(path: Path):
    if not _PYGAME_AVAILABLE:
        return None
    key = str(path)
    if key not in _CACHED_SOUNDS:
        if path.exists():
            try:
                _CACHED_SOUNDS[key] = pygame.mixer.Sound(key)
            except Exception:
                _CACHED_SOUNDS[key] = None
        else:
            _CACHED_SOUNDS[key] = None
    return _CACHED_SOUNDS[key]

def play_sound_async(sound_type: str):
    """
    Plays an SFX asynchronously in the background.
    sound_type: 'poof', 'teleport', 'dissolve', 'reappear'
    """
    mapping = {
        "poof": SOUND_POOF,
        "teleport": SOUND_TELEPORT,
        "dissolve": SOUND_DISSOLVE,
        "reappear": SOUND_REAPPEAR
    }
    path = mapping.get(sound_type.lower())
    if not path or not path.exists():
        return

    def _play():
        if _PYGAME_AVAILABLE:
            snd = _get_pygame_sound(path)
            if snd:
                snd.play()
                return

        # Fallback to Windows native winsound
        try:
            import winsound
            winsound.PlaySound(str(path), winsound.SND_FILENAME | winsound.SND_ASYNC)
        except Exception:
            pass

    thread = threading.Thread(target=_play, daemon=True)
    thread.start()
