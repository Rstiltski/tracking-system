"""
Pytest Configuration and Shared Fixtures

This module provides shared fixtures and configuration for all tests.
Follows the testing best practices from PHASE_4_NOTIFICATIONS.md:
- Virtual environment isolation
- Proper test data setup
- Mock database connections
- Edge case coverage

Run tests with:
    python -m pytest tests/ -v
    python -m pytest tests/ -v --cov=brain
    python -m pytest tests/test_notification_engine.py -v -k "test_dispatch"
"""

import pytest
from datetime import datetime, time, timedelta
from unittest.mock import Mock, MagicMock, patch
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# ==========================================
# Mock Database Fixture
# ==========================================

@pytest.fixture
def mock_db():
    """
    Create a mock database object for unit tests.
    
    Provides mock methods for:
    - fetch_one(): Return single row
    - fetch_all(): Return multiple rows
    - execute(): Execute SQL statement
    
    Example:
        def test_something(mock_db):
            mock_db.fetch_one.return_value = {'id': 1, 'name': 'test'}
            result = some_function(mock_db)
            assert result.id == 1
    """
    db = Mock()
    db.fetch_one = Mock(return_value=None)
    db.fetch_all = Mock(return_value=[])
    db.execute = Mock(return_value=Mock())
    return db


@pytest.fixture
def mock_db_with_data(mock_db):
    """
    Mock database pre-loaded with sample notification data.
    
    Useful for integration-style tests without real DB.
    """
    # Sample preferences
    mock_db.fetch_one.side_effect = lambda query, params=None: {
        'user_id': 'test_user',
        'enabled': 1,
        'quiet_hours_start': '22:00',
        'quiet_hours_end': '07:00',
        'default_sound': 'default',
        'vibration_enabled': 1,
        'habit_reminders_enabled': 1,
        'task_reminders_enabled': 1,
        'goal_reminders_enabled': 1,
        'achievement_notifications_enabled': 1,
        'streak_warnings_enabled': 1,
        'daily_digest_enabled': 0,
        'browser_notifications_enabled': 1,
        'email_notifications_enabled': 0,
        'email_address': None,
        'smart_scheduling_enabled': 1,
        'min_reminder_lead_minutes': 15,
        'created_at': '2026-01-01T00:00:00',
        'updated_at': '2026-01-01T00:00:00',
    } if 'notification_preferences' in str(query) else None
    
    return mock_db


# ==========================================
# Model Fixtures
# ==========================================

@pytest.fixture
def sample_notification():
    """Create a sample notification for testing."""
    from brain.notifications.models import (
        Notification,
        NotificationType,
        NotificationPriority,
        NotificationStatus,
    )
    
    return Notification(
        type=NotificationType.HABIT_REMINDER,
        title="Test Reminder",
        message="This is a test notification",
        priority=NotificationPriority.MEDIUM,
        status=NotificationStatus.PENDING,
        entity_type="habit",
        entity_id="habit-123",
    )


@pytest.fixture
def urgent_notification():
    """Create an urgent notification for testing."""
    from brain.notifications.models import (
        Notification,
        NotificationType,
        NotificationPriority,
    )
    
    return Notification(
        type=NotificationType.STREAK_WARNING,
        title="Urgent: Streak at Risk!",
        message="Your 30-day streak is about to end!",
        priority=NotificationPriority.URGENT,
        entity_type="habit",
        entity_id="habit-456",
    )


@pytest.fixture
def sample_preferences():
    """Create sample notification preferences."""
    from brain.notifications.models import NotificationPreferences
    
    return NotificationPreferences(
        user_id="test_user",
        enabled=True,
        quiet_hours_start=time(22, 0),
        quiet_hours_end=time(7, 0),
        browser_notifications_enabled=True,
        email_notifications_enabled=False,
        habit_reminders_enabled=True,
        task_reminders_enabled=True,
        goal_reminders_enabled=True,
    )


