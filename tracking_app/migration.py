"""
Migration Utility - Migrate from LocalStorage/JSON to SQLite

This module provides utilities to migrate existing data from the
legacy JavaScript LocalStorage format to the new Python SQLite database.

Usage:
    from tracking_app.migration import migrate_from_json
    
    # Migrate from exported JSON file
    migrate_from_json("exported_data.json")
"""
from __future__ import annotations

import json
from datetime import datetime, date
from pathlib import Path
from typing import Dict, Any, List, Optional
import logging

from tracking_app.database import Database, get_db, init_db, generate_id
from tracking_app.models import (
    Habit, HabitEntry, Task, Transaction, HealthEntry, Goal, Achievement
)
from tracking_app.storage import Storage, get_storage

logger = logging.getLogger(__name__)


class MigrationResult:
    """Result of a migration operation."""
    
    def __init__(self):
        self.habits_migrated: int = 0
        self.entries_migrated: int = 0
        self.tasks_migrated: int = 0
        self.transactions_migrated: int = 0
        self.health_entries_migrated: int = 0
        self.goals_migrated: int = 0
        self.achievements_migrated: int = 0
        self.errors: List[str] = []
    
    @property
    def total_migrated(self) -> int:
        """Total items migrated."""
        return (
            self.habits_migrated + self.entries_migrated +
            self.tasks_migrated + self.transactions_migrated +
            self.health_entries_migrated + self.goals_migrated +
            self.achievements_migrated
        )
    
    @property
    def success(self) -> bool:
        """Whether migration was successful (no errors)."""
        return len(self.errors) == 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "success": self.success,
            "total_migrated": self.total_migrated,
            "habits_migrated": self.habits_migrated,
            "entries_migrated": self.entries_migrated,
            "tasks_migrated": self.tasks_migrated,
            "transactions_migrated": self.transactions_migrated,
            "health_entries_migrated": self.health_entries_migrated,
            "goals_migrated": self.goals_migrated,
            "achievements_migrated": self.achievements_migrated,
            "errors": self.errors
        }


def migrate_from_json(
    json_path: str,
    db: Optional[Database] = None
) -> MigrationResult:
    """
    Migrate data from a JSON export file to SQLite.
    
    Args:
        json_path: Path to the JSON export file
        db: Optional database instance
        
    Returns:
        MigrationResult with migration statistics
    """
    result = MigrationResult()
    
    # Load JSON data
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        result.errors.append(f"File not found: {json_path}")
        return result
    except json.JSONDecodeError as e:
        result.errors.append(f"Invalid JSON: {e}")
        return result
    
    # Initialize database
    database = db or get_db()
    init_db()
    storage = Storage(database)
    
    # Migrate habits
    if 'habits' in data:
        result.habits_migrated = _migrate_habits(data['habits'], storage, result)
    
    # Migrate habit entries/completions
    if 'habitEntries' in data or 'habitCompletions' in data:
        entries_data = data.get('habitEntries', data.get('habitCompletions', {}))
        result.entries_migrated = _migrate_habit_entries(entries_data, storage, result)
    
    # Migrate tasks
    if 'tasks' in data:
        result.tasks_migrated = _migrate_tasks(data['tasks'], storage, result)
    
    # Migrate transactions
    if 'transactions' in data:
        result.transactions_migrated = _migrate_transactions(data['transactions'], storage, result)
    
    # Migrate health entries
    if 'healthEntries' in data:
        result.health_entries_migrated = _migrate_health_entries(data['healthEntries'], storage, result)
    
    # Migrate goals
    if 'goals' in data:
        result.goals_migrated = _migrate_goals(data['goals'], storage, result)
    
    # Migrate achievements
    if 'achievements' in data:
        result.achievements_migrated = _migrate_achievements(data['achievements'], storage, result)
    
    # Migrate user data (XP, level, etc.)
    if 'userData' in data:
        _migrate_user_data(data['userData'], storage)
    
    logger.info(f"Migration complete: {result.total_migrated} items migrated")
    return result


