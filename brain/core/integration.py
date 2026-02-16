"""
Unified Connection Layer - Central Interface for Veryfyn Tracking System

This module provides a central interface that enforces strict execution order 
between the frontend, brain, and database modules. It ensures that the Brain 
cannot execute logic without a valid connection to tracking_app.database.

The interface implements:
1. Connection validation between Brain and Database
2. Unified API for frontend-backend communication
3. Proper integration with the existing Brain architecture
4. Synchronization between LocalStorage and backend database
"""

from typing import Optional, Dict, Any, Union
import sqlite3
import logging
from contextlib import contextmanager

logger = logging.getLogger(__name__)


class UnifiedConnectionLayer:
    """
    Central interface that manages connections between frontend, brain, and database.
    
    This layer ensures proper integration between:
    - Frontend (js/*.js) with LocalStorage
    - Brain system with its tools and policies
    - Database layer (tracking_app)
    """
    
    def __init__(self):
        self.brain = None
        self.cerebellum = None
        self.database = None
        self.is_connected: bool = False
        
    def initialize_connections(self) -> bool:
        """
        Initialize connections to all required systems.
        
        Returns:
            bool: True if all connections are successful, False otherwise
        """
        try:
            # Initialize database connection
            from tracking_app.database import Database
            self.database = Database()
            
            # Verify database connectivity
            with self.database.get_connection() as conn:
                # Test connection by performing a simple query
                conn.execute("SELECT 1")
                
            # Initialize cerebellum with database connection
            from brain.core.cerebellum import Cerebellum
            self.cerebellum = Cerebellum(self.database.get_connection())
            
            # Initialize brain with database connection
            from brain.core.brain import Brain
            # Get the raw sqlite3 connection from the context manager
            with self.database.get_connection() as conn:
                # Create a new connection for the Brain since it expects a raw connection
                brain_db_path = self.database.db_path
            self.brain = Brain(db_connection=sqlite3.connect(brain_db_path))
            
            self.is_connected = True
            logger.info("Unified connection layer initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize unified connection layer: {e}")
            self.is_connected = False
            return False
    
    def validate_connection(self) -> bool:
        """
        Validate that all required connections are active.
        
        Returns:
            bool: True if all connections are valid, False otherwise
        """
        if not self.is_connected:
            return False
            
        if not self.database:
            return False
            
        try:
            # Test database connection
            with self.database.get_connection() as conn:
                conn.execute("SELECT 1")
            return True
        except Exception:
            return False
    
    def execute_brain_command(self, command_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a command through the Brain system with proper connection validation.
        
        Args:
            command_data: Dictionary containing command information
            
        Returns:
            Dict with result of the command execution
        """
        if not self.validate_connection():
            raise ConnectionError("Unified connection layer is not properly connected")
            
        if not self.brain:
            raise RuntimeError("Brain system is not initialized")
            
        # Create a CommandEvent from the command data
        from brain.core.command_event import CommandEvent
        command_event = CommandEvent(
            command_type=command_data.get('command_type', ''),
            params=command_data.get('params', {}),
            user_id=command_data.get('user_id', 1),  # Default user
            company_id=command_data.get('company_id', 1)  # Default company
        )
        
        # Execute the command through the brain system
        # This follows the proper Brain architecture (Router -> Policies -> State -> Tools)
        result = self.brain.run(command_event)
        
        # Convert result to dictionary for return
        return {
            'success': result.success,
            'data': result.data if hasattr(result, 'data') else None,
            'error': result.error if hasattr(result, 'error') else None,
            'command_id': result.command_id if hasattr(result, 'command_id') else None
        }
    
    def sync_frontend_data(self, frontend_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Synchronize data from frontend (LocalStorage) with backend database.
        
        Args:
            frontend_data: Data from frontend LocalStorage
            
        Returns:
            Dict with synchronization result
        """
        if not self.validate_connection():
            raise ConnectionError("Unified connection layer is not properly connected")
            
        # Process different types of data from frontend
        sync_result = {
            'success': True,
            'processed_items': 0,
            'errors': []
        }
        
        try:
            # Process habits
            if 'habits' in frontend_data:
                from tracking_app.models import Habit
                for habit_data in frontend_data['habits']:
                    # Convert frontend habit data to backend model
                    habit = Habit.from_dict(habit_data) if hasattr(Habit, 'from_dict') else Habit(**habit_data)
                    
                    # Create a command to add/update the habit through the Brain system
                    command_data = {
                        'command_type': 'HabitCreate' if 'id' not in habit_data else 'HabitUpdate',
                        'params': habit_data,
                        'user_id': 1,  # Default user
                        'company_id': 1  # Default company
                    }
                    self.execute_brain_command(command_data)
            
            # Process tasks
            if 'tasks' in frontend_data:
                from tracking_app.models import Task
                for task_data in frontend_data['tasks']:
                    task = Task.from_dict(task_data) if hasattr(Task, 'from_dict') else Task(**task_data)
                    
                    # Create a command to add/update the task through the Brain system
                    command_data = {
                        'command_type': 'TaskCreate' if 'id' not in task_data else 'TaskUpdate',
                        'params': task_data,
                        'user_id': 1,  # Default user
                        'company_id': 1  # Default company
                    }
                    self.execute_brain_command(command_data)
            
            # Process finances
            if 'transactions' in frontend_data:
                from tracking_app.models import Transaction
                for transaction_data in frontend_data['transactions']:
                    transaction = Transaction.from_dict(transaction_data) if hasattr(Transaction, 'from_dict') else Transaction(**transaction_data)
                    
                    # Create a command to add/update the transaction through the Brain system
                    command_data = {
                        'command_type': 'TransactionCreate' if 'id' not in transaction_data else 'TransactionUpdate',
                        'params': transaction_data,
                        'user_id': 1,  # Default user
                        'company_id': 1  # Default company
                    }
                    self.execute_brain_command(command_data)
            
            # Process health entries
            if 'health' in frontend_data:
                from tracking_app.models import HealthEntry
                for health_data in frontend_data['health']:
                    health_entry = HealthEntry.from_dict(health_data) if hasattr(HealthEntry, 'from_dict') else HealthEntry(**health_data)
                    
                    # Create a command to add/update the health entry through the Brain system
                    command_data = {
                        'command_type': 'HealthEntryCreate' if 'id' not in health_data else 'HealthEntryUpdate',
                        'params': health_data,
                        'user_id': 1,  # Default user
                        'company_id': 1  # Default company
                    }
                    self.execute_brain_command(command_data)
            
            # Process goals
            if 'goals' in frontend_data:
                from tracking_app.models import Goal
                for goal_data in frontend_data['goals']:
                    goal = Goal.from_dict(goal_data) if hasattr(Goal, 'from_dict') else Goal(**goal_data)
                    
                    # Create a command to add/update the goal through the Brain system
                    command_data = {
                        'command_type': 'GoalCreate' if 'id' not in goal_data else 'GoalUpdate',
                        'params': goal_data,
                        'user_id': 1,  # Default user
                        'company_id': 1  # Default company
                    }
                    self.execute_brain_command(command_data)
            
            sync_result['processed_items'] = sum([
                len(frontend_data.get('habits', [])),
                len(frontend_data.get('tasks', [])),
                len(frontend_data.get('transactions', [])),
                len(frontend_data.get('health', [])),
                len(frontend_data.get('goals', []))
            ])
            
        except Exception as e:
            sync_result['success'] = False
            sync_result['errors'].append(str(e))
            
        return sync_result
    
    def get_backend_data(self) -> Dict[str, Any]:
        """
        Retrieve data from backend database for frontend synchronization.
        
        Returns:
            Dict containing backend data organized by type
        """
        if not self.validate_connection():
            raise ConnectionError("Unified connection layer is not properly connected")
            
        backend_data = {}
        
        try:
            # Retrieve habits
            with self.database.get_connection() as conn:
                # Get all habits from the database
                habits_cursor = conn.execute("SELECT * FROM habits ORDER BY created_at DESC")
                backend_data['habits'] = [dict(row) for row in habits_cursor.fetchall()]
                
            # Retrieve tasks
            with self.database.get_connection() as conn:
                # Get all tasks from the database
                tasks_cursor = conn.execute("SELECT * FROM tasks ORDER BY created_at DESC")
                backend_data['tasks'] = [dict(row) for row in tasks_cursor.fetchall()]
                
            # Retrieve transactions
            with self.database.get_connection() as conn:
                # Get all transactions from the database
                transactions_cursor = conn.execute("SELECT * FROM transactions ORDER BY created_at DESC")
                backend_data['transactions'] = [dict(row) for row in transactions_cursor.fetchall()]
                
            # Retrieve health entries
            with self.database.get_connection() as conn:
                # Get all health entries from the database
                health_cursor = conn.execute("SELECT * FROM health_entries ORDER BY created_at DESC")
                backend_data['health'] = [dict(row) for row in health_cursor.fetchall()]
                
            # Retrieve goals
            with self.database.get_connection() as conn:
                # Get all goals from the database
                goals_cursor = conn.execute("SELECT * FROM goals ORDER BY created_at DESC")
                backend_data['goals'] = [dict(row) for row in goals_cursor.fetchall()]
                
        except Exception as e:
            logger.error(f"Error retrieving backend data: {e}")
            backend_data['error'] = str(e)
            
        return backend_data


# Global instance for easy access (following singleton pattern)
_unified_connector: Optional[UnifiedConnectionLayer] = None


def get_unified_connector() -> UnifiedConnectionLayer:
    """
    Get the global unified connection layer instance.
    
    Returns:
        UnifiedConnectionLayer instance
    """
    global _unified_connector
    if _unified_connector is None:
        _unified_connector = UnifiedConnectionLayer()
        _unified_connector.initialize_connections()
    return _unified_connector


def reset_unified_connector():
    """
    Reset the global unified connection layer instance.
    Useful for testing or reinitialization.
    """
    global _unified_connector
    _unified_connector = None


# API endpoints that the frontend can call
class UnifiedAPI:
    """
    API layer that provides endpoints for frontend-backend communication.
    This simulates what would be actual API endpoints in a real implementation.
    """
    
    @staticmethod
    def sync_data_with_backend(frontend_payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        API endpoint to synchronize frontend data with backend.
        
        Args:
            frontend_payload: Data from frontend to sync with backend
            
        Returns:
            Response dictionary
        """
        connector = get_unified_connector()
        return connector.sync_frontend_data(frontend_payload)
    
    @staticmethod
    def get_backend_sync_data() -> Dict[str, Any]:
        """
        API endpoint to get backend data for frontend synchronization.
        
        Returns:
            Response dictionary with backend data
        """
        connector = get_unified_connector()
        return connector.get_backend_data()
    
    @staticmethod
    def execute_backend_command(command: Dict[str, Any]) -> Dict[str, Any]:
        """
        API endpoint to execute a command through the Brain system.
        
        Args:
            command: Command to execute
            
        Returns:
            Response dictionary with command result
        """
        connector = get_unified_connector()
        return connector.execute_brain_command(command)


# Example usage:
if __name__ == "__main__":
    # Initialize the unified connection layer
    connector = get_unified_connector()
    
    if connector.validate_connection():
        print("Unified connection layer is ready!")
        print("Frontend, Brain, and Database are properly connected.")
    else:
        print("Failed to establish unified connection.")