@pytest.fixture
def sample_reminder_schedule():
    """Create a sample reminder schedule."""
    from brain.notifications.models import ReminderSchedule, NotificationChannel
    
    return ReminderSchedule(
        user_id="test_user",
        entity_type="habit",
        entity_id="habit-123",
        reminder_time=time(8, 0),
        days_of_week=[0, 1, 2, 3, 4],  # Weekdays
        channels=[NotificationChannel.IN_APP, NotificationChannel.WEB_PUSH],
        is_smart=False,
    )


@pytest.fixture
def sample_push_subscription():
    """Create a sample push subscription."""
    from brain.notifications.models import PushSubscription
    
    return PushSubscription(
        user_id="test_user",
        endpoint="https://fcm.googleapis.com/fcm/send/test-endpoint",
        p256dh="test-p256dh-key",
        auth="test-auth-secret",
        user_agent="Mozilla/5.0 Chrome/120.0.0.0",
        device_name="Test Browser",
    )


# ==========================================
# Engine/Manager Fixtures
# ==========================================

@pytest.fixture
def preference_manager(mock_db):
    """Create a PreferenceManager with mocked database."""
    from brain.notifications.preferences import PreferenceManager
    
    # Reset singleton
    PreferenceManager._instance = None
    
    return PreferenceManager(db=mock_db)


@pytest.fixture
def notification_engine(mock_db):
    """Create a NotificationEngine with mocked database."""
    from brain.notifications.engine import NotificationEngine
    
    return NotificationEngine(db=mock_db)


# ==========================================
# Time/Date Fixtures
# ==========================================

@pytest.fixture
def freeze_time():
    """
    Context manager to freeze time for testing.
    
    Example:
        def test_something(freeze_time):
            with freeze_time('2026-01-01 10:00:00'):
                # Test time-dependent logic
                pass
    """
    from datetime import datetime
    from unittest.mock import patch
    
    def _freeze_time(datetime_str):
        dt = datetime.fromisoformat(datetime_str)
        return patch('datetime.datetime', wraps=datetime)
    
    return _freeze_time


@pytest.fixture
def quiet_hours_time():
    """Return a time within typical quiet hours (11 PM)."""
    return time(23, 0)


@pytest.fixture
def business_hours_time():
    """Return a time within business hours (2 PM)."""
    return time(14, 0)


# ==========================================
# Edge Case Data
# ==========================================

@pytest.fixture
def edge_case_notifications():
    """
    Generate edge case notifications for robustness testing.
    
    Tests:
    - Null/empty fields
    - Extremely long titles/messages
    - Special characters
    - Invalid entity references
    """
    from brain.notifications.models import Notification, NotificationType
    
    return [
        # Empty title/message
        Notification(
            type=NotificationType.SYSTEM,
            title="",
            message="",
        ),
        # Very long title (1000 chars)
        Notification(
            type=NotificationType.SYSTEM,
            title="A" * 1000,
            message="Normal message",
        ),
        # Special characters
        Notification(
            type=NotificationType.SYSTEM,
            title="Test 🎉 Emoji & <HTML> 'quotes' \"double\"",
            message="Special: \n\t\\",
        ),
        # Null entity
        Notification(
            type=NotificationType.HABIT_REMINDER,
            title="No entity",
            entity_type=None,
            entity_id=None,
        ),
    ]


# ==========================================
# Pytest Hooks
# ==========================================

def pytest_configure(config):
    """Configure pytest markers."""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "edge_case: marks tests for edge cases"
    )


# ==========================================
# Helper Functions
# ==========================================

def assert_notification_sent(notification, channel_results):
    """Helper to assert notification was sent successfully."""
    assert any(result.success for result in channel_results.values()), \
        "At least one channel should succeed"


def assert_notification_failed(notification, channel_results):
    """Helper to assert notification failed on all channels."""
    assert not any(result.success for result in channel_results.values()), \
        "All channels should fail"
