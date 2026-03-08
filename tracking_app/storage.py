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
from brain.models.burnout import BurnoutRisk, BurnoutSnapshot
from brain.models.habit_difficulty import (
    DifficultyRatingEntry,
    DifficultyAdjustment,
)
from brain.models.relapse_plan import (
    RelapsePreventionPlan,
    PlanUsage,
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
        category: str = "general",
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
            category: Category for grouping (general, health, productivity, mindfulness, learning, social, finance, creativity)
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
            category=category,
            target_value=target_value,
            target_type=target_type
        )
        
        self._db.execute(
            """INSERT INTO habits 
               (id, name, description, frequency, habit_type, color, icon, category,
                target_value, target_type, archived, created_at, updated_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0, ?, ?)""",
            (
                habit.id, habit.name, habit.description, habit.frequency,
                habit.habit_type, habit.color, habit.icon, habit.category,
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
            'habit_type', 'color', 'icon', 'category', 'target_value', 'target_type', 'archived'
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
            "SELECT id, entry_date, weight, sleep_hours, mood, notes, created_at FROM health_entries WHERE entry_date = ?",
            (entry_date.isoformat(),)
        )
        if row:
            # Convert row to dict and handle date
            data = dict(row)
            if isinstance(data.get('entry_date'), str):
                data['entry_date'] = data['entry_date']
            return HealthEntry.from_dict(data)
        return None
    
    def create_health_entry(
        self,
        entry_date,
        weight: Optional[float] = None,
        sleep_hours: Optional[float] = None,
        mood: str = "good",
        notes: str = ""
    ) -> HealthEntry:
        """Create or update a health entry."""
        # Convert string to date if needed
        if isinstance(entry_date, str):
            entry_date = date.fromisoformat(entry_date)
        
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

    # ==================== BURNOUT RISK ====================

    def get_burnout_risk(self, habit_id: str) -> Optional[BurnoutRisk]:
        """
        Get the most recent burnout risk assessment for a habit.

        Args:
            habit_id: Habit ID

        Returns:
            BurnoutRisk object or None if not found
        """
        row = self._db.fetch_one(
            """SELECT * FROM burnout_risk_snapshots
               WHERE habit_id = ?
               ORDER BY assessment_date DESC, created_at DESC
               LIMIT 1""",
            (habit_id,)
        )

        if not row:
            return None

        return BurnoutRisk.from_dict(dict(row))

    def save_burnout_risk(self, habit_id: str, risk_data: Dict[str, Any]) -> None:
        """
        Save a burnout risk assessment.

        Args:
            habit_id: Habit ID
            risk_data: Dictionary with risk data
        """
        self._db.execute(
            """INSERT INTO burnout_risk_snapshots
               (id, habit_id, user_id, risk_score, risk_level, contributing_factors,
                assessment_date, trend, previous_score, intervention_suggested,
                intervention_type, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                risk_data.get("id", generate_id()),
                habit_id,
                risk_data.get("user_id", ""),
                risk_data.get("risk_score", 0.0),
                risk_data.get("risk_level", "low"),
                json.dumps(risk_data.get("contributing_factors", {})),
                risk_data.get("assessment_date", date.today().isoformat()),
                risk_data.get("trend", "stable"),
                risk_data.get("previous_score", 0.0),
                1 if risk_data.get("intervention_suggested", False) else 0,
                risk_data.get("intervention_type"),
                datetime.now().isoformat()
            )
        )

    def get_all_at_risk_habits(self, min_risk_level: str = "moderate") -> List[Dict[str, Any]]:
        """
        Get all habits with burnout risk at or above a threshold.

        Args:
            min_risk_level: Minimum risk level to include (moderate, high, critical)

        Returns:
            List of dicts with habit and risk information
        """
        # Get recent risk assessments (last 7 days)
        rows = self._db.fetch_all(
            """SELECT b.*, h.name as habit_name
               FROM burnout_risk_snapshots b
               JOIN habits h ON b.habit_id = h.id
               WHERE b.risk_level IN (?, ?, ?)
               AND b.assessment_date >= date('now', '-7 days')
               ORDER BY b.risk_score DESC""",
            ("moderate", "high", "critical")
        )

        results = []
        for row in rows:
            row_dict = dict(row)
            try:
                row_dict["contributing_factors"] = json.loads(
                    row_dict.get("contributing_factors", "{}")
                )
            except (json.JSONDecodeError, TypeError):
                row_dict["contributing_factors"] = {}
            results.append(row_dict)

        return results

    def get_burnout_history(self, habit_id: str, days: int = 30) -> List[BurnoutSnapshot]:
        """
        Get burnout risk history for a habit.

        Args:
            habit_id: Habit ID
            days: Number of days of history to retrieve

        Returns:
            List of BurnoutSnapshot objects
        """
        rows = self._db.fetch_all(
            """SELECT * FROM burnout_risk_snapshots
               WHERE habit_id = ?
               AND assessment_date >= date('now', ? days)
               ORDER BY assessment_date DESC""",
            (habit_id, -days)
        )

        return [BurnoutSnapshot.from_dict(dict(row)) for row in rows]

    # ==================== DIFFICULTY RATINGS ====================

    def get_difficulty_rating(self, habit_id: str) -> Optional[Dict[str, Any]]:
        """
        Get the most recent difficulty rating for a habit.

        Args:
            habit_id: Habit ID

        Returns:
            Dictionary with rating data or None
        """
        row = self._db.fetch_one(
            """SELECT * FROM difficulty_ratings
               WHERE habit_id = ?
               ORDER BY rated_at DESC
               LIMIT 1""",
            (habit_id,)
        )

        if not row:
            return None

        result = dict(row)
        try:
            result["adjustment_details"] = json.loads(
                result.get("adjustment_details", "{}")
            )
        except (json.JSONDecodeError, TypeError):
            result["adjustment_details"] = {}

        return result

    def save_difficulty_rating(
        self,
        habit_id: str,
        rating_data: Dict[str, Any]
    ) -> None:
        """
        Save a difficulty rating.

        Args:
            habit_id: Habit ID
            rating_data: Dictionary with rating data
        """
        self._db.execute(
            """INSERT INTO difficulty_ratings
               (id, habit_id, user_id, rating, notes, rated_at,
                adjustment_made, adjustment_type, adjustment_details, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                rating_data.get("id", generate_id()),
                habit_id,
                rating_data.get("user_id", ""),
                rating_data.get("rating", "just_right"),
                rating_data.get("notes", ""),
                rating_data.get("rated_at", datetime.now().isoformat()),
                1 if rating_data.get("adjustment_made", False) else 0,
                rating_data.get("adjustment_type"),
                json.dumps(rating_data.get("adjustment_details", {})),
                datetime.now().isoformat()
            )
        )

    def save_difficulty_adjustment(
        self,
        habit_id: str,
        adjustment_data: Dict[str, Any]
    ) -> None:
        """
        Save a difficulty adjustment.

        Args:
            habit_id: Habit ID
            adjustment_data: Dictionary with adjustment data
        """
        self._db.execute(
            """INSERT INTO difficulty_adjustments
               (id, habit_id, user_id, adjustment_type, old_value, new_value,
                reason, adjusted_at, effectiveness, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                adjustment_data.get("id", generate_id()),
                habit_id,
                adjustment_data.get("user_id", ""),
                adjustment_data.get("adjustment_type", "no_change"),
                json.dumps(adjustment_data.get("old_value")) if adjustment_data.get("old_value") is not None else None,
                json.dumps(adjustment_data.get("new_value")) if adjustment_data.get("new_value") is not None else None,
                adjustment_data.get("reason", ""),
                adjustment_data.get("adjusted_at", datetime.now().isoformat()),
                adjustment_data.get("effectiveness"),
                datetime.now().isoformat()
            )
        )

    def get_difficulty_adjustment_history(
        self,
        habit_id: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get difficulty adjustment history for a habit.

        Args:
            habit_id: Habit ID
            limit: Maximum number of records to return

        Returns:
            List of dictionaries with adjustment data
        """
        rows = self._db.fetch_all(
            """SELECT * FROM difficulty_adjustments
               WHERE habit_id = ?
               ORDER BY adjusted_at DESC
               LIMIT ?""",
            (habit_id, limit)
        )

        results = []
        for row in rows:
            result = dict(row)
            # Parse JSON fields
            for field in ["old_value", "new_value"]:
                if result.get(field):
                    try:
                        result[field] = json.loads(result[field])
                    except (json.JSONDecodeError, TypeError):
                        pass
            results.append(result)

        return results

    # ==================== RELAPSE PREVENTION PLANS ====================

    def save_relapse_plan(
        self,
        habit_id: str,
        plan_data: Dict[str, Any]
    ) -> None:
        """
        Save a relapse prevention plan.

        Args:
            habit_id: Habit ID
            plan_data: Dictionary with plan data
        """
        self._db.execute(
            """INSERT INTO relapse_prevention_plans
               (id, habit_id, user_id, category, trigger, if_condition,
                then_action, action_type, backup_plan, is_active,
                created_at, last_used, effectiveness, usage_count)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                plan_data.get("id", generate_id()),
                habit_id,
                plan_data.get("user_id", ""),
                plan_data.get("category", "custom"),
                plan_data.get("trigger", "custom"),
                plan_data.get("if_condition", ""),
                plan_data.get("then_action", ""),
                plan_data.get("action_type", "reduce"),
                plan_data.get("backup_plan", ""),
                1 if plan_data.get("is_active", True) else 0,
                plan_data.get("created_at", datetime.now().isoformat()),
                plan_data.get("last_used"),
                plan_data.get("effectiveness"),
                plan_data.get("usage_count", 0)
            )
        )

    def update_relapse_plan(
        self,
        plan_id: str,
        updates: Dict[str, Any]
    ) -> bool:
        """
        Update a relapse prevention plan.

        Args:
            plan_id: Plan ID
            updates: Dictionary of fields to update

        Returns:
            True if updated successfully
        """
        if not updates:
            return False

        # Build SET clause
        set_clauses = []
        values = []
        for key, value in updates.items():
            set_clauses.append(f"{key} = ?")
            values.append(value)

        values.append(plan_id)

        result = self._db.execute(
            f"""UPDATE relapse_prevention_plans
                SET {', '.join(set_clauses)}
                WHERE id = ?""",
            tuple(values)
        )

        return result.rowcount > 0

    def get_relapse_plans(
        self,
        habit_id: str,
        active_only: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Get relapse prevention plans for a habit.

        Args:
            habit_id: Habit ID
            active_only: Whether to return only active plans

        Returns:
            List of dictionaries with plan data
        """
        if active_only:
            rows = self._db.fetch_all(
                """SELECT * FROM relapse_prevention_plans
                   WHERE habit_id = ? AND is_active = 1
                   ORDER BY created_at DESC""",
                (habit_id,)
            )
        else:
            rows = self._db.fetch_all(
                """SELECT * FROM relapse_prevention_plans
                   WHERE habit_id = ?
                   ORDER BY created_at DESC""",
                (habit_id,)
            )

        return [dict(row) for row in rows]

    def delete_relapse_plan(self, plan_id: str) -> bool:
        """
        Delete a relapse prevention plan.

        Args:
            plan_id: Plan ID

        Returns:
            True if deleted successfully
        """
        result = self._db.execute(
            "DELETE FROM relapse_prevention_plans WHERE id = ?",
            (plan_id,)
        )
        return result.rowcount > 0

    def save_relapse_plan_usage(
        self,
        habit_id: str,
        usage_data: Dict[str, Any]
    ) -> None:
        """
        Save relapse plan usage record.

        Args:
            habit_id: Habit ID
            usage_data: Dictionary with usage data
        """
        self._db.execute(
            """INSERT INTO relapse_plan_usage
               (id, plan_id, habit_id, used_at, situation,
                action_taken, effectiveness, notes)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                usage_data.get("id", generate_id()),
                usage_data.get("plan_id", ""),
                habit_id,
                usage_data.get("used_at", datetime.now().isoformat()),
                usage_data.get("situation", ""),
                usage_data.get("action_taken", ""),
                usage_data.get("effectiveness"),
                usage_data.get("notes", "")
            )
        )

    def get_relapse_plan_usage(
        self,
        habit_id: str,
        plan_id: Optional[str] = None,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Get relapse plan usage records.

        Args:
            habit_id: Habit ID
            plan_id: Optional specific plan ID
            limit: Maximum number of records

        Returns:
            List of dictionaries with usage data
        """
        if plan_id:
            rows = self._db.fetch_all(
                """SELECT * FROM relapse_plan_usage
                   WHERE habit_id = ? AND plan_id = ?
                   ORDER BY used_at DESC
                   LIMIT ?""",
                (habit_id, plan_id, limit)
            )
        else:
            rows = self._db.fetch_all(
                """SELECT * FROM relapse_plan_usage
                   WHERE habit_id = ?
                   ORDER BY used_at DESC
                   LIMIT ?""",
                (habit_id, limit)
            )

        return [dict(row) for row in rows]

    # ==================== EVENT TRACKING ====================

    def log_habit_event(
        self,
        event_data: Dict[str, Any]
    ) -> None:
        """
        Log a habit event.

        Args:
            event_data: Event data dict
        """
        self._db.execute(
            """INSERT INTO habit_events
               (id, habit_id, user_id, event_type, event_data, timestamp)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (
                event_data.get("id", generate_id()),
                event_data.get("habit_id", ""),
                event_data.get("user_id", ""),
                event_data.get("event_type", ""),
                event_data.get("event_data", "{}"),
                event_data.get("timestamp", datetime.now().isoformat())
            )
        )

    def log_interaction(
        self,
        interaction_data: Dict[str, Any]
    ) -> None:
        """
        Log a user interaction.

        Args:
            interaction_data: Interaction data dict
        """
        self._db.execute(
            """INSERT INTO user_interactions
               (id, user_id, feature, action, metadata, timestamp)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (
                interaction_data.get("id", generate_id()),
                interaction_data.get("user_id", ""),
                interaction_data.get("feature", ""),
                interaction_data.get("action", ""),
                interaction_data.get("metadata", "{}"),
                interaction_data.get("timestamp", datetime.now().isoformat())
            )
        )

    def log_intervention(
        self,
        intervention_data: Dict[str, Any]
    ) -> None:
        """
        Log an intervention.

        Args:
            intervention_data: Intervention data dict
        """
        self._db.execute(
            """INSERT INTO intervention_log
               (id, habit_id, user_id, intervention_type, user_action, details, timestamp)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (
                intervention_data.get("id", generate_id()),
                intervention_data.get("habit_id"),
                intervention_data.get("user_id", ""),
                intervention_data.get("intervention_type", ""),
                intervention_data.get("user_action", ""),
                intervention_data.get("details", "{}"),
                intervention_data.get("timestamp", datetime.now().isoformat())
            )
        )

    def get_user_events(
        self,
        user_id: str,
        limit: int = 100,
        event_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get user's habit events.

        Args:
            user_id: User ID
            limit: Maximum events to return
            event_type: Optional type filter

        Returns:
            List of events
        """
        if event_type:
            rows = self._db.fetch_all(
                """SELECT * FROM habit_events
                   WHERE user_id = ? AND event_type = ?
                   ORDER BY timestamp DESC
                   LIMIT ?""",
                (user_id, event_type, limit)
            )
        else:
            rows = self._db.fetch_all(
                """SELECT * FROM habit_events
                   WHERE user_id = ?
                   ORDER BY timestamp DESC
                   LIMIT ?""",
                (user_id, limit)
            )

        return [dict(row) for row in rows]

    # ==================== HABIT STACKS ====================

    def create_habit_stack(
        self,
        user_id: str,
        name: str,
        trigger_description: str = "",
        anchor_category: str = "custom"
    ) -> str:
        """
        Create a new habit stack.

        Args:
            user_id: User ID
            name: Stack name
            trigger_description: Anchor trigger description
            anchor_category: Category of anchor

        Returns:
            Stack ID
        """
        stack_id = generate_id()
        self._db.execute(
            """INSERT INTO habit_stacks
               (id, user_id, name, trigger_description, anchor_category, created_at)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (stack_id, user_id, name, trigger_description, anchor_category, datetime.now().isoformat())
        )
        return stack_id

    def get_habit_stacks(self, user_id: str, active_only: bool = True) -> List[Dict[str, Any]]:
        """
        Get all habit stacks for a user.

        Args:
            user_id: User ID
            active_only: Whether to return only active stacks

        Returns:
            List of stack data
        """
        if active_only:
            rows = self._db.fetch_all(
                """SELECT * FROM habit_stacks
                   WHERE user_id = ? AND is_active = 1
                   ORDER BY created_at DESC""",
                (user_id,)
            )
        else:
            rows = self._db.fetch_all(
                """SELECT * FROM habit_stacks
                   WHERE user_id = ?
                   ORDER BY created_at DESC""",
                (user_id,)
            )

        stacks = []
        for row in rows:
            stack = dict(row)
            stack['items'] = self.get_stack_items(stack['id'])
            stacks.append(stack)

        return stacks

    def get_stack_items(self, stack_id: str) -> List[Dict[str, Any]]:
        """
        Get items in a stack.

        Args:
            stack_id: Stack ID

        Returns:
            List of stack items
        """
        rows = self._db.fetch_all(
            """SELECT * FROM stack_items
               WHERE stack_id = ?
               ORDER BY position_index""",
            (stack_id,)
        )
        return [dict(row) for row in rows]

    def add_item_to_stack(
        self,
        stack_id: str,
        habit_id: Optional[str],
        position: int,
        delay_seconds: int = 0,
        tiny_description: str = ""
    ) -> str:
        """
        Add an item to a stack.

        Args:
            stack_id: Stack ID
            habit_id: Optional habit ID
            position: Position in stack
            delay_seconds: Delay before this item
            tiny_description: Description for tiny habit

        Returns:
            Item ID
        """
        item_id = generate_id()
        self._db.execute(
            """INSERT INTO stack_items
               (id, stack_id, habit_id, position_index, delay_seconds, tiny_description)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (item_id, stack_id, habit_id, position, delay_seconds, tiny_description)
        )

        # Update positions of items after this one
        self._db.execute(
            """UPDATE stack_items
               SET position_index = position_index + 1
               WHERE stack_id = ? AND position_index >= ? AND id != ?""",
            (stack_id, position, item_id)
        )

        return item_id

    def remove_item_from_stack(self, stack_id: str, item_id: str) -> bool:
        """
        Remove an item from a stack.

        Args:
            stack_id: Stack ID
            item_id: Item ID

        Returns:
            True if removed
        """
        result = self._db.execute(
            "DELETE FROM stack_items WHERE stack_id = ? AND id = ?",
            (stack_id, item_id)
        )

        # Re-index positions
        rows = self._db.fetch_all(
            """SELECT id FROM stack_items
               WHERE stack_id = ?
               ORDER BY position_index""",
            (stack_id,)
        )
        for i, row in enumerate(rows):
            self._db.execute(
                "UPDATE stack_items SET position_index = ? WHERE id = ?",
                (i, row['id'])
            )

        return result.rowcount > 0

    def record_stack_completion(
        self,
        stack_id: str,
        completed_items: List[str],
        completion_order: List[str],
        conversion_rate: float
    ) -> str:
        """
        Record a stack completion.

        Args:
            stack_id: Stack ID
            completed_items: List of completed item IDs
            completion_order: Order of completion
            conversion_rate: Stack conversion rate

        Returns:
            Completion ID
        """
        completion_id = generate_id()
        today = date.today()

        self._db.execute(
            """INSERT INTO stack_completions
               (id, stack_id, completion_date, completed_items, completion_order, conversion_rate)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (completion_id, stack_id, today.isoformat(),
             json.dumps(completed_items), json.dumps(completion_order), conversion_rate)
        )

        return completion_id

    def get_stack_completion_stats(self, stack_id: str, days: int = 30) -> Dict[str, Any]:
        """
        Get stack completion statistics.

        Args:
            stack_id: Stack ID
            days: Number of days to analyze

        Returns:
            Statistics dict
        """
        rows = self._db.fetch_all(
            """SELECT * FROM stack_completions
               WHERE stack_id = ?
               AND completion_date >= date('now', ? days)
               ORDER BY completion_date DESC""",
            (stack_id, -days)
        )

        if not rows:
            return {"total_completions": 0, "average_conversion": 0.0}

        total = len(rows)
        avg_conversion = sum(dict(r)['conversion_rate'] for r in rows) / total

        return {
            "total_completions": total,
            "average_conversion": avg_conversion,
            "recent_completions": [dict(r) for r in rows[:10]]
        }

    # ==================== SRBAI SURVEY ====================

    def submit_srbai_survey(
        self,
        habit_id: str,
        user_id: str,
        q1: int,
        q2: int,
        q3: int,
        q4: int
    ) -> Dict[str, Any]:
        """
        Submit SRBAI survey responses.

        Args:
            habit_id: Habit ID
            user_id: User ID
            q1-q4: Responses (1-7 scale)

        Returns:
            Survey result dict
        """
        # Calculate automaticity score (average of 4 questions)
        automaticity_score = (q1 + q2 + q3 + q4) / 4.0
        
        # Determine if habit is formed (score >= 5.5)
        is_habit_formed = automaticity_score >= 5.5
        
        # Determine habit strength
        if automaticity_score >= 6.0:
            habit_strength = "strong"
        elif automaticity_score >= 5.0:
            habit_strength = "moderate"
        elif automaticity_score >= 4.0:
            habit_strength = "developing"
        elif automaticity_score >= 3.0:
            habit_strength = "weak"
        else:
            habit_strength = "not_a_habit"

        result_id = generate_id()
        survey_date = date.today()

        self._db.execute(
            """INSERT INTO srbai_results
               (id, habit_id, user_id, q1_automatic, q2_without_thinking,
                q3_start_unintentionally, q4_difficult_not_to_do,
                automaticity_score, is_habit_formed, habit_strength, survey_date)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (result_id, habit_id, user_id, q1, q2, q3, q4,
             automaticity_score, 1 if is_habit_formed else 0,
             habit_strength, survey_date.isoformat())
        )

        return {
            "id": result_id,
            "habit_id": habit_id,
            "automaticity_score": automaticity_score,
            "is_habit_formed": is_habit_formed,
            "habit_strength": habit_strength,
            "survey_date": survey_date.isoformat()
        }

    def get_latest_srbai_result(self, habit_id: str) -> Optional[Dict[str, Any]]:
        """
        Get latest SRBAI result for a habit.

        Args:
            habit_id: Habit ID

        Returns:
            Latest result dict or None
        """
        row = self._db.fetch_one(
            """SELECT * FROM srbai_results
               WHERE habit_id = ?
               ORDER BY survey_date DESC
               LIMIT 1""",
            (habit_id,)
        )

        if not row:
            return None

        result = dict(row)
        result['is_habit_formed'] = bool(result['is_habit_formed'])
        return result

    def should_show_srbai_survey(self, habit_id: str) -> bool:
        """
        Check if SRBAI survey should be shown.

        Survey is recommended after 14 days of streak.

        Args:
            habit_id: Habit ID

        Returns:
            True if survey should be shown
        """
        # Check if survey was already taken in last 30 days
        row = self._db.fetch_one(
            """SELECT COUNT(*) as count FROM srbai_results
               WHERE habit_id = ?
               AND survey_date >= date('now', '-30 days')""",
            (habit_id,)
        )

        if row and dict(row)['count'] > 0:
            return False

        # Check streak (should be 14+ days)
        # This is a simplified check - in production, calculate actual streak
        return True

    def get_srbai_history(self, habit_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get SRBAI survey history for a habit.

        Args:
            habit_id: Habit ID
            limit: Maximum results to return

        Returns:
            List of survey results
        """
        rows = self._db.fetch_all(
            """SELECT * FROM srbai_results
               WHERE habit_id = ?
               ORDER BY survey_date DESC
               LIMIT ?""",
            (habit_id, limit)
        )

        results = []
        for row in rows:
            result = dict(row)
            result['is_habit_formed'] = bool(result['is_habit_formed'])
            results.append(result)

        return results

    # ==================== ENVIRONMENT TIPS ====================

    def save_tip_interaction(
        self,
        interaction_data: Dict[str, Any]
    ) -> None:
        """
        Save tip interaction.

        Args:
            interaction_data: Interaction data dict
        """
        self._db.execute(
            """INSERT INTO user_tip_interactions
               (id, tip_id, user_id, habit_id, action, notes, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (
                interaction_data.get("id", generate_id()),
                interaction_data.get("tip_id", ""),
                interaction_data.get("user_id", ""),
                interaction_data.get("habit_id"),
                interaction_data.get("action", "viewed"),
                interaction_data.get("notes", ""),
                interaction_data.get("created_at", datetime.now().isoformat())
            )
        )

    def get_tip_interactions(
        self,
        user_id: str,
        habit_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get user's tip interactions.

        Args:
            user_id: User ID
            habit_id: Optional habit ID filter

        Returns:
            List of interactions
        """
        if habit_id:
            rows = self._db.fetch_all(
                """SELECT * FROM user_tip_interactions
                   WHERE user_id = ? AND habit_id = ?
                   ORDER BY created_at DESC""",
                (user_id, habit_id)
            )
        else:
            rows = self._db.fetch_all(
                """SELECT * FROM user_tip_interactions
                   WHERE user_id = ?
                   ORDER BY created_at DESC""",
                (user_id,)
            )

        return [dict(row) for row in rows]

    def get_tip_stats(self, user_id: str) -> Dict[str, Any]:
        """
        Get tip interaction statistics.

        Args:
            user_id: User ID

        Returns:
            Statistics dict
        """
        rows = self._db.fetch_all(
            """SELECT action, COUNT(*) as count
               FROM user_tip_interactions
               WHERE user_id = ?
               GROUP BY action""",
            (user_id,)
        )

        stats = {"viewed": 0, "tried": 0, "helpful": 0, "not_helpful": 0}
        for row in rows:
            action = dict(row)['action']
            count = dict(row)['count']
            if action in stats:
                stats[action] = count

        return stats

    # ==================== SMART SUGGESTIONS ====================

    def save_suggestion(
        self,
        suggestion_data: Dict[str, Any]
    ) -> str:
        """
        Save a suggestion.

        Args:
            suggestion_data: Suggestion data dict

        Returns:
            Suggestion ID
        """
        suggestion_id = suggestion_data.get("id", generate_id())
        self._db.execute(
            """INSERT INTO suggestions
               (id, habit_id, user_id, suggestion_type, priority,
                title, description, action, metadata, dismissed, acted_upon)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                suggestion_id,
                suggestion_data.get("habit_id"),
                suggestion_data.get("user_id", ""),
                suggestion_data.get("suggestion_type", "pattern"),
                suggestion_data.get("priority", "medium"),
                suggestion_data.get("title", ""),
                suggestion_data.get("description", ""),
                suggestion_data.get("action", ""),
                json.dumps(suggestion_data.get("metadata", {})),
                1 if suggestion_data.get("dismissed", False) else 0,
                1 if suggestion_data.get("acted_upon", False) else 0
            )
        )
        return suggestion_id

    def get_suggestions(
        self,
        user_id: str,
        limit: int = 5,
        active_only: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Get suggestions for user.

        Args:
            user_id: User ID
            limit: Maximum suggestions
            active_only: Only non-dismissed suggestions

        Returns:
            List of suggestions
        """
        if active_only:
            rows = self._db.fetch_all(
                """SELECT * FROM suggestions
                   WHERE user_id = ? AND dismissed = 0
                   ORDER BY 
                     CASE priority
                       WHEN 'high' THEN 1
                       WHEN 'medium' THEN 2
                       WHEN 'low' THEN 3
                     END,
                   created_at DESC
                   LIMIT ?""",
                (user_id, limit)
            )
        else:
            rows = self._db.fetch_all(
                """SELECT * FROM suggestions
                   WHERE user_id = ?
                   ORDER BY created_at DESC
                   LIMIT ?""",
                (user_id, limit)
            )

        results = []
        for row in rows:
            result = dict(row)
            result['dismissed'] = bool(result['dismissed'])
            result['acted_upon'] = bool(result['acted_upon'])
            try:
                result['metadata'] = json.loads(result['metadata'])
            except:
                result['metadata'] = {}
            results.append(result)

        return results

    def dismiss_suggestion(self, suggestion_id: str) -> bool:
        """
        Dismiss a suggestion.

        Args:
            suggestion_id: Suggestion ID

        Returns:
            True if dismissed
        """
        result = self._db.execute(
            "UPDATE suggestions SET dismissed = 1 WHERE id = ?",
            (suggestion_id,)
        )
        return result.rowcount > 0

    def record_suggestion_action(self, suggestion_id: str) -> bool:
        """
        Record that user acted on suggestion.

        Args:
            suggestion_id: Suggestion ID

        Returns:
            True if recorded
        """
        result = self._db.execute(
            "UPDATE suggestions SET acted_upon = 1 WHERE id = ?",
            (suggestion_id,)
        )
        return result.rowcount > 0

    def save_suggestion_feedback(
        self,
        feedback_data: Dict[str, Any]
    ) -> str:
        """
        Save suggestion feedback.

        Args:
            feedback_data: Feedback data dict

        Returns:
            Feedback ID
        """
        feedback_id = feedback_data.get("id", generate_id())
        self._db.execute(
            """INSERT INTO suggestion_feedback
               (id, suggestion_id, user_id, helpful, notes, created_at)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (
                feedback_id,
                feedback_data.get("suggestion_id", ""),
                feedback_data.get("user_id", ""),
                1 if feedback_data.get("helpful", False) else 0,
                feedback_data.get("notes", ""),
                feedback_data.get("created_at", datetime.now().isoformat())
            )
        )
        return feedback_id

    # ==================== TIMING OPTIMIZATION ====================

    def get_timing_analysis(self, habit_id: str) -> Dict[str, Any]:
        """
        Get timing analysis for a habit.

        Args:
            habit_id: Habit ID

        Returns:
            Timing analysis dict
        """
        from brain.analytics.timing_optimizer import TimingOptimizer
        
        optimizer = TimingOptimizer(self, habit_id)
        return optimizer.analyze_optimal_time()

    def save_timing_recommendation(
        self,
        habit_id: str,
        recommendation: str,
        day_of_week: Optional[int] = None
    ) -> None:
        """
        Save timing recommendation.

        Args:
            habit_id: Habit ID
            recommendation: Recommendation text
            day_of_week: Optional day of week (0-6)
        """
        # Store in user data for now
        key = f"timing_rec_{habit_id}"
        self.set_user_data(key, {
            "recommendation": recommendation,
            "day_of_week": day_of_week,
            "saved_at": datetime.now().isoformat()
        })

    # ==================== EXPERIMENTS ====================

    def save_experiment(
        self,
        experiment_data: Dict[str, Any]
    ) -> str:
        """
        Save experiment.

        Args:
            experiment_data: Experiment data dict

        Returns:
            Experiment ID
        """
        experiment_id = experiment_data.get("id", generate_id())
        self._db.execute(
            """INSERT INTO habit_experiments
               (id, habit_id, user_id, name, experiment_type, hypothesis,
                variant_a, variant_b, duration_days, status, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                experiment_id,
                experiment_data.get("habit_id", ""),
                experiment_data.get("user_id", ""),
                experiment_data.get("name", ""),
                experiment_data.get("experiment_type", "custom"),
                experiment_data.get("hypothesis", ""),
                json.dumps(experiment_data.get("variant_a", {})),
                json.dumps(experiment_data.get("variant_b", {})),
                experiment_data.get("duration_days", 7),
                experiment_data.get("status", "draft"),
                experiment_data.get("created_at", datetime.now().isoformat())
            )
        )
        return experiment_id

    def get_experiments(
        self,
        user_id: str,
        status: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get experiments for user.

        Args:
            user_id: User ID
            status: Optional status filter

        Returns:
            List of experiments
        """
        if status:
            rows = self._db.fetch_all(
                """SELECT * FROM habit_experiments
                   WHERE user_id = ? AND status = ?
                   ORDER BY created_at DESC""",
                (user_id, status)
            )
        else:
            rows = self._db.fetch_all(
                """SELECT * FROM habit_experiments
                   WHERE user_id = ?
                   ORDER BY created_at DESC""",
                (user_id,)
            )

        return [dict(row) for row in rows]

    def save_experiment_result(
        self,
        result_data: Dict[str, Any]
    ) -> str:
        """
        Save experiment result.

        Args:
            result_data: Result data dict

        Returns:
            Result ID
        """
        result_id = result_data.get("id", generate_id())
        self._db.execute(
            """INSERT INTO experiment_results
               (id, experiment_id, variant, date, completed, notes)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (
                result_id,
                result_data.get("experiment_id", ""),
                result_data.get("variant", "A"),
                result_data.get("date", date.today().isoformat()),
                1 if result_data.get("completed", False) else 0,
                result_data.get("notes", "")
            )
        )
        return result_id

    def get_experiment_results(
        self,
        experiment_id: str
    ) -> List[Dict[str, Any]]:
        """
        Get results for experiment.

        Args:
            experiment_id: Experiment ID

        Returns:
            List of results
        """
        rows = self._db.fetch_all(
            """SELECT * FROM experiment_results
               WHERE experiment_id = ?
               ORDER BY date""",
            (experiment_id,)
        )
        return [dict(row) for row in rows]

    def end_experiment(
        self,
        experiment_id: str,
        results: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        End an experiment.

        Args:
            experiment_id: Experiment ID
            results: Optional results data

        Returns:
            True if ended
        """
        result = self._db.execute(
            """UPDATE habit_experiments
               SET status = 'completed', end_date = ?, results = ?
               WHERE id = ?""",
            (
                date.today().isoformat(),
                json.dumps(results or {}),
                experiment_id
            )
        )
        return result.rowcount > 0

    # ==================== SOCIAL / FRIENDS ====================

    def save_friendship(
        self,
        friendship_data: Dict[str, Any]
    ) -> str:
        """Save friendship."""
        friendship_id = friendship_data.get("id", generate_id())
        self._db.execute(
            """INSERT INTO friendships
               (id, user_id, friend_id, status, created_at, updated_at)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (
                friendship_id,
                friendship_data.get("user_id", ""),
                friendship_data.get("friend_id", ""),
                friendship_data.get("status", "pending"),
                friendship_data.get("created_at", datetime.now().isoformat()),
                friendship_data.get("updated_at", datetime.now().isoformat())
            )
        )
        return friendship_id

    def get_friends(self, user_id: str) -> List[Dict[str, Any]]:
        """Get user's friends."""
        rows = self._db.fetch_all(
            """SELECT f.id, f.user_id, f.friend_id, f.status, f.created_at, f.updated_at,
                      f.friend_id as friend_name
               FROM friendships f
               WHERE f.user_id = ? AND f.status = 'accepted'
               ORDER BY f.created_at DESC""",
            (user_id,)
        )
        return [dict(row) for row in rows]

    def get_pending_friend_requests(self, user_id: str) -> List[Dict[str, Any]]:
        """Get pending friend requests."""
        rows = self._db.fetch_all(
            """SELECT f.id, f.user_id, f.friend_id, f.status, f.created_at, f.updated_at,
                      f.user_id as sender_name
               FROM friendships f
               WHERE f.friend_id = ? AND f.status = 'pending'
               ORDER BY f.created_at DESC""",
            (user_id,)
        )
        return [dict(row) for row in rows]

    def update_friendship_status(
        self,
        friendship_id: str,
        status: str
    ) -> bool:
        """Update friendship status."""
        result = self._db.execute(
            """UPDATE friendships
               SET status = ?, updated_at = ?
               WHERE id = ?""",
            (status, datetime.now().isoformat(), friendship_id)
        )
        return result.rowcount > 0

    def delete_friendship(self, friendship_id: str) -> bool:
        """Delete friendship."""
        result = self._db.execute(
            "DELETE FROM friendships WHERE id = ?",
            (friendship_id,)
        )
        return result.rowcount > 0

    def save_cheer(self, cheer_data: Dict[str, Any]) -> str:
        """Save cheer."""
        cheer_id = cheer_data.get("id", generate_id())
        self._db.execute(
            """INSERT INTO cheers
               (id, sender_id, receiver_id, habit_id, message, cheer_type, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (
                cheer_id,
                cheer_data.get("sender_id", ""),
                cheer_data.get("receiver_id", ""),
                cheer_data.get("habit_id"),
                cheer_data.get("message", ""),
                cheer_data.get("cheer_type", "general"),
                cheer_data.get("created_at", datetime.now().isoformat())
            )
        )
        return cheer_id

    def get_cheers(self, user_id: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Get cheers for user."""
        rows = self._db.fetch_all(
            """SELECT c.*, s.name as sender_name
               FROM cheers c
               LEFT JOIN users s ON c.sender_id = s.id
               WHERE c.receiver_id = ?
               ORDER BY c.created_at DESC
               LIMIT ?""",
            (user_id, limit)
        )
        return [dict(row) for row in rows]

    def save_activity_share(self, share_data: Dict[str, Any]) -> str:
        """Save activity share."""
        share_id = share_data.get("id", generate_id())
        self._db.execute(
            """INSERT INTO activity_shares
               (id, user_id, activity_type, habit_id, habit_name, details, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (
                share_id,
                share_data.get("user_id", ""),
                share_data.get("activity_type", ""),
                share_data.get("habit_id"),
                share_data.get("habit_name"),
                json.dumps(share_data.get("details", {})),
                share_data.get("created_at", datetime.now().isoformat())
            )
        )
        return share_id

    def get_friend_feed(self, user_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get activity feed from friends."""
        rows = self._db.fetch_all(
            """SELECT a.*, u.name as user_name
               FROM activity_shares a
               LEFT JOIN users u ON a.user_id = u.id
               WHERE a.user_id IN (
                   SELECT friend_id FROM friendships
                   WHERE user_id = ? AND status = 'accepted'
               )
               ORDER BY a.created_at DESC
               LIMIT ?""",
            (user_id, limit)
        )
        return [dict(row) for row in rows]

    def get_privacy_settings(self, user_id: str) -> Dict[str, Any]:
        """Get privacy settings for user."""
        row = self._db.fetch_one(
            "SELECT * FROM user_privacy_settings WHERE user_id = ?",
            (user_id,)
        )
        if row:
            return dict(row)
        # Return defaults
        return {
            "user_id": user_id,
            "share_achievements": 1,
            "share_streaks": 1,
            "share_completions": 0,
            "allow_cheers": 1,
            "visible_to": "friends"
        }

    def save_privacy_settings(
        self,
        user_id: str,
        settings_data: Dict[str, Any]
    ) -> bool:
        """Save privacy settings."""
        self._db.execute(
            """INSERT OR REPLACE INTO user_privacy_settings
               (user_id, share_achievements, share_streaks, share_completions,
                allow_cheers, visible_to, updated_at)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (
                user_id,
                1 if settings_data.get("share_achievements", True) else 0,
                1 if settings_data.get("share_streaks", True) else 0,
                1 if settings_data.get("share_completions", False) else 0,
                1 if settings_data.get("allow_cheers", True) else 0,
                settings_data.get("visible_to", "friends"),
                datetime.now().isoformat()
            )
        )
        return True

    # ==================== CHALLENGES ====================

    def save_challenge(self, challenge_data: Dict[str, Any]) -> str:
        """Save challenge."""
        challenge_id = challenge_data.get("id", generate_id())
        self._db.execute(
            """INSERT INTO group_challenges
               (id, name, challenge_type, description, status, start_date, end_date,
                creator_id, max_participants, is_public, goal_description, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                challenge_id,
                challenge_data.get("name", ""),
                challenge_data.get("challenge_type", ""),
                challenge_data.get("description", ""),
                challenge_data.get("status", "draft"),
                challenge_data.get("start_date", date.today().isoformat()),
                challenge_data.get("end_date", date.today().isoformat()),
                challenge_data.get("creator_id", ""),
                challenge_data.get("max_participants", 0),
                1 if challenge_data.get("is_public", True) else 0,
                challenge_data.get("goal_description", ""),
                challenge_data.get("created_at", datetime.now().isoformat())
            )
        )
        return challenge_id

    def get_challenges(
        self,
        user_id: str,
        status: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get challenges."""
        if status:
            rows = self._db.fetch_all(
                """SELECT * FROM group_challenges
                   WHERE status = ?
                   ORDER BY created_at DESC""",
                (status,)
            )
        else:
            rows = self._db.fetch_all(
                """SELECT * FROM group_challenges
                   WHERE is_public = 1 AND status = 'active'
                   ORDER BY created_at DESC"""
            )
        return [dict(row) for row in rows]

    def join_challenge(self, challenge_id: str, user_id: str) -> bool:
        """Join a challenge."""
        participant_id = generate_id()
        self._db.execute(
            """INSERT INTO challenge_participants
               (id, challenge_id, user_id, joined_at)
               VALUES (?, ?, ?, ?)""",
            (participant_id, challenge_id, user_id, datetime.now().isoformat())
        )
        return True

    def get_challenge_participants(
        self,
        challenge_id: str
    ) -> List[Dict[str, Any]]:
        """Get challenge participants."""
        rows = self._db.fetch_all(
            """SELECT p.*, u.name as user_name
               FROM challenge_participants p
               LEFT JOIN users u ON p.user_id = u.id
               WHERE p.challenge_id = ?
               ORDER BY p.progress DESC, p.streak DESC""",
            (challenge_id,)
        )
        return [dict(row) for row in rows]

    def save_challenge_checkin(self, checkin_data: Dict[str, Any]) -> str:
        """Save challenge check-in."""
        checkin_id = checkin_data.get("id", generate_id())
        self._db.execute(
            """INSERT INTO challenge_checkins
               (id, challenge_id, participant_id, user_id, check_in_date, completed, notes, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                checkin_id,
                checkin_data.get("challenge_id", ""),
                checkin_data.get("participant_id", ""),
                checkin_data.get("user_id", ""),
                checkin_data.get("check_in_date", date.today().isoformat()),
                1 if checkin_data.get("completed", False) else 0,
                checkin_data.get("notes", ""),
                checkin_data.get("created_at", datetime.now().isoformat())
            )
        )
        return checkin_id

    def get_challenge_checkins(
        self,
        challenge_id: str,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """Get challenge check-ins."""
        rows = self._db.fetch_all(
            """SELECT c.*, u.name as user_name
               FROM challenge_checkins c
               LEFT JOIN users u ON c.user_id = u.id
               WHERE c.challenge_id = ?
               ORDER BY c.check_in_date DESC
               LIMIT ?""",
            (challenge_id, limit)
        )
        return [dict(row) for row in rows]

    def earn_certificate(self, challenge_id: str, user_id: str) -> bool:
        """Earn completion certificate."""
        cert_id = generate_id()
        self._db.execute(
            """INSERT INTO challenge_certificates
               (id, challenge_id, user_id, earned_at)
               VALUES (?, ?, ?, ?)""",
            (cert_id, challenge_id, user_id, datetime.now().isoformat())
        )
        return True

    def get_certificates(self, user_id: str) -> List[Dict[str, Any]]:
        """Get user's certificates."""
        rows = self._db.fetch_all(
            """SELECT c.*, ch.name as challenge_name
               FROM challenge_certificates c
               LEFT JOIN group_challenges ch ON c.challenge_id = ch.id
               WHERE c.user_id = ?
               ORDER BY c.earned_at DESC""",
            (user_id,)
        )
        return [dict(row) for row in rows]


    # ==================== DIARY ENTRIES ====================

    def get_diary_entries(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        mood: Optional[str] = None,
        limit: int = 100
    ) -> List["DiaryEntry"]:
        """
        Get diary entries.

        Args:
            start_date: Optional start date filter
            end_date: Optional end date filter
            mood: Optional mood filter
            limit: Maximum number of entries to return

        Returns:
            List of DiaryEntry objects
        """
        from tracking_app.models import DiaryEntry

        query = "SELECT * FROM diary_entries"
        params = []
        conditions = []

        if start_date:
            conditions.append("entry_date >= ?")
            params.append(start_date.isoformat())
        if end_date:
            conditions.append("entry_date <= ?")
            params.append(end_date.isoformat())
        if mood:
            conditions.append("mood = ?")
            params.append(mood)

        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        query += " ORDER BY entry_date DESC LIMIT ?"
        params.append(limit)

        rows = self._db.fetch_all(query, tuple(params))
        return [DiaryEntry.from_dict(row) for row in rows]

    def get_diary_entry(self, entry_id: str) -> Optional["DiaryEntry"]:
        """Get a single diary entry by ID."""
        from tracking_app.models import DiaryEntry

        row = self._db.fetch_one(
            "SELECT * FROM diary_entries WHERE id = ?",
            (entry_id,)
        )
        return DiaryEntry.from_dict(row) if row else None

    def get_diary_entry_by_date(self, entry_date: date) -> Optional["DiaryEntry"]:
        """Get diary entry for a specific date."""
        from tracking_app.models import DiaryEntry

        row = self._db.fetch_one(
            "SELECT * FROM diary_entries WHERE entry_date = ?",
            (entry_date.isoformat(),)
        )
        return DiaryEntry.from_dict(row) if row else None

    def create_diary_entry(
        self,
        title: str,
        content: str,
        entry_date: Optional[date] = None,
        mood: str = "good",
        tags: Optional[List[str]] = None
    ) -> "DiaryEntry":
        """Create a new diary entry."""
        from tracking_app.models import DiaryEntry

        entry = DiaryEntry(
            title=title,
            content=content,
            entry_date=entry_date,
            mood=mood,
            tags=tags or []
        )

        self._db.execute(
            """INSERT INTO diary_entries
               (id, title, content, entry_date, mood, tags, is_private, created_at, updated_at)
               VALUES (?, ?, ?, ?, ?, ?, 1, ?, ?)""",
            (
                entry.id, entry.title, entry.content,
                entry.entry_date.isoformat() if entry.entry_date else date.today().isoformat(),
                entry.mood, json.dumps(entry.tags),
                entry.created_at.isoformat(), entry.updated_at.isoformat()
            )
        )

        return entry

    def update_diary_entry(self, entry_id: str, **updates) -> Optional["DiaryEntry"]:
        """Update a diary entry."""
        entry = self.get_diary_entry(entry_id)
        if not entry:
            return None

        valid_fields = {'title', 'content', 'entry_date', 'mood', 'tags'}
        update_fields = []
        update_values = []

        for field, value in updates.items():
            if field in valid_fields:
                update_fields.append(f"{field} = ?")
                if field == 'entry_date' and isinstance(value, date):
                    value = value.isoformat()
                elif field == 'tags' and isinstance(value, list):
                    value = json.dumps(value)
                update_values.append(value)

        if not update_fields:
            return entry

        update_fields.append("updated_at = ?")
        update_values.append(datetime.now().isoformat())
        update_values.append(entry_id)

        self._db.execute(
            f"UPDATE diary_entries SET {', '.join(update_fields)} WHERE id = ?",
            tuple(update_values)
        )

        return self.get_diary_entry(entry_id)

    def delete_diary_entry(self, entry_id: str) -> bool:
        """Delete a diary entry."""
        result = self._db.execute(
            "DELETE FROM diary_entries WHERE id = ?",
            (entry_id,)
        )
        return result.rowcount > 0

    def search_diary_entries(self, query: str, limit: int = 50) -> List["DiaryEntry"]:
        """Search diary entries by content or title."""
        from tracking_app.models import DiaryEntry

        search_term = f"%{query}%"
        rows = self._db.fetch_all(
            """SELECT * FROM diary_entries
               WHERE title LIKE ? OR content LIKE ?
               ORDER BY entry_date DESC
               LIMIT ?""",
            (search_term, search_term, limit)
        )
        return [DiaryEntry.from_dict(row) for row in rows]

    # ==================== JOURNAL ENTRIES ====================

    def get_journal_entries(
        self,
        category: Optional[str] = None,
        limit: int = 100
    ) -> List["JournalEntry"]:
        """
        Get journal entries.

        Args:
            category: Optional category filter
            limit: Maximum number of entries to return

        Returns:
            List of JournalEntry objects
        """
        from tracking_app.models import JournalEntry

        if category:
            rows = self._db.fetch_all(
                """SELECT * FROM journal_entries
                   WHERE category = ?
                   ORDER BY created_at DESC
                   LIMIT ?""",
                (category, limit)
            )
        else:
            rows = self._db.fetch_all(
                """SELECT * FROM journal_entries
                   ORDER BY created_at DESC
                   LIMIT ?""",
                (limit,)
            )

        return [JournalEntry.from_dict(row) for row in rows]

    def get_journal_entry(self, entry_id: str) -> Optional["JournalEntry"]:
        """Get a single journal entry by ID."""
        from tracking_app.models import JournalEntry

        row = self._db.fetch_one(
            "SELECT * FROM journal_entries WHERE id = ?",
            (entry_id,)
        )
        return JournalEntry.from_dict(row) if row else None

    def create_journal_entry(
        self,
        title: str,
        content: str,
        category: str = "free_write",
        tags: Optional[List[str]] = None
    ) -> "JournalEntry":
        """Create a new journal entry."""
        from tracking_app.models import JournalEntry

        entry = JournalEntry(
            title=title,
            content=content,
            category=category,
            tags=tags or []
        )

        self._db.execute(
            """INSERT INTO journal_entries
               (id, title, content, category, tags, is_private, created_at, updated_at)
               VALUES (?, ?, ?, ?, ?, 1, ?, ?)""",
            (
                entry.id, entry.title, entry.content, entry.category,
                json.dumps(entry.tags),
                entry.created_at.isoformat(), entry.updated_at.isoformat()
            )
        )

        return entry

    def update_journal_entry(self, entry_id: str, **updates) -> Optional["JournalEntry"]:
        """Update a journal entry."""
        entry = self.get_journal_entry(entry_id)
        if not entry:
            return None

        valid_fields = {'title', 'content', 'category', 'tags'}
        update_fields = []
        update_values = []

        for field, value in updates.items():
            if field in valid_fields:
                update_fields.append(f"{field} = ?")
                if field == 'tags' and isinstance(value, list):
                    value = json.dumps(value)
                update_values.append(value)

        if not update_fields:
            return entry

        update_fields.append("updated_at = ?")
        update_values.append(datetime.now().isoformat())
        update_values.append(entry_id)

        self._db.execute(
            f"UPDATE journal_entries SET {', '.join(update_fields)} WHERE id = ?",
            tuple(update_values)
        )

        return self.get_journal_entry(entry_id)

    def delete_journal_entry(self, entry_id: str) -> bool:
        """Delete a journal entry."""
        result = self._db.execute(
            "DELETE FROM journal_entries WHERE id = ?",
            (entry_id,)
        )
        return result.rowcount > 0

    def search_journal_entries(self, query: str, limit: int = 50) -> List["JournalEntry"]:
        """Search journal entries by content or title."""
        from tracking_app.models import JournalEntry

        search_term = f"%{query}%"
        rows = self._db.fetch_all(
            """SELECT * FROM journal_entries
               WHERE title LIKE ? OR content LIKE ?
               ORDER BY created_at DESC
               LIMIT ?""",
            (search_term, search_term, limit)
        )
        return [JournalEntry.from_dict(row) for row in rows]

    # ==================== PRIVATE TODOS ====================

    def get_private_todos(self, include_completed: bool = False) -> List["PrivateTodo"]:
        """
        Get private todos.

        Args:
            include_completed: Whether to include completed todos

        Returns:
            List of PrivateTodo objects
        """
        from tracking_app.models import PrivateTodo

        if include_completed:
            rows = self._db.fetch_all(
                """SELECT * FROM private_todos
                   ORDER BY due_date IS NULL, due_date ASC, priority DESC"""
            )
        else:
            rows = self._db.fetch_all(
                """SELECT * FROM private_todos
                   WHERE completed = 0
                   ORDER BY due_date IS NULL, due_date ASC, priority DESC"""
            )

        return [PrivateTodo.from_dict(row) for row in rows]

    def get_private_todo(self, todo_id: str) -> Optional["PrivateTodo"]:
        """Get a single private todo by ID."""
        from tracking_app.models import PrivateTodo

        row = self._db.fetch_one(
            "SELECT * FROM private_todos WHERE id = ?",
            (todo_id,)
        )
        return PrivateTodo.from_dict(row) if row else None

    def create_private_todo(
        self,
        title: str,
        description: str = "",
        priority: str = "medium",
        category: str = "",
        due_date: Optional[datetime] = None
    ) -> "PrivateTodo":
        """Create a new private todo."""
        from tracking_app.models import PrivateTodo

        todo = PrivateTodo(
            title=title,
            description=description,
            priority=priority,
            category=category,
            due_date=due_date
        )

        self._db.execute(
            """INSERT INTO private_todos
               (id, title, description, priority, due_date, completed, category, is_private, created_at, updated_at)
               VALUES (?, ?, ?, ?, ?, 0, ?, 1, ?, ?)""",
            (
                todo.id, todo.title, todo.description, todo.priority,
                todo.due_date.isoformat() if todo.due_date else None,
                todo.category,
                todo.created_at.isoformat(), todo.updated_at.isoformat()
            )
        )

        return todo

    def update_private_todo(self, todo_id: str, **updates) -> Optional["PrivateTodo"]:
        """Update a private todo."""
        todo = self.get_private_todo(todo_id)
        if not todo:
            return None

        valid_fields = {'title', 'description', 'priority', 'due_date', 'completed', 'category'}
        update_fields = []
        update_values = []

        for field, value in updates.items():
            if field in valid_fields:
                update_fields.append(f"{field} = ?")
                if field == 'due_date' and isinstance(value, datetime):
                    value = value.isoformat()
                elif field == 'completed':
                    value = 1 if value else 0
                update_values.append(value)

        if not update_fields:
            return todo

        update_fields.append("updated_at = ?")
        update_values.append(datetime.now().isoformat())
        update_values.append(todo_id)

        self._db.execute(
            f"UPDATE private_todos SET {', '.join(update_fields)} WHERE id = ?",
            tuple(update_values)
        )

        return self.get_private_todo(todo_id)

    def complete_private_todo(self, todo_id: str) -> Optional["PrivateTodo"]:
        """Mark a private todo as complete."""
        return self.update_private_todo(todo_id, completed=True)

    def delete_private_todo(self, todo_id: str) -> bool:
        """Delete a private todo."""
        result = self._db.execute(
            "DELETE FROM private_todos WHERE id = ?",
            (todo_id,)
        )
        return result.rowcount > 0


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
