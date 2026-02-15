"""
Migration Utility - Migrate existing data to event-sourced format.

This module provides utilities to migrate existing habit data
to the event-sourced format by generating events from current state.

Usage:
    from brain.audit.migration import HabitMigrator
    
    migrator = HabitMigrator()
    
    # Migrate a single habit
    migrator.migrate_habit(habit)
    
    # Migrate all habits from HabitBrain
    migrator.migrate_all_habits(habit_brain)
"""
from datetime import date, datetime
from typing import List, Dict, Any, Optional
import logging

from brain.models import Habit, Entry, EntryType
from brain.brains.habit_brain import HabitBrain
from brain.audit.habit_events import (
    HabitCreated,
    HabitCompleted,
    HabitSkipped,
    HabitArchived,
    StreakFreezeAwarded,
)
from brain.audit.event_store import get_event_publisher, get_event_store

logger = logging.getLogger(__name__)


class HabitMigrator:
    """
    Migrates existing habit data to event-sourced format.
    
    This utility reads the current state of habits and generates
    the corresponding events that would produce that state.
    
    Migration Process:
    1. Generate HABIT_CREATED event for each habit
    2. Generate HABIT_COMPLETED events for all completions
    3. Generate HABIT_SKIPPED events for all skips
    4. Generate HABIT_ARCHIVED events for archived habits
    5. Generate STREAK_FREEZE_AWARDED events for existing freezes
    """
    
    def __init__(self, dry_run: bool = False):
        """
        Initialize the migrator.
        
        Args:
            dry_run: If True, don't actually write events (just log)
        """
        self.dry_run = dry_run
        self.event_publisher = get_event_publisher()
        self.event_store = get_event_store()
        self.migrated_count = 0
        self.skipped_count = 0
        self.error_count = 0
    
    def migrate_habit(
        self,
        habit: Habit,
        skip_existing: bool = True
    ) -> Dict[str, Any]:
        """
        Migrate a single habit to event-sourced format.
        
        Args:
            habit: The habit to migrate
            skip_existing: Skip if habit already has events
        
        Returns:
            Migration result with counts
        """
        result = {
            "habit_id": habit.id,
            "habit_name": habit.name,
            "events_created": 0,
            "skipped": False,
            "error": None
        }
        
        try:
            # Check if habit already has events
            if skip_existing:
                existing_events = self.event_store.get_events(
                    entity_type="habit",
                    entity_id=habit.id
                )
                if existing_events:
                    logger.info(f"Habit {habit.id} already has {len(existing_events)} events, skipping")
                    self.skipped_count += 1
                    result["skipped"] = True
                    return result
            
            # Generate HABIT_CREATED event
            created_event = HabitCreated.create(
                habit_id=habit.id,
                name=habit.name,
                frequency=(habit.frequency.numerator, habit.frequency.denominator),
                description=habit.description,
                habit_type="boolean" if habit.habit_type.value == "boolean" else "numerical",
                color=habit.color,
                icon=habit.icon
            )
            
            if not self.dry_run:
                self.event_publisher.publish(created_event)
            result["events_created"] += 1
            logger.debug(f"Created HABIT_CREATED event for {habit.name}")
            
            # Generate completion/skip events for all entries
            for entry_date, entry in habit.entries.entries.items():
                if entry.is_completed:
                    event = HabitCompleted.create(
                        habit_id=habit.id,
                        completion_date=entry_date,
                        notes=entry.notes or ""
                    )
                    if not self.dry_run:
                        self.event_publisher.publish(event)
                    result["events_created"] += 1
                    
                elif entry.is_skip:
                    event = HabitSkipped.create(
                        habit_id=habit.id,
                        skip_date=entry_date,
                        reason=entry.notes or ""
                    )
                    if not self.dry_run:
                        self.event_publisher.publish(event)
                    result["events_created"] += 1
            
            # Generate HABIT_ARCHIVED event if archived
            if habit.is_archived:
                event = HabitArchived.create(habit_id=habit.id)
                if not self.dry_run:
                    self.event_publisher.publish(event)
                result["events_created"] += 1
            
            self.migrated_count += 1
            logger.info(f"Migrated habit '{habit.name}' with {result['events_created']} events")
            
        except Exception as e:
            self.error_count += 1
            result["error"] = str(e)
            logger.error(f"Error migrating habit {habit.id}: {e}")
        
        return result
    
    def migrate_all_habits(
        self,
        habit_brain: HabitBrain,
        skip_existing: bool = True
    ) -> Dict[str, Any]:
        """
        Migrate all habits from a HabitBrain instance.
        
        Args:
            habit_brain: The HabitBrain containing habits to migrate
            skip_existing: Skip habits that already have events
        
        Returns:
            Migration summary
        """
        results = {
            "total_habits": 0,
            "migrated": 0,
            "skipped": 0,
            "errors": 0,
            "total_events": 0,
            "details": []
        }
        
        habits = habit_brain.get_all_habits(include_archived=True)
        results["total_habits"] = len(habits)
        
        for habit in habits:
            detail = self.migrate_habit(habit, skip_existing)
            results["details"].append(detail)
            
            if detail["skipped"]:
                results["skipped"] += 1
            elif detail["error"]:
                results["errors"] += 1
            else:
                results["migrated"] += 1
                results["total_events"] += detail["events_created"]
        
        logger.info(
            f"Migration complete: {results['migrated']} migrated, "
            f"{results['skipped']} skipped, {results['errors']} errors, "
            f"{results['total_events']} total events"
        )
        
        return results
    
    def migrate_inventory(
        self,
        inventory,
        user_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Migrate inventory (streak freezes) to events.
        
        Args:
            inventory: UserInventory instance
            user_id: Optional user ID
        
        Returns:
            Migration result
        """
        result = {
            "events_created": 0,
            "error": None
        }
        
        try:
            # Generate STREAK_FREEZE_AWARDED events for existing freezes
            freeze_count = inventory.streak_freezes.count
            
            for i in range(freeze_count):
                event = StreakFreezeAwarded.create(
                    reason="Migration: Existing streak freeze",
                    freezes_count=i + 1,
                    user_id=user_id
                )
                if not self.dry_run:
                    self.event_publisher.publish(event)
                result["events_created"] += 1
            
            logger.info(f"Migrated {freeze_count} streak freezes")
            
        except Exception as e:
            result["error"] = str(e)
            logger.error(f"Error migrating inventory: {e}")
        
        return result
    
    def verify_migration(
        self,
        habit_brain: HabitBrain
    ) -> Dict[str, Any]:
        """
        Verify that migrated data matches original data.
        
        Args:
            habit_brain: The HabitBrain to verify against
        
        Returns:
            Verification results
        """
        from brain.audit.event_replay import get_event_replayer
        
        replayer = get_event_replayer()
        
        results = {
            "verified": 0,
            "mismatched": 0,
            "missing": 0,
            "details": []
        }
        
        habits = habit_brain.get_all_habits(include_archived=True)
        
        for habit in habits:
            detail = {
                "habit_id": habit.id,
                "habit_name": habit.name,
                "matched": True,
                "issues": []
            }
            
            # Rebuild habit from events
            rebuilt = replayer.rebuild_habit(habit.id)
            
            if rebuilt is None:
                results["missing"] += 1
                detail["matched"] = False
                detail["issues"].append("No events found for habit")
                results["details"].append(detail)
                continue
            
            # Compare fields
            if rebuilt.name != habit.name:
                detail["matched"] = False
                detail["issues"].append(f"Name mismatch: {rebuilt.name} != {habit.name}")
            
            if rebuilt.description != habit.description:
                detail["matched"] = False
                detail["issues"].append("Description mismatch")
            
            if rebuilt.is_archived != habit.is_archived:
                detail["matched"] = False
                detail["issues"].append("Archive status mismatch")
            
            # Compare entry counts
            rebuilt_completions = rebuilt.total_completions
            original_completions = sum(
                1 for e in habit.entries.entries.values() if e.is_completed
            )
            
            if rebuilt_completions != original_completions:
                detail["matched"] = False
                detail["issues"].append(
                    f"Completion count mismatch: {rebuilt_completions} != {original_completions}"
                )
            
            if detail["matched"]:
                results["verified"] += 1
            else:
                results["mismatched"] += 1
            
            results["details"].append(detail)
        
        return results
    
    def get_migration_status(self) -> Dict[str, Any]:
        """
        Get the current migration status.
        
        Returns:
            Status information
        """
        return {
            "migrated_count": self.migrated_count,
            "skipped_count": self.skipped_count,
            "error_count": self.error_count,
            "dry_run": self.dry_run
        }


def migrate_from_json_file(
    filepath: str,
    dry_run: bool = False
) -> Dict[str, Any]:
    """
    Migrate habits from a JSON file.
    
    Args:
        filepath: Path to the JSON file
        dry_run: If True, don't actually write events
    
    Returns:
        Migration results
    """
    import json
    
    migrator = HabitMigrator(dry_run=dry_run)
    
    try:
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        # Create HabitBrain from the data
        habit_brain = HabitBrain.from_dict(data)
        
        # Migrate all habits
        return migrator.migrate_all_habits(habit_brain)
        
    except FileNotFoundError:
        return {"error": f"File not found: {filepath}"}
    except json.JSONDecodeError as e:
        return {"error": f"Invalid JSON: {e}"}
    except Exception as e:
        return {"error": str(e)}


# Export
__all__ = [
    "HabitMigrator",
    "migrate_from_json_file",
]