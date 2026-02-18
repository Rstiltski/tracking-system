"""
Unit Tests for Notification Preferences

Tests the PreferenceManager decision logic and preference management.

Phase 4.4 Feature: Notification Settings UI

Run with: python -m pytest tests/test_notification_preferences.py -v
"""

import unittest
from datetime import time, datetime
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestNotificationPreferences(unittest.TestCase):
    """Test cases for notification preferences."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a mock database
        self.mock_db = Mock()
        
        # Import with mocked database
        from brain.notifications.preferences import PreferenceManager
        from brain.notifications.models import (
            NotificationPreferences,
            NotificationType,
            NotificationChannel,
            NotificationPriority,
        )
        
        self.PreferenceManager = PreferenceManager
        self.NotificationPreferences = NotificationPreferences
        self.NotificationType = NotificationType
        self.NotificationChannel = NotificationChannel
        self.NotificationPriority = NotificationPriority
        
        # Reset singleton for each test
        self.PreferenceManager._instance = None
    
    def test_get_default_preferences(self):
        """Test that default preferences are returned when none exist."""
        # Mock database returns None (no preferences)
        self.mock_db.fetch_one.return_value = None
        
        pm = self.PreferenceManager(db=self.mock_db)
        prefs = pm.get_user_preferences("test_user")
        
        # Should return defaults
        self.assertEqual(prefs.user_id, "test_user")
        self.assertTrue(prefs.enabled)
        self.assertIsNone(prefs.quiet_hours_start)
        self.assertTrue(prefs.browser_notifications_enabled)
    
    def test_get_existing_preferences(self):
        """Test retrieving existing preferences."""
        # Mock database returns existing preferences
        self.mock_db.fetch_one.return_value = {
            'user_id': 'test_user',
            'enabled': 0,
            'quiet_hours_start': '22:00',
            'quiet_hours_end': '07:00',
            'default_sound': 'default',
            'vibration_enabled': 1,
            'habit_reminders_enabled': 1,
            'task_reminders_enabled': 0,
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
        }
        
        pm = self.PreferenceManager(db=self.mock_db)
        prefs = pm.get_user_preferences("test_user")
        
        self.assertEqual(prefs.user_id, "test_user")
        self.assertFalse(prefs.enabled)
        self.assertEqual(prefs.quiet_hours_start, time(22, 0))
        self.assertEqual(prefs.quiet_hours_end, time(7, 0))
        self.assertFalse(prefs.task_reminders_enabled)
    
    def test_save_preferences(self):
        """Test saving preferences."""
        self.mock_db.execute.return_value = Mock()
        
        pm = self.PreferenceManager(db=self.mock_db)
        prefs = self.NotificationPreferences(
            user_id="test_user",
            enabled=True,
            quiet_hours_start=time(22, 0),
            quiet_hours_end=time(7, 0),
        )
        
        result = pm.save_preferences(prefs)
        
        self.assertTrue(result)
        self.mock_db.execute.assert_called_once()
    
    def test_should_notify_global_disabled(self):
        """Test that global disable blocks all notifications."""
        # Setup: Global is False
        prefs = self.NotificationPreferences(
            user_id="test_user",
            enabled=False,
        )
        
        self.mock_db.fetch_one.return_value = prefs.to_dict()
        
        pm = self.PreferenceManager(db=self.mock_db)
        
        result = pm.should_notify(
            "test_user",
            self.NotificationType.HABIT_REMINDER,
            self.NotificationChannel.EMAIL
        )
        
        self.assertFalse(result, "Global disable failed to block notification")
    
    def test_should_notify_channel_disabled(self):
        """Test that disabled channel blocks notification."""
        prefs = self.NotificationPreferences(
            user_id="test_user",
            enabled=True,
            email_notifications_enabled=False,
        )
        
        self.mock_db.fetch_one.return_value = prefs.to_dict()
        
        pm = self.PreferenceManager(db=self.mock_db)
        
        result = pm.should_notify(
            "test_user",
            self.NotificationType.HABIT_REMINDER,
            self.NotificationChannel.EMAIL
        )
        
        self.assertFalse(result, "Channel disable failed to block notification")
    
    def test_should_notify_type_disabled(self):
        """Test that disabled type blocks notification."""
        prefs = self.NotificationPreferences(
            user_id="test_user",
            enabled=True,
            browser_notifications_enabled=True,
            task_reminders_enabled=False,
        )
        
        self.mock_db.fetch_one.return_value = prefs.to_dict()
        
        pm = self.PreferenceManager(db=self.mock_db)
        
        result = pm.should_notify(
            "test_user",
            self.NotificationType.TASK_DUE,
            self.NotificationChannel.WEB_PUSH
        )
        
        self.assertFalse(result, "Type disable failed to block notification")
    
    def test_should_notify_quiet_hours(self):
        """Test that quiet hours block notification."""
        # Set quiet hours to current time +/- 1 hour
        now = datetime.now()
        start = time(now.hour, 0) if now.minute < 30 else time((now.hour + 1) % 24, 0)
        end = time((now.hour + 2) % 24, 0)
        
        prefs = self.NotificationPreferences(
            user_id="test_user",
            enabled=True,
            browser_notifications_enabled=True,
            habit_reminders_enabled=True,
            quiet_hours_start=start,
            quiet_hours_end=end,
        )
        
        self.mock_db.fetch_one.return_value = prefs.to_dict()
        
        pm = self.PreferenceManager(db=self.mock_db)
        
        result = pm.should_notify(
            "test_user",
            self.NotificationType.HABIT_REMINDER,
            self.NotificationChannel.WEB_PUSH
        )
        
        self.assertFalse(result, "Quiet hours failed to block notification")
    
    def test_should_notify_urgent_bypasses_quiet_hours(self):
        """Test that urgent notifications bypass quiet hours."""
        now = datetime.now()
        start = time(now.hour, 0) if now.minute < 30 else time((now.hour + 1) % 24, 0)
        end = time((now.hour + 2) % 24, 0)
        
        prefs = self.NotificationPreferences(
            user_id="test_user",
            enabled=True,
            browser_notifications_enabled=True,
            habit_reminders_enabled=True,
            quiet_hours_start=start,
            quiet_hours_end=end,
        )
        
        self.mock_db.fetch_one.return_value = prefs.to_dict()
        
        pm = self.PreferenceManager(db=self.mock_db)
        
        result = pm.should_notify(
            "test_user",
            self.NotificationType.HABIT_REMINDER,
            self.NotificationChannel.WEB_PUSH,
            self.NotificationPriority.URGENT
        )
        
        self.assertTrue(result, "Urgent notification should bypass quiet hours")
    
    def test_quiet_hours_cross_midnight(self):
        """Test quiet hours that cross midnight."""
        # Quiet hours 22:00 to 06:00
        prefs = self.NotificationPreferences(
            user_id="test_user",
            quiet_hours_start=time(22, 0),
            quiet_hours_end=time(6, 0),
        )
        
        # Test times within quiet hours
        self.assertTrue(prefs.is_quiet_hours_at(time(23, 0)))  # 11 PM
        self.assertTrue(prefs.is_quiet_hours_at(time(2, 0)))   # 2 AM
        self.assertTrue(prefs.is_quiet_hours_at(time(5, 30)))  # 5:30 AM
        
        # Test times outside quiet hours
        self.assertFalse(prefs.is_quiet_hours_at(time(8, 0)))  # 8 AM
        self.assertFalse(prefs.is_quiet_hours_at(time(12, 0))) # Noon
        self.assertFalse(prefs.is_quiet_hours_at(time(21, 0))) # 9 PM
    
    def test_quiet_hours_same_day(self):
        """Test quiet hours within same day."""
        # Quiet hours 13:00 to 17:00
        prefs = self.NotificationPreferences(
            user_id="test_user",
            quiet_hours_start=time(13, 0),
            quiet_hours_end=time(17, 0),
        )
        
        # Test times within quiet hours
        self.assertTrue(prefs.is_quiet_hours_at(time(14, 0)))  # 2 PM
        self.assertTrue(prefs.is_quiet_hours_at(time(16, 30))) # 4:30 PM
        
        # Test times outside quiet hours
        self.assertFalse(prefs.is_quiet_hours_at(time(10, 0))) # 10 AM
        self.assertFalse(prefs.is_quiet_hours_at(time(18, 0))) # 6 PM
    
    def test_set_global_enabled(self):
        """Test enabling/disabling global notifications."""
        self.mock_db.fetch_one.return_value = None
        self.mock_db.execute.return_value = Mock()
        
        pm = self.PreferenceManager(db=self.mock_db)
        
        result = pm.set_global_enabled("test_user", False)
        
        self.assertTrue(result)
        self.mock_db.execute.assert_called()
    
    def test_set_quiet_hours(self):
        """Test setting quiet hours."""
        self.mock_db.fetch_one.return_value = None
        self.mock_db.execute.return_value = Mock()
        
        pm = self.PreferenceManager(db=self.mock_db)
        
        result = pm.set_quiet_hours("test_user", time(22, 0), time(7, 0))
        
        self.assertTrue(result)
        self.mock_db.execute.assert_called()
    
    def test_set_type_enabled(self):
        """Test enabling/disabling notification types."""
        self.mock_db.fetch_one.return_value = None
        self.mock_db.execute.return_value = Mock()
        
        pm = self.PreferenceManager(db=self.mock_db)
        
        result = pm.set_type_enabled("test_user", "habit", False)
        
        self.assertTrue(result)
    
    def test_set_channel_enabled(self):
        """Test enabling/disabling channels."""
        self.mock_db.fetch_one.return_value = None
        self.mock_db.execute.return_value = Mock()
        
        pm = self.PreferenceManager(db=self.mock_db)
        
        result = pm.set_channel_enabled("test_user", "email", True)
        
        self.assertTrue(result)
    
    def test_reset_to_defaults(self):
        """Test resetting preferences to defaults."""
        self.mock_db.fetch_one.return_value = None
        self.mock_db.execute.return_value = Mock()
        
        pm = self.PreferenceManager(db=self.mock_db)
        
        result = pm.reset_to_defaults("test_user")
        
        self.assertTrue(result)
        self.mock_db.execute.assert_called()
    
    def test_get_enabled_types(self):
        """Test getting enabled notification types."""
        prefs = self.NotificationPreferences(
            user_id="test_user",
            habit_reminders_enabled=True,
            task_reminders_enabled=False,
            goal_reminders_enabled=True,
            achievement_notifications_enabled=True,
            streak_warnings_enabled=False,
            daily_digest_enabled=False,
        )
        
        self.mock_db.fetch_one.return_value = prefs.to_dict()
        
        pm = self.PreferenceManager(db=self.mock_db)
        types = pm.get_enabled_types("test_user")
        
        self.assertTrue(types['habit'])
        self.assertFalse(types['task'])
        self.assertTrue(types['goal'])
        self.assertFalse(types['streak_warning'])
    
    def test_get_enabled_channels(self):
        """Test getting enabled channels."""
        prefs = self.NotificationPreferences(
            user_id="test_user",
            browser_notifications_enabled=True,
            email_notifications_enabled=False,
        )
        
        self.mock_db.fetch_one.return_value = prefs.to_dict()
        
        pm = self.PreferenceManager(db=self.mock_db)
        channels = pm.get_enabled_channels("test_user")
        
        self.assertTrue(channels['browser'])
        self.assertFalse(channels['email'])
    
    def test_notification_history(self):
        """Test getting notification history."""
        self.mock_db.fetch_all.return_value = [
            {
                'id': 'notif-1',
                'type': 'habit_reminder',
                'title': 'Test Notification',
                'message': 'Test message',
                'priority': 'medium',
                'entity_type': 'habit',
                'entity_id': 'habit-1',
                'created_at': '2026-01-01T10:00:00',
                'read': 0,
                'channel': 'in_app',
                'delivery_status': 'sent',
            }
        ]
        
        pm = self.PreferenceManager(db=self.mock_db)
        history = pm.get_notification_history("test_user")
        
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0]['title'], 'Test Notification')
    
    def test_notification_stats(self):
        """Test getting notification statistics."""
        self.mock_db.fetch_one.return_value = {'count': 10}
        self.mock_db.fetch_all.return_value = [
            {'status': 'sent', 'count': 8},
            {'status': 'failed', 'count': 2},
        ]
        
        pm = self.PreferenceManager(db=self.mock_db)
        stats = pm.get_notification_stats("test_user")
        
        self.assertEqual(stats['total_notifications'], 10)
        self.assertEqual(stats['by_status']['sent'], 8)
        self.assertEqual(stats['by_status']['failed'], 2)


class TestNotificationPreferencesModel(unittest.TestCase):
    """Test cases for NotificationPreferences dataclass."""
    
    def test_is_quiet_hours_at(self):
        """Test quiet hours check at specific time."""
        from brain.notifications.models import NotificationPreferences
        
        # Cross-midnight quiet hours
        prefs = NotificationPreferences(
            user_id="test",
            quiet_hours_start=time(22, 0),
            quiet_hours_end=time(6, 0),
        )
        
        # Test various times
        self.assertTrue(prefs.is_quiet_hours_at(time(23, 0)))
        self.assertTrue(prefs.is_quiet_hours_at(time(3, 0)))
        self.assertFalse(prefs.is_quiet_hours_at(time(10, 0)))
        self.assertFalse(prefs.is_quiet_hours_at(time(21, 0)))
    
    def test_is_type_enabled(self):
        """Test notification type enable check."""
        from brain.notifications.models import NotificationPreferences, NotificationType
        
        prefs = NotificationPreferences(
            user_id="test",
            habit_reminders_enabled=True,
            task_reminders_enabled=False,
        )
        
        self.assertTrue(prefs.is_type_enabled(NotificationType.HABIT_REMINDER))
        self.assertFalse(prefs.is_type_enabled(NotificationType.TASK_DUE))
        self.assertTrue(prefs.is_type_enabled(NotificationType.SYSTEM))  # Always enabled
    
    def test_to_dict_and_from_dict(self):
        """Test serialization and deserialization."""
        from brain.notifications.models import NotificationPreferences
        
        original = NotificationPreferences(
            user_id="test_user",
            enabled=True,
            quiet_hours_start=time(22, 0),
            quiet_hours_end=time(7, 0),
            browser_notifications_enabled=True,
            email_notifications_enabled=False,
            email_address="test@example.com",
        )
        
        data = original.to_dict()
        restored = NotificationPreferences.from_dict(data)
        
        self.assertEqual(restored.user_id, original.user_id)
        self.assertEqual(restored.enabled, original.enabled)
        self.assertEqual(restored.quiet_hours_start, original.quiet_hours_start)
        self.assertEqual(restored.quiet_hours_end, original.quiet_hours_end)
        self.assertEqual(restored.email_address, original.email_address)


if __name__ == '__main__':
    unittest.main()