"""
Audio Manager

Phase 7.3: Core audio playback manager for the tracking system.
Manages sound playback, volume control, and audio preferences.

Usage:
    from brain.audio import AudioManager, SoundEffect
    
    audio = AudioManager()
    audio.play(SoundEffect.HABIT_COMPLETE)
    
    # With volume control
    audio.set_volume(0.5)  # 50% volume
    audio.mute()  # Mute all sounds
    audio.unmute()  # Unmute
"""

import logging
from dataclasses import dataclass, field
from typing import Optional, Dict, Any, Callable
from pathlib import Path

from brain.audio.sounds import SoundEffect, SoundDefinition, SoundLibrary

logger = logging.getLogger(__name__)


@dataclass
class AudioPreferences:
    """
    User audio preferences.
    
    Attributes:
        enabled: Whether audio is enabled globally
        volume: Master volume (0.0 to 1.0)
        habit_sounds: Whether habit sounds are enabled
        achievement_sounds: Whether achievement sounds are enabled
        task_sounds: Whether task sounds are enabled
        system_sounds: Whether system sounds are enabled
    """
    enabled: bool = True
    volume: float = 0.7  # 70% default volume
    habit_sounds: bool = True
    achievement_sounds: bool = True
    task_sounds: bool = True
    system_sounds: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "enabled": self.enabled,
            "volume": self.volume,
            "habit_sounds": self.habit_sounds,
            "achievement_sounds": self.achievement_sounds,
            "task_sounds": self.task_sounds,
            "system_sounds": self.system_sounds,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AudioPreferences":
        """Create from dictionary."""
        return cls(
            enabled=data.get("enabled", True),
            volume=data.get("volume", 0.7),
            habit_sounds=data.get("habit_sounds", True),
            achievement_sounds=data.get("achievement_sounds", True),
            task_sounds=data.get("task_sounds", True),
            system_sounds=data.get("system_sounds", True),
        )


