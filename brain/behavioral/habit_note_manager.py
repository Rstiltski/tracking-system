"""
Habit Note Manager - Create and manage habit notes.

Usage:
    from brain.behavioral.habit_note_manager import HabitNoteManager
    
    manager = HabitNoteManager(storage, user_id)
    manager.create_note(habit_id, "Great session today!", mood=5)
"""
from datetime import date, timedelta, datetime
from typing import List, Dict, Any, Optional
import logging

from brain.models.habit_note import (
    HabitNote,
    NoteType,
    NoteStats,
    get_note_prompt,
)

logger = logging.getLogger(__name__)


class HabitNoteManager:
    """
    Manages habit notes and reflections.

    Usage:
        manager = HabitNoteManager(storage, user_id)
    """

    def __init__(self, storage: Any, user_id: str = ""):
        """
        Initialize note manager.

        Args:
            storage: Storage instance
            user_id: User ID
        """
        self.storage = storage
        self.user_id = user_id

    def create_note(
        self,
        habit_id: str,
        content: str,
        note_type: NoteType = NoteType.DAILY,
        mood: Optional[int] = None,
        energy: Optional[int] = None,
        tags: Optional[List[str]] = None,
        entry_date: Optional[date] = None
    ) -> HabitNote:
        """
        Create a habit note.

        Args:
            habit_id: Habit ID
            content: Note content
            note_type: Type of note
            mood: Mood rating (1-5)
            energy: Energy level (1-5)
            tags: Optional tags
            entry_date: Date note refers to

        Returns:
            Created HabitNote
        """
        note = HabitNote(
            habit_id=habit_id,
            user_id=self.user_id,
            note_type=note_type,
            content=content,
            mood=mood,
            energy=energy,
            tags=tags or [],
            entry_date=entry_date or date.today()
        )

        # Save note
        if hasattr(self.storage, 'save_habit_note'):
            self.storage.save_habit_note(habit_id, note.to_dict())

        logger.info(
            f"Created {note_type.value} note for habit {habit_id}"
        )

        return note

    def get_notes(
        self,
        habit_id: str,
        limit: int = 50,
        note_type: Optional[NoteType] = None
    ) -> List[HabitNote]:
        """
        Get notes for a habit.

        Args:
            habit_id: Habit ID
            limit: Maximum notes to return
            note_type: Optional type filter

        Returns:
            List of HabitNotes
        """
        if hasattr(self.storage, 'get_habit_notes'):
            notes_data = self.storage.get_habit_notes(
                habit_id,
                limit,
                note_type.value if note_type else None
            )
            return [HabitNote.from_dict(n) for n in notes_data]
        return []

    def get_note_stats(self, habit_id: str) -> NoteStats:
        """
        Get statistics about habit notes.

        Args:
            habit_id: Habit ID

        Returns:
            NoteStats object
        """
        notes = self.get_notes(habit_id, limit=1000)

        stats = NoteStats(total_notes=len(notes))

        if not notes:
            return stats

        # Count by type
        type_counts = {}
        for note in notes:
            type_key = note.note_type.value
            type_counts[type_key] = type_counts.get(type_key, 0) + 1
        stats.notes_by_type = type_counts

        # Average mood and energy
        moods = [n.mood for n in notes if n.mood]
        energies = [n.energy for n in notes if n.energy]

        if moods:
            stats.average_mood = sum(moods) / len(moods)
        if energies:
            stats.average_energy = sum(energies) / len(energies)

        # Most used tags
        tag_counts = {}
        for note in notes:
            for tag in note.tags:
                tag_counts[tag] = tag_counts.get(tag, 0) + 1

        sorted_tags = sorted(
            tag_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )
        stats.most_used_tags = [t[0] for t in sorted_tags[:5]]

        # Notes this week
        week_ago = date.today() - timedelta(days=7)
        stats.notes_this_week = sum(
            1 for n in notes
            if n.entry_date >= week_ago
        )

        return stats

    def search_notes(
        self,
        habit_id: str,
        query: str
    ) -> List[HabitNote]:
        """
        Search notes by content.

        Args:
            habit_id: Habit ID
            query: Search query

        Returns:
            List of matching notes
        """
        notes = self.get_notes(habit_id, limit=1000)
        query_lower = query.lower()

        return [
            n for n in notes
            if query_lower in n.content.lower()
            or any(query_lower in tag.lower() for tag in n.tags)
        ]

    def get_prompt(self, note_type: NoteType = NoteType.DAILY) -> str:
        """
        Get a writing prompt.

        Args:
            note_type: Type of note

        Returns:
            Prompt string
        """
        return get_note_prompt(note_type)

    def delete_note(self, note_id: str) -> bool:
        """
        Delete a note.

        Args:
            note_id: Note ID

        Returns:
            True if deleted
        """
        if hasattr(self.storage, 'delete_habit_note'):
            return self.storage.delete_habit_note(note_id)
        return False


__all__ = [
    "HabitNoteManager",
]