def _migrate_habits(
    habits_data: List[Dict],
    storage: Storage,
    result: MigrationResult
) -> int:
    """Migrate habits."""
    count = 0
    
    for habit_data in habits_data:
        try:
            # Handle different field names from JS version
            habit = Habit(
                id=habit_data.get('id', generate_id()),
                name=habit_data.get('name', 'Unnamed Habit'),
                description=habit_data.get('description', ''),
                frequency=habit_data.get('frequency', 'daily'),
                icon=habit_data.get('icon', '🎯'),
                color=habit_data.get('color', '#6366f1'),
                habit_type=habit_data.get('type', 'boolean'),
                target_value=habit_data.get('targetValue', 0),
                target_type=habit_data.get('targetType', 'at_least'),
                archived=habit_data.get('archived', False)
            )
            
            # Check if habit already exists
            existing = storage.get_habit(habit.id)
            if existing:
                logger.debug(f"Habit {habit.id} already exists, skipping")
                continue
            
            # Insert habit
            storage._db.execute(
                """INSERT INTO habits 
                   (id, name, description, frequency, habit_type, color, icon, 
                    target_value, target_type, archived, created_at, updated_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    habit.id, habit.name, habit.description, habit.frequency,
                    habit.habit_type, habit.color, habit.icon,
                    habit.target_value, habit.target_type, habit.archived,
                    habit.created_at.isoformat(), habit.updated_at.isoformat()
                )
            )
            count += 1
            
        except Exception as e:
            result.errors.append(f"Failed to migrate habit: {e}")
    
    return count


def _migrate_habit_entries(
    entries_data: Dict[str, List],
    storage: Storage,
    result: MigrationResult
) -> int:
    """
    Migrate habit entries.
    
    Expected format:
    {
        "habit_id_1": ["2026-01-01", "2026-01-02", ...],
        "habit_id_2": [...]
    }
    """
    count = 0
    
    for habit_id, dates in entries_data.items():
        for date_str in dates:
            try:
                entry_date = date.fromisoformat(date_str) if isinstance(date_str, str) else date_str
                
                # Check if entry already exists
                existing = storage.get_habit_entry(habit_id, entry_date)
                if existing:
                    continue
                
                # Create entry
                storage._db.execute(
                    """INSERT OR IGNORE INTO habit_entries 
                       (id, habit_id, entry_date, value, notes, skipped, created_at)
                       VALUES (?, ?, ?, 1.0, '', 0, ?)""",
                    (generate_id(), habit_id, entry_date.isoformat(), datetime.now().isoformat())
                )
                count += 1
                
            except Exception as e:
                result.errors.append(f"Failed to migrate entry for {habit_id} on {date_str}: {e}")
    
    return count


def _migrate_tasks(
    tasks_data: List[Dict],
    storage: Storage,
    result: MigrationResult
) -> int:
    """Migrate tasks."""
    count = 0
    
    for task_data in tasks_data:
        try:
            due_date = task_data.get('dueDate') or task_data.get('due_date')
            if isinstance(due_date, str):
                due_date = datetime.fromisoformat(due_date)
            
            task = Task(
                id=task_data.get('id', generate_id()),
                title=task_data.get('title', 'Untitled Task'),
                description=task_data.get('description', ''),
                due_date=due_date,
                priority=task_data.get('priority', 'medium'),
                category=task_data.get('category', ''),
                completed=task_data.get('completed', False)
            )
            
            # Check if task already exists
            existing = storage.get_task(task.id)
            if existing:
                continue
            
            storage._db.execute(
                """INSERT INTO tasks 
                   (id, title, description, due_date, priority, category, 
                    completed, completed_at, created_at, updated_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    task.id, task.title, task.description,
                    task.due_date.isoformat() if task.due_date else None,
                    task.priority, task.category, task.completed,
                    task.completed_at.isoformat() if task.completed_at else None,
                    task.created_at.isoformat(), task.updated_at.isoformat()
                )
            )
            count += 1
            
        except Exception as e:
            result.errors.append(f"Failed to migrate task: {e}")
    
    return count