class AudioManager:
    """
    Manages audio playback for the tracking system.
    
    Features:
    - Web Audio API synthesis (no external files needed)
    - Volume control (0-100%)
    - Mute toggle
    - Category-based sound filtering
    - Preference persistence
    
    Usage:
        audio = AudioManager()
        audio.play(SoundEffect.HABIT_COMPLETE)
    """
    
    def __init__(
        self,
        preferences: Optional[AudioPreferences] = None,
        storage: Optional[Any] = None,
    ):
        """
        Initialize the audio manager.
        
        Args:
            preferences: Audio preferences (uses defaults if not provided)
            storage: Storage backend for persisting preferences
        """
        self.preferences = preferences or AudioPreferences()
        self.storage = storage
        self._sound_queue: list = []
        self._last_played: Dict[str, float] = {}  # Track last played times
        
        # Load preferences from storage if available
        if storage and hasattr(storage, 'get_setting'):
            self._load_preferences()
    
    def _load_preferences(self) -> None:
        """Load audio preferences from storage."""
        try:
            if self.storage and hasattr(self.storage, 'get_setting'):
                prefs_data = self.storage.get_setting('audio_preferences', {})
                if prefs_data:
                    self.preferences = AudioPreferences.from_dict(prefs_data)
                    logger.debug("Loaded audio preferences from storage")
        except Exception as e:
            logger.warning("Failed to load audio preferences: %s", e)
    
    def _save_preferences(self) -> None:
        """Save audio preferences to storage."""
        try:
            if self.storage and hasattr(self.storage, 'set_setting'):
                self.storage.set_setting(
                    'audio_preferences', 
                    self.preferences.to_dict()
                )
                logger.debug("Saved audio preferences to storage")
        except Exception as e:
            logger.warning("Failed to save audio preferences: %s", e)
    
    def play(self, effect: SoundEffect, force: bool = False) -> bool:
        """
        Play a sound effect.
        
        Args:
            effect: The sound effect to play
            force: Play even if muted (for testing)
        
        Returns:
            True if sound was played, False if muted or unavailable
        """
        # Check if audio is enabled
        if not self.preferences.enabled and not force:
            logger.debug("Audio disabled, skipping: %s", effect.value)
            return False
        
        # Check category-specific settings
        sound = SoundLibrary.get(effect)
        if not sound:
            logger.warning("Sound effect not found: %s", effect.value)
            return False
        
        if not self._is_category_enabled(sound.category) and not force:
            logger.debug("Sound category disabled: %s", sound.category)
            return False
        
        # Queue the sound for playback
        self._sound_queue.append(effect)
        logger.debug("Queued sound: %s", effect.value)
        
        return True
    
    def _is_category_enabled(self, category: str) -> bool:
        """Check if a sound category is enabled."""
        category_map = {
            "habits": self.preferences.habit_sounds,
            "achievements": self.preferences.achievement_sounds,
            "tasks": self.preferences.task_sounds,
            "system": self.preferences.system_sounds,
        }
        return category_map.get(category, True)
    
    def get_sound_data(self, effect: SoundEffect) -> Optional[Dict[str, Any]]:
        """
        Get sound data for Web Audio API playback.
        
        This returns the sound parameters needed for browser-side
        synthesis using the Web Audio API.
        
        Args:
            effect: The sound effect
        
        Returns:
            Dictionary with sound parameters or None if not found
        """
        sound = SoundLibrary.get(effect)
        if not sound:
            return None
        
        return {
            **sound.to_dict(),
            "master_volume": self.preferences.volume,
        }
    
    def get_queued_sounds(self) -> list:
        """
        Get all queued sounds and clear the queue.
        
        Used by the UI to render JavaScript for sound playback.
        
        Returns:
            List of sound effect data dictionaries
        """
        sounds = []
        while self._sound_queue:
            effect = self._sound_queue.pop(0)
            data = self.get_sound_data(effect)
            if data:
                sounds.append(data)
        return sounds
    
    def set_volume(self, volume: float) -> None:
        """
        Set the master volume.
        
        Args:
            volume: Volume level (0.0 to 1.0)
        """
        self.preferences.volume = max(0.0, min(1.0, volume))
        self._save_preferences()
        logger.debug("Set volume to: %.2f", self.preferences.volume)
    
    def get_volume(self) -> float:
        """Get the current master volume."""
        return self.preferences.volume
    
    def mute(self) -> None:
        """Mute all sounds."""
        self.preferences.enabled = False
        self._save_preferences()
        logger.debug("Audio muted")
    
    def unmute(self) -> None:
        """Unmute all sounds."""
        self.preferences.enabled = True
        self._save_preferences()
        logger.debug("Audio unmuted")
    
    def toggle_mute(self) -> bool:
        """
        Toggle mute state.
        
        Returns:
            New mute state (True if muted, False if unmuted)
        """
        if self.preferences.enabled:
            self.mute()
        else:
            self.unmute()
        return not self.preferences.enabled
    
    def is_muted(self) -> bool:
        """Check if audio is muted."""
        return not self.preferences.enabled
    
    def set_category_enabled(
        self, 
        category: str, 
        enabled: bool
    ) -> None:
        """
        Enable or disable a sound category.
        
        Args:
            category: Category name (habits, achievements, tasks, system)
            enabled: Whether to enable the category
        """
        if category == "habits":
            self.preferences.habit_sounds = enabled
        elif category == "achievements":
            self.preferences.achievement_sounds = enabled
        elif category == "tasks":
            self.preferences.task_sounds = enabled
        elif category == "system":
            self.preferences.system_sounds = enabled
        
        self._save_preferences()
        logger.debug("Set category %s to: %s", category, enabled)
    
    def get_preferences(self) -> AudioPreferences:
        """Get current audio preferences."""
        return self.preferences
    
    def update_preferences(self, prefs: AudioPreferences) -> None:
        """
        Update audio preferences.
        
        Args:
            prefs: New preferences to apply
        """
        self.preferences = prefs
        self._save_preferences()
        logger.debug("Updated audio preferences")
    
    def test_sound(self, effect: SoundEffect = SoundEffect.SUCCESS) -> bool:
        """
        Test audio by playing a sound.
        
        Args:
            effect: Sound effect to play for testing
        
        Returns:
            True if sound was queued successfully
        """
        return self.play(effect, force=True)


# Singleton instance
_audio_manager: Optional[AudioManager] = None


def get_audio_manager(
    storage: Optional[Any] = None,
    preferences: Optional[AudioPreferences] = None,
) -> AudioManager:
    """
    Get the singleton AudioManager instance.
    
    Args:
        storage: Storage backend (only used on first call)
        preferences: Audio preferences (only used on first call)
    
    Returns:
        AudioManager instance
    """
    global _audio_manager
    
    if _audio_manager is None:
        _audio_manager = AudioManager(
            storage=storage,
            preferences=preferences,
        )
    
    return _audio_manager


def reset_audio_manager() -> None:
    """Reset the singleton instance (for testing)."""
    global _audio_manager
    _audio_manager = None


__all__ = [
    "AudioManager",
    "AudioPreferences",
    "get_audio_manager",
    "reset_audio_manager",
]