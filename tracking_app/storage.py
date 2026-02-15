"""
Storage Module - Data Persistence Layer

This module provides the Storage class that handles all CRUD operations
for the tracking system. Replaces js/storage.js with Python/SQLite.

Following PROJECT_RULES.md:
- All data goes through this Storage class
- Uses SQLite for persistence
- Provides type-safe operations
"""
from __future__ import annotations

import json
from datetime import datetime, date
from typing import Optional, List, Dict, Any
import logging

from tracking_app.database import Database, get_db, generate_id
from tracking_app.models import (
    Habit, HabitEntry, Task, Transaction, HealthEntry, Goal, Achievement
)

logger = logging.getLogger(__name__)


class Storage:
    """
    Storage manager for all tracking data.
    
    Provides CRUD operations for habits, tasks, transactions, etc.
    All data persistence goes through this class.
    
    Usage:
        storage = Storage()
        
        # Create a habit
        habit = storage.create_habit("Morning Exercise", icon="🏃")
        
        # Get all habits
        habits = storage.get_habits()
        
        # Mark habit complete
        storage.mark_habit_complete(habit.id, date.today())
    """
    
    def __init__(self, db: Optional[Database] = None):
        """
        Initialize storage with database.
        
        Args:
            db: Optional database instance (uses global if not provided)
        """
        self._db = db or get_db()
    
    # ==================== HABITS ====================
    
    def get_habits(self, include_archived: bool = False) -> List[Habit]:
        """
        Get all habits.
        
        Args:
            include_archived: Whether to include archived habits
            
        Returns:
            List of Habit objects
        """
        if include_archived:
            rows = self._db.fetch_all("SELECT * FROM habits ORDER BY created_at DESC")
        else:
            rows = self._db.fetch_all(
                "SELECT * FROM habits WHERE archived = 0 ORDER BY created_at DESC"
            )
        return [Habit.from_dict(row) for row in rows]
    
    def get_habit(self, habit_id: str) -> Optional[Habit]:
        """
        Get a single habit by ID.
        
        Args:
            habit_id: Habit ID
            
        Returns:
            Habit object or None if not found
        """
        row = self._db.fetch_one(
            "SELECT * FROM habits WHERE id = ?",
            (habit_id,)
        )
        return Habit.from_dict(row) if row else None
    
    def create_habit(
        self,
        name: str,
        description: str = "",
        frequency: str = "daily",
        icon: str = "🎯",
        color: str = "#6366f1",
        habit_type: str = "boolean",
        target_value: float = 0.0,
        target_type: str = "at_least"
    ) -> Habit:
        """
        Create a new habit.
        
        Args:
            name: Habit name
            description: Optional description
            frequency: Frequency type (daily, weekly, custom)
            icon: Emoji icon
            color: Hex color code
            habit_type: Boolean or numerical
            target_value: Target for numerical habits
            target_type: "at_least" or "at_most"
            
        Returns:
            Created Habit object
        """
        habit = Habit(
            name=name,
            description=description,
            frequency=frequency,
            icon=icon,
            color=color,
            habit_type=habit_type,
            target_value=target_value,
            target_type=target_type
        )
        
        self._db.execute(
            """INSERT INTO habits 
               (id, name, description, frequency, habit_type, color, icon, 
                target_value, target_type, archived, created_at, updated_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 0, ?, ?)""",
            (
                habit.id, habit.name, habit.description, habit.frequency,
                habit.habit_type, habit.color, habit.icon,
                habit.target_value, habit.target_type,
                habit.created_at.isoformat(), habit.updated_at.isoformat()
            )
        )
        
        logger.info(f"Created habit: {habit.name} ({habit.id})")
        return habit
    
    def update_habit(self, habit_id: str, **updates) -> Optional[Habit]:
        """
        Update a habit.
        
        Args:
            habit_id: Habit ID
            **updates: Fields to update
            
        Returns:
            Updated Habit object or None if not found
        """
        habit = self.get_habit(habit_id)
        if not habit:
            return None
        
        # Build update query
        valid_fields = {
            'name', 'description', 'frequency', 'frequency_data',
            'habit_type', 'color', 'icon', 'target_value', 'target_type', 'archived'
        }
        
        update_fields = []
        update_values = []
        
        for field, value in updates.items():
            if field in valid_fields:
                update_fields.append(f"{field} = ?")
                if field == 'frequency_data' and isinstance(value, tuple):
                    value = json.dumps(list(value))
                update_values.append(value)
        
        if not update_fields:
            return habit
        
        update_fields.append("updated_at = ?")
        update_values.append(datetime.now().isoformat())
        update_values.append(habit_id)
        
        self._db.execute(
            f"UPDATE habits SET {', '.join(update_fields)} WHERE id = ?",
            tuple(update_values)
        )
        
        return self.get_habit(habit_id)
    
    def delete_habit(self, habit_id: str) -> bool:
        """
        Delete a habit and all its entries.
        
        Args:
            habit_id: Habit ID
            
        Returns:
            True if deleted, False if not found
        """
        result = self._db.execute(
            "DELETE FROM habits WHERE id = ?",
            (habit_id,)
        )
        return result.rowcount > 0
    
    def archive_habit(self, habit_id: str) -> bool:
        """Archive a habit (soft delete)."""
        return self.update_habit(habit_id, archived=True) is not None
    
    def unarchive_habit(self, habit_id: str) -> bool:
        """Unarchive a habit."""
        return self.update_habit(habit_id, archived=False) is not None
    
    # ==================== HABIT ENTRIES ====================
    
    def get_habit_entries(
        self,
        habit_id: str,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> List[HabitEntry]:
        """
        Get entries for a habit.
        
        Args:
            habit_id: Habit ID
            start_date: Optional start date filter
            end_date: Optional end date filter
            
        Returns:
            List of HabitEntry objects
        """
        query = "SELECT * FROM habit_entries WHERE habit_id = ?"
        params = [habit_id]
        
        if start_date:
            query += " AND entry_date >= ?"
            params.append(start_date.isoformat())
        
        if end_date:
            query += " AND entry_date <= ?"
            params.append(end_date.isoformat())
        
        query += " ORDER BY entry_date DESC"
        
        rows = self._db.fetch_all(query, tuple(params))
        return [HabitEntry.from_dict(row) for row in rows]
    
    def get_habit_entry(self, habit_id: str, entry_date: date) -> Optional[HabitEntry]:
        """Get entry for a specific date."""
        row = self._db.fetch_one(
            "SELECT * FROM habit_entries WHERE habit_id = ? AND entry_date = ?",
            (habit_id, entry_date.isoformat())
        )
        return HabitEntry.from_dict(row) if row else None
    
    def mark_habit_complete(
        self,
        habit_id: str,
        entry_date: date,
        value: float = 1.0,
        notes: str = ""
    ) -> HabitEntry:
        """
        Mark a habit as complete for a date.
        
        Args:
            habit_id: Habit ID
            entry_date: Date of completion
            value: Value (1.0 for boolean, actual for numerical)
            notes: Optional notes
            
        Returns:
            Created or updated HabitEntry
        """
        entry_id = generate_id()
        
        self._db.execute(
            """INSERT OR REPLACE INTO habit_entries 
               (id, habit_id, entry_date, value, notes, skipped, created_at)
               VALUES (?, ?, ?, ?, ?, 0, ?)""",
            (
                entry_id, habit_id, entry_date.isoformat(),
                value, notes, datetime.now().isoformat()
            )
        )
        
        return self.get_habit_entry(habit_id, entry_date)
    
    def unmark_habit_complete(self, habit_id: str, entry_date: date) -> bool:
        """Remove completion for a date."""
        result = self._db.execute(
            "DELETE FROM habit_entries WHERE habit_id = ? AND entry_date = ?",
            (habit_id, entry_date.isoformat())
        )
        return result.rowcount > 0
    
    def skip_habit(self, habit_id: str, entry_date: date, reason: str = "") -> HabitEntry:
        """Mark a habit as skipped for a date."""
        entry_id = generate_id()
        
        self._db.execute(
            """INSERT OR REPLACE INTO habit_entries 
               (id, habit_id, entry_date, value, notes, skipped, created_at)
               VALUES (?, ?, ?, 0, ?, 1, ?)""",
            (
                entry_id, habit_id, entry_date.isoformat(),
                reason, datetime.now().isoformat()
            )
        )
        
        return self.get_habit_entry(habit_id, entry_date)
    
    # ==================== TASKS ====================
    
    def get_tasks(self, include_completed: bool = False) -> List[Task]:
        """Get all tasks."""
        if include_completed:
            rows = self._db.fetch_all(
                "SELECT * FROM tasks ORDER BY due_date IS NULL, due_date ASC"
            )
        else:
            rows = self._db.fetch_all(
                "SELECT * FROM tasks WHERE completed = 0 ORDER BY due_date IS NULL, due_date ASC"
            )
        return [Task.from_dict(row) for row in rows]
    
    def get_task(self, task_id: str) -> Optional[Task]:
        """Get a single task by ID."""
        row = self._db.fetch_one(
            "SELECT * FROM tasks WHERE id = ?",
            (task_id,)
        )
        return Task.from_dict(row) if row else None
    
    def create_task(
        self,
        title: str,
        description: str = "",
        priority: str = "medium",
        category: str = "",
        due_date: Optional[datetime] = None
    ) -> Task:
        """Create a new task."""
        task = Task(
            title=title,
            description=description,
            priority=priority,
            category=category,
            due_date=due_date
        )
        
        self._db.execute(
            """INSERT INTO tasks 
               (id, title, description, due_date, priority, category, completed, created_at, updated_at)
               VALUES (?, ?, ?, ?, ?, ?, 0, ?, ?)""",
            (
                task.id, task.title, task.description,
                task.due_date.isoformat() if task.due_date else None,
                task.priority, task.category,
                task.created_at.isoformat(), task.updated_at.isoformat()
            )
        )
        
        return task
    
    def update_task(self, task_id: str, **updates) -> Optional[Task]:
        """Update a task."""
        task = self.get_task(task_id)
        if not task:
            return None
        
        valid_fields = {'title', 'description', 'due_date', 'priority', 'category', 'completed'}
        
        update_fields = []
        update_values = []
        
        for field, value in updates.items():
            if field in valid_fields:
                update_fields.append(f"{field} = ?")
                if field == 'due_date' and isinstance(value, datetime):
                    value = value.isoformat()
                update_values.append(value)
        
        if not update_fields:
            return task
        
        update_fields.append("updated_at = ?")
        update_values.append(datetime.now().isoformat())
        update_values.append(task_id)
        
        self._db.execute(
            f"UPDATE tasks SET {', '.join(update_fields)} WHERE id = ?",
            tuple(update_values)
        )
        
        return self.get_task(task_id)
    
    def complete_task(self, task_id: str) -> Optional[Task]:
        """Mark a task as complete."""
        return self.update_task(
            task_id,
            completed=True,
            completed_at=datetime.now().isoformat()
        )
    
    def delete_task(self, task_id: str) -> bool:
        """Delete a task."""
        result = self._db.execute(
            "DELETE FROM tasks WHERE id = ?",
            (task_id,)
        )
        return result.rowcount > 0
    
    # ==================== TRANSACTIONS ====================
    
    def get_transactions(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> List[Transaction]:
        """Get all transactions."""
        query = "SELECT * FROM transactions"
        params = []
        
        conditions = []
        if start_date:
            conditions.append("trans_date >= ?")
            params.append(start_date.isoformat())
        if end_date:
            conditions.append("trans_date <= ?")
            params.append(end_date.isoformat())
        
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        
        query += " ORDER BY trans_date DESC"
        
        rows = self._db.fetch_all(query, tuple(params))
        return [Transaction.from_dict(row) for row in rows]
    
    def create_transaction(
        self,
        description: str,
        amount: float,
        trans_type: str,
        category: str = "",
        trans_date: Optional[date] = None
    ) -> Transaction:
        """Create a new transaction."""
        transaction = Transaction(
            description=description,
            amount=amount,
            type=trans_type,
            category=category,
            trans_date=trans_date
        )
        
        self._db.execute(
            """INSERT INTO transactions 
               (id, description, amount, type, category, trans_date, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (
                transaction.id, transaction.description, transaction.amount,
                transaction.type, transaction.category,
                transaction.trans_date.isoformat() if transaction.trans_date else None,
                transaction.created_at.isoformat()
            )
        )
        
        return transaction
    
    def delete_transaction(self, transaction_id: str) -> bool:
        """Delete a transaction."""
        result = self._db.execute(
            "DELETE FROM transactions WHERE id = ?",
            (transaction_id,)
        )
        return result.rowcount > 0
    
    # ==================== HEALTH ENTRIES ====================
    
    def get_health_entries(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> List[HealthEntry]:
        """Get health entries."""
        query = "SELECT * FROM health_entries"
        params = []
        
        conditions = []
        if start_date:
            conditions.append("entry_date >= ?")
            params.append(start_date.isoformat())
        if end_date:
            conditions.append("entry_date <= ?")
            params.append(end_date.isoformat())
        
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        
        query += " ORDER BY entry_date DESC"
        
        rows = self._db.fetch_all(query, tuple(params))
        return [HealthEntry.from_dict(row) for row in rows]
    
    def get_health_entry(self, entry_date: date) -> Optional[HealthEntry]:
        """Get health entry for a specific date."""
        row = self._db.fetch_one(
            "SELECT * FROM health_entries WHERE entry_date = ?",
            (entry_date.isoformat(),)
        )
        return HealthEntry.from_dict(row) if row else None
    
    def create_health_entry(
        self,
        entry_date: date,
        weight: Optional[float] = None,
        sleep_hours: Optional[float] = None,
        mood: str = "good",
        notes: str = ""
    ) -> HealthEntry:
        """Create or update a health entry."""
        entry = HealthEntry(
            entry_date=entry_date,
            weight=weight,
            sleep_hours=sleep_hours,
            mood=mood,
            notes=notes
        )
        
        self._db.execute(
            """INSERT OR REPLACE INTO health_entries 
               (id, entry_date, weight, sleep_hours, mood, notes, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (
                entry.id, entry.entry_date.isoformat(),
                entry.weight, entry.sleep_hours, entry.mood, entry.notes,
                entry.created_at.isoformat()
            )
        )
        
        return self.get_health_entry(entry_date)
    
    # ==================== GOALS ====================
    
    def get_goals(self, include_completed: bool = False) -> List[Goal]:
        """Get all goals."""
        if include_completed:
            rows = self._db.fetch_all(
                "SELECT * FROM goals ORDER BY deadline IS NULL, deadline ASC"
            )
        else:
            rows = self._db.fetch_all(
                "SELECT * FROM goals WHERE completed = 0 ORDER BY deadline IS NULL, deadline ASC"
            )
        return [Goal.from_dict(row) for row in rows]
    
    def get_goal(self, goal_id: str) -> Optional[Goal]:
        """Get a single goal by ID."""
        row = self._db.fetch_one(
            "SELECT * FROM goals WHERE id = ?",
            (goal_id,)
        )
        return Goal.from_dict(row) if row else None
    
    def create_goal(
        self,
        title: str,
        description: str = "",
        target: float = 0,
        unit: str = "",
        deadline: Optional[datetime] = None
    ) -> Goal:
        """Create a new goal."""
        goal = Goal(
            title=title,
            description=description,
            target=target,
            unit=unit,
            deadline=deadline
        )
        
        self._db.execute(
            """INSERT INTO goals 
               (id, title, description, target, current, unit, deadline, completed, created_at, updated_at)
               VALUES (?, ?, ?, ?, 0, ?, ?, 0, ?, ?)""",
            (
                goal.id, goal.title, goal.description, goal.target,
                goal.unit, goal.deadline.isoformat() if goal.deadline else None,
                goal.created_at.isoformat(), goal.updated_at.isoformat()
            )
        )
        
        return goal
    
    def update_goal_progress(self, goal_id: str, current: float) -> Optional[Goal]:
        """Update goal progress."""
        goal = self.get_goal(goal_id)
        if not goal:
            return None
        
        completed = current >= goal.target if goal.target > 0 else False
        
        self._db.execute(
            """UPDATE goals SET current = ?, completed = ?, updated_at = ? WHERE id = ?""",
            (current, completed, datetime.now().isoformat(), goal_id)
        )
        
        return self.get_goal(goal_id)
    
    def delete_goal(self, goal_id: str) -> bool:
        """Delete a goal."""
        result = self._db.execute(
            "DELETE FROM goals WHERE id = ?",
            (goal_id,)
        )
        return result.rowcount > 0
    
    # ==================== USER DATA ====================
    
    def get_user_data(self, key: str, default: Any = None) -> Any:
        """
        Get user data by key.
        
        Args:
            key: Data key
            default: Default value if not found
            
        Returns:
            Stored value or default
        """
        row = self._db.fetch_one(
            "SELECT value FROM user_inventory WHERE key = ?",
            (key,)
        )
        
        if row:
            value = row['value']
            # Try to parse as JSON
            try:
                return json.loads(value)
            except (json.JSONDecodeError, TypeError):
                return value
        
        return default
    
    def set_user_data(self, key: str, value: Any) -> None:
        """
        Set user data.
        
        Args:
            key: Data key
            value: Value to store (will be JSON-encoded if not a string)
        """
        if not isinstance(value, str):
            value = json.dumps(value)
        
        self._db.execute(
            """INSERT OR REPLACE INTO user_inventory (key, value, updated_at)
               VALUES (?, ?, ?)""",
            (key, value, datetime.now().isoformat())
        )
    
    def get_xp(self) -> int:
        """Get user's current XP."""
        return int(self.get_user_data('xp', 0))
    
    def add_xp(self, amount: int) -> int:
        """Add XP and return new total."""
        current = self.get_xp()
        new_total = current + amount
        self.set_user_data('xp', new_total)
        return new_total
    
    def get_level(self) -> int:
        """Get user's current level."""
        return int(self.get_user_data('level', 1))
    
    def get_streak_freezes(self) -> int:
        """Get number of streak freezes available."""
        return int(self.get_user_data('streak_freezes', 3))
    
    def use_streak_freeze(self) -> bool:
        """Use a streak freeze. Returns True if successful."""
        current = self.get_streak_freezes()
        if current <= 0:
            return False
        self.set_user_data('streak_freezes', current - 1)
        return True
    
    def add_streak_freeze(self, count: int = 1) -> int:
        """Add streak freezes. Returns new total."""
        current = self.get_streak_freezes()
        max_freezes = int(self.get_user_data('max_streak_freezes', 10))
        new_total = min(current + count, max_freezes)
        self.set_user_data('streak_freezes', new_total)
        return new_total
    
    # ==================== ACHIEVEMENTS ====================
    
    def get_achievements(self, unlocked_only: bool = False) -> List[Achievement]:
        """Get all achievements."""
        if unlocked_only:
            rows = self._db.fetch_all(
                "SELECT * FROM achievements WHERE unlocked_at IS NOT NULL"
            )
        else:
            rows = self._db.fetch_all("SELECT * FROM achievements")
        return [Achievement.from_dict(row) for row in rows]
    
    def unlock_achievement(self, achievement_id: str) -> Optional[Achievement]:
        """Unlock an achievement."""
        row = self._db.fetch_one(
            "SELECT * FROM achievements WHERE id = ?",
            (achievement_id,)
        )
        
        if not row:
            return None
        
        self._db.execute(
            "UPDATE achievements SET unlocked_at = ? WHERE id = ? AND unlocked_at IS NULL",
            (datetime.now().isoformat(), achievement_id)
        )
        
        return self._db.fetch_one(
            "SELECT * FROM achievements WHERE id = ?",
            (achievement_id,)
        )


# Global storage instance
_storage: Optional[Storage] = None


def get_storage() -> Storage:
    """Get the global storage instance."""
    global _storage
    if _storage is None:
        _storage = Storage()
    return _storage


# Export
__all__ = [
    "Storage",
    "get_storage",
]