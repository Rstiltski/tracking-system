"""
Brain Audio Module

Phase 7.3: Audio feedback system for gamification.
Provides sound effects for actions, achievements, and notifications.

Key Components:
- AudioManager: Core sound playback manager
- SoundEffect: Sound effect definitions
- AudioPreferences: User audio settings

Usage:
    from brain.audio import AudioManager, SoundEffect
    
    audio = AudioManager()
    audio.play(SoundEffect.HABIT_COMPLETE)
"""

from brain.audio.manager import AudioManager, get_audio_manager
from brain.audio.sounds import SoundEffect, SoundLibrary

__all__ = [
    "AudioManager",
    "get_audio_manager",
    "SoundEffect",
    "SoundLibrary",
]