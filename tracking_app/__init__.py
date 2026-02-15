"""
Tracking App - Personal Tracking System

A Python/Streamlit application for tracking habits, tasks, finances, health, and more.

This module provides the core functionality for the tracking system,
replacing the legacy JavaScript frontend.
"""

__version__ = "0.1.0"
__author__ = "TrackLife Team"

# Import key modules for easy access
from tracking_app.database import Database, get_db, init_db
from tracking_app.models import Habit, Task, Transaction, HealthEntry, Goal
from tracking_app.storage import Storage

__all__ = [
    "Database",
    "get_db",
    "init_db",
    "Habit",
    "Task",
    "Transaction",
    "HealthEntry",
    "Goal",
    "Storage",
]