def _migrate_transactions(
    transactions_data: List[Dict],
    storage: Storage,
    result: MigrationResult
) -> int:
    """Migrate financial transactions."""
    count = 0
    
    for trans_data in transactions_data:
        try:
            trans_date = trans_data.get('date') or trans_data.get('trans_date')
            if isinstance(trans_date, str):
                trans_date = date.fromisoformat(trans_date)
            
            transaction = Transaction(
                id=trans_data.get('id', generate_id()),
                description=trans_data.get('description', ''),
                amount=float(trans_data.get('amount', 0)),
                type=trans_data.get('type', 'expense'),
                category=trans_data.get('category', ''),
                trans_date=trans_date
            )
            
            storage._db.execute(
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
            count += 1
            
        except Exception as e:
            result.errors.append(f"Failed to migrate transaction: {e}")
    
    return count


def _migrate_health_entries(
    health_data: List[Dict],
    storage: Storage,
    result: MigrationResult
) -> int:
    """Migrate health entries."""
    count = 0
    
    for entry_data in health_data:
        try:
            entry_date = entry_data.get('date') or entry_data.get('entry_date')
            if isinstance(entry_date, str):
                entry_date = date.fromisoformat(entry_date)
            
            entry = HealthEntry(
                id=entry_data.get('id', generate_id()),
                entry_date=entry_date,
                weight=entry_data.get('weight'),
                sleep_hours=entry_data.get('sleepHours') or entry_data.get('sleep_hours'),
                mood=entry_data.get('mood', 'good'),
                notes=entry_data.get('notes', '')
            )
            
            storage._db.execute(
                """INSERT OR REPLACE INTO health_entries 
                   (id, entry_date, weight, sleep_hours, mood, notes, created_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (
                    entry.id, entry.entry_date.isoformat(),
                    entry.weight, entry.sleep_hours, entry.mood, entry.notes,
                    entry.created_at.isoformat()
                )
            )
            count += 1
            
        except Exception as e:
            result.errors.append(f"Failed to migrate health entry: {e}")
    
    return count


def _migrate_goals(
    goals_data: List[Dict],
    storage: Storage,
    result: MigrationResult
) -> int:
    """Migrate goals."""
    count = 0
    
    for goal_data in goals_data:
        try:
            deadline = goal_data.get('deadline')
            if isinstance(deadline, str):
                deadline = datetime.fromisoformat(deadline)
            
            goal = Goal(
                id=goal_data.get('id', generate_id()),
                title=goal_data.get('title', 'Untitled Goal'),
                description=goal_data.get('description', ''),
                target=float(goal_data.get('target', 0)),
                current=float(goal_data.get('current', 0)),
                unit=goal_data.get('unit', ''),
                deadline=deadline,
                completed=goal_data.get('completed', False)
            )
            
            storage._db.execute(
                """INSERT INTO goals 
                   (id, title, description, target, current, unit, deadline, 
                    completed, created_at, updated_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    goal.id, goal.title, goal.description, goal.target,
                    goal.current, goal.unit,
                    goal.deadline.isoformat() if goal.deadline else None,
                    goal.completed, goal.created_at.isoformat(), goal.updated_at.isoformat()
                )
            )
            count += 1
            
        except Exception as e:
            result.errors.append(f"Failed to migrate goal: {e}")
    
    return count


def _migrate_achievements(
    achievements_data: List[Dict],
    storage: Storage,
    result: MigrationResult
) -> int:
    """Migrate achievements."""
    count = 0
    
    for ach_data in achievements_data:
        try:
            unlocked_at = ach_data.get('unlockedAt') or ach_data.get('unlocked_at')
            if isinstance(unlocked_at, str):
                unlocked_at = datetime.fromisoformat(unlocked_at)
            
            achievement = Achievement(
                id=ach_data.get('id', generate_id()),
                name=ach_data.get('name', 'Unnamed Achievement'),
                description=ach_data.get('description', ''),
                icon=ach_data.get('icon', '🏆'),
                xp_reward=ach_data.get('xpReward') or ach_data.get('xp_reward', 0),
                unlocked_at=unlocked_at
            )
            
            storage._db.execute(
                """INSERT INTO achievements 
                   (id, name, description, icon, xp_reward, unlocked_at, created_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (
                    achievement.id, achievement.name, achievement.description,
                    achievement.icon, achievement.xp_reward,
                    achievement.unlocked_at.isoformat() if achievement.unlocked_at else None,
                    achievement.created_at.isoformat()
                )
            )
            count += 1
            
        except Exception as e:
            result.errors.append(f"Failed to migrate achievement: {e}")
    
    return count


def _migrate_user_data(user_data: Dict, storage: Storage) -> None:
    """Migrate user data (XP, level, settings)."""
    # Map of JS keys to storage keys
    key_mapping = {
        'xp': 'xp',
        'level': 'level',
        'streakFreezes': 'streak_freezes',
        'maxStreakFreezes': 'max_streak_freezes',
        'theme': 'theme'
    }
    
    for js_key, storage_key in key_mapping.items():
        if js_key in user_data:
            storage.set_user_data(storage_key, user_data[js_key])


def export_to_json(
    output_path: str,
    storage: Optional[Storage] = None
) -> Dict[str, Any]:
    """
    Export database contents to JSON format.
    
    Useful for backup or migration to other systems.
    
    Args:
        output_path: Path to save the JSON file
        storage: Optional storage instance
        
    Returns:
        Dictionary with exported data
    """
    storage = storage or get_storage()
    
    data = {
        "exported_at": datetime.now().isoformat(),
        "version": "1.0",
        "habits": [],
        "habitEntries": {},
        "tasks": [],
        "transactions": [],
        "healthEntries": [],
        "goals": [],
        "achievements": [],
        "userData": {}
    }
    
    # Export habits
    habits = storage.get_habits(include_archived=True)
    for habit in habits:
        data["habits"].append(habit.to_dict())
    
    # Export habit entries
    for habit in habits:
        entries = storage.get_habit_entries(habit.id)
        if entries:
            data["habitEntries"][habit.id] = [
                e.entry_date.isoformat() for e in entries if not e.skipped
            ]
    
    # Export tasks
    tasks = storage.get_tasks(include_completed=True)
    for task in tasks:
        data["tasks"].append(task.to_dict())
    
    # Export transactions
    transactions = storage.get_transactions()
    for trans in transactions:
        data["transactions"].append(trans.to_dict())
    
    # Export health entries
    health_entries = storage.get_health_entries()
    for entry in health_entries:
        data["healthEntries"].append(entry.to_dict())
    
    # Export goals
    goals = storage.get_goals(include_completed=True)
    for goal in goals:
        data["goals"].append(goal.to_dict())
    
    # Export achievements
    achievements = storage.get_achievements()
    for ach in achievements:
        data["achievements"].append(ach.to_dict())
    
    # Export user data
    for key in ['xp', 'level', 'streak_freezes', 'max_streak_freezes', 'theme']:
        value = storage.get_user_data(key)
        if value is not None:
            data["userData"][key] = value
    
    # Write to file
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, default=str)
    
    logger.info(f"Exported data to {output_path}")
    return data


# Export
__all__ = [
    "migrate_from_json",
    "export_to_json",
    "MigrationResult",
]