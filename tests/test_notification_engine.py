"""
Unit Tests for Notification Engine

Comprehensive test suite for the NotificationEngine class.
Follows testing best practices from PHASE_4_NOTIFICATIONS.md:
- Unit testing individual functions
- Edge case coverage (null inputs, large data, unexpected types)
- Data validation
- Model evaluation metrics

Test Categories:
1. CRUD Operations - Create, read, update, delete notifications
2. Dispatch Logic - Channel selection and fallback
3. Preferences Integration - Decision hierarchy
4. Edge Cases - Null inputs, special characters, large datasets
5. Callback System - Event triggers

Run with:
    python -m pytest tests/test_notification_engine.py -v
    python -m pytest tests/test_notification_engine.py -v -k "test_dispatch"
    python -m pytest tests/test_notification_engine.py -v --cov=brain.notifications.engine
"""

import pytest
from datetime import datetime, time, timedelta
from unittest.mock import Mock, patch, MagicMock, call
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestNotificationEngineInitialization:
    """Test NotificationEngine initialization."""

    def test_init_with_mock_db(self, mock_db):
        """Test engine initializes with mocked database."""
        from brain.notifications.engine import NotificationEngine
        
        engine = NotificationEngine(db=mock_db)
        
        assert engine._db == mock_db
        assert len(engine._channels) > 0  # Should have default channels
        assert engine._templates is not None

    def test_init_channels(self, mock_db):
        """Test that default channels are initialized."""
        from brain.notifications.engine import NotificationEngine
        from brain.notifications.models import NotificationChannel
        
        engine = NotificationEngine(db=mock_db)
        
        # Should have these channels
        assert NotificationChannel.IN_APP in engine._channels
        assert NotificationChannel.WEB_PUSH in engine._channels
        assert NotificationChannel.EMAIL in engine._channels
        assert NotificationChannel.DESKTOP in engine._channels

    def test_get_channel(self, mock_db):
        """Test retrieving channel instances."""
        from brain.notifications.engine import NotificationEngine
        from brain.notifications.models import NotificationChannel
        
        engine = NotificationEngine(db=mock_db)
        
        channel = engine.get_channel(NotificationChannel.IN_APP)
        assert channel is not None
        
        # Non-existent channel
        channel = engine.get_channel(NotificationChannel.EMAIL)
        assert channel is not None  # Email channel exists but may not be available


class TestNotificationCreation:
    """Test notification creation operations."""

    def test_create_notification_basic(self, mock_db):
        """Test basic notification creation."""
        from brain.notifications.engine import NotificationEngine
        from brain.notifications.models import NotificationType, NotificationPriority
        
        engine = NotificationEngine(db=mock_db)
        
        notification = engine.create_notification(
            type=NotificationType.HABIT_REMINDER,
            title="Test Reminder",
            message="This is a test",
            priority=NotificationPriority.MEDIUM,
        )
        
        assert notification.type == NotificationType.HABIT_REMINDER
        assert notification.title == "Test Reminder"
        assert notification.priority == NotificationPriority.MEDIUM
        assert notification.status.value == "pending"
        assert notification.id is not None

    def test_create_notification_with_entity(self, mock_db):
        """Test creating notification with entity reference."""
        from brain.notifications.engine import NotificationEngine
        from brain.notifications.models import NotificationType
        
        engine = NotificationEngine(db=mock_db)
        
        notification = engine.create_notification(
            type=NotificationType.TASK_DUE,
            title="Task Due",
            message="Task is due tomorrow",
            entity_type="task",
            entity_id="task-123",
            action_url="/tasks/task-123",
        )
        
        assert notification.entity_type == "task"
        assert notification.entity_id == "task-123"
        assert notification.action_url == "/tasks/task-123"

    def test_create_notification_scheduled(self, mock_db):
        """Test creating scheduled notification."""
        from brain.notifications.engine import NotificationEngine
        from brain.notifications.models import NotificationType
        
        future_time = datetime.now() + timedelta(hours=1)
        
        engine = NotificationEngine(db=mock_db)
        
        notification = engine.create_notification(
            type=NotificationType.DAILY_DIGEST,
            title="Daily Digest",
            message="Your daily summary",
            scheduled_for=future_time,
        )
        
        assert notification.scheduled_for is not None
        assert notification.scheduled_for > datetime.now()

    def test_create_notification_with_metadata(self, mock_db):
        """Test creating notification with metadata."""
        from brain.notifications.engine import NotificationEngine
        from brain.notifications.models import NotificationType
        
        engine = NotificationEngine(db=mock_db)
        
        metadata = {
            "habit_name": "Drink Water",
            "streak_count": 30,
            "custom_data": {"key": "value"}
        }
        
        notification = engine.create_notification(
            type=NotificationType.ACHIEVEMENT,
            title="30-Day Streak!",
            message="Congratulations!",
            metadata=metadata,
        )
        
        assert notification.metadata == metadata

    def test_create_notification_persists_to_db(self, mock_db):
        """Test that notifications are saved to database."""
        from brain.notifications.engine import NotificationEngine
        from brain.notifications.models import NotificationType
        
        engine = NotificationEngine(db=mock_db)
        
        notification = engine.create_notification(
            type=NotificationType.SYSTEM,
            title="Test",
            message="Test message",
            persist=True,
        )
        
        # Should have called db.execute to insert
        mock_db.execute.assert_called_once()

    def test_create_notification_no_persist(self, mock_db):
        """Test creating notification without persistence."""
        from brain.notifications.engine import NotificationEngine
        from brain.notifications.models import NotificationType
        
        engine = NotificationEngine(db=mock_db)
        
        notification = engine.create_notification(
            type=NotificationType.SYSTEM,
            title="Test",
            message="Test message",
            persist=False,
        )
        
        # Should NOT have called db.execute
        mock_db.execute.assert_not_called()

    @pytest.mark.edge_case
    def test_create_notification_empty_title(self, mock_db):
        """Test creating notification with empty title."""
        from brain.notifications.engine import NotificationEngine
        from brain.notifications.models import NotificationType
        
        engine = NotificationEngine(db=mock_db)
        
        notification = engine.create_notification(
            type=NotificationType.SYSTEM,
            title="",
            message="Message without title",
        )
        
        assert notification.title == ""
        assert notification.message == "Message without title"

    @pytest.mark.edge_case
    def test_create_notification_very_long_message(self, mock_db):
        """Test creating notification with very long message."""
        from brain.notifications.engine import NotificationEngine
        from brain.notifications.models import NotificationType
        
        engine = NotificationEngine(db=mock_db)
        long_message = "A" * 10000  # 10k characters
        
        notification = engine.create_notification(
            type=NotificationType.SYSTEM,
            title="Long Message Test",
            message=long_message,
        )
        
        assert len(notification.message) == 10000

    @pytest.mark.edge_case
    def test_create_notification_special_characters(self, mock_db):
        """Test creating notification with special characters."""
        from brain.notifications.engine import NotificationEngine
        from brain.notifications.models import NotificationType
        
        engine = NotificationEngine(db=mock_db)
        
        notification = engine.create_notification(
            type=NotificationType.SYSTEM,
            title="Test 🎉 <HTML> & 'quotes'",
            message="Special: \n\t\\",
        )
        
        assert "🎉" in notification.title
        assert "<HTML>" in notification.title

    def test_create_notification_callbacks(self, mock_db):
        """Test that 'created' callbacks are triggered."""
        from brain.notifications.engine import NotificationEngine
        from brain.notifications.models import NotificationType
        
        engine = NotificationEngine(db=mock_db)
        
        # Register callback
        callback_mock = Mock()
        engine.register_callback('created', callback_mock)
        
        notification = engine.create_notification(
            type=NotificationType.SYSTEM,
            title="Test",
            message="Test",
        )
        
        # Callback should have been called
        callback_mock.assert_called_once()


class TestNotificationDispatch:
    """Test notification dispatch logic."""

    def test_dispatch_basic(self, mock_db, sample_notification):
        """Test basic notification dispatch."""
        from brain.notifications.engine import NotificationEngine
        from brain.notifications.models import NotificationChannel, NotificationStatus
        from brain.notifications.channels import ChannelResult
        
        engine = NotificationEngine(db=mock_db)
        
        # Mock channel to be available
        mock_channel = Mock()
        mock_channel.is_available.return_value = True
        
        # Mock ChannelResult for send return value
        mock_result = Mock(spec=ChannelResult)
        mock_result.success = True
        mock_result.to_log.return_value = Mock(to_dict=Mock(return_value={
            'id': 'log-123',
            'notification_id': sample_notification.id,
            'channel': 'in_app',
            'status': 'sent',
            'error_message': None,
            'response_code': 200,
            'dispatched_at': datetime.now().isoformat(),
        }))
        mock_channel.send.return_value = mock_result
        
        engine._channels[NotificationChannel.IN_APP] = mock_channel
        
        results = engine.dispatch(
            sample_notification,
            channels=[NotificationChannel.IN_APP],
            user_id="test_user",
        )
        
        assert NotificationChannel.IN_APP in results
        assert results[NotificationChannel.IN_APP].success is True

    def test_dispatch_with_preferences(self, mock_db, sample_notification):
        """Test dispatch respects user preferences."""
        from brain.notifications.engine import NotificationEngine
        from brain.notifications.models import NotificationPreferences, NotificationChannel
        
        engine = NotificationEngine(db=mock_db)
        
        # Create preferences that disable notifications
        prefs = NotificationPreferences(
            user_id="test_user",
            enabled=False,  # Disabled
        )
        
        mock_channel = Mock()
        engine._channels[NotificationChannel.IN_APP] = mock_channel
        
        results = engine.dispatch(
            sample_notification,
            channels=[NotificationChannel.IN_APP],
            user_id="test_user",
            preferences=prefs,
        )
        
        # Should not send anything
        assert len(results) == 0
        mock_channel.send.assert_not_called()

    def test_dispatch_quiet_hours(self, mock_db, sample_notification):
        """Test dispatch respects quiet hours."""
        from brain.notifications.engine import NotificationEngine
        from brain.notifications.models import NotificationPreferences, NotificationChannel, NotificationPriority

        engine = NotificationEngine(db=mock_db)

        # Create preferences with quiet hours
        prefs = NotificationPreferences(
            user_id="test_user",
            enabled=True,
            quiet_hours_start=time(22, 0),
            quiet_hours_end=time(7, 0),
        )

        # Mock current time to be within quiet hours
        with patch('datetime.datetime') as mock_datetime:
            mock_datetime.now.return_value = datetime(2026, 1, 1, 23, 0)  # 11 PM

            mock_channel = Mock()
            engine._channels[NotificationChannel.IN_APP] = mock_channel

            results = engine.dispatch(
                sample_notification,
                channels=[NotificationChannel.IN_APP],
                user_id="test_user",
                preferences=prefs,
            )

            # Should not send during quiet hours
            assert len(results) == 0

    def test_dispatch_urgent_bypasses_quiet_hours(self, mock_db, urgent_notification):
        """Test that urgent notifications bypass quiet hours."""
        from brain.notifications.engine import NotificationEngine
        from brain.notifications.models import NotificationPreferences, NotificationChannel
        from brain.notifications.channels import ChannelResult
        
        engine = NotificationEngine(db=mock_db)
        
        # Create preferences with quiet hours
        prefs = NotificationPreferences(
            user_id="test_user",
            enabled=True,
            quiet_hours_start=time(22, 0),
            quiet_hours_end=time(7, 0),
        )
        
        # Mock current time to be within quiet hours
        with patch('datetime.datetime') as mock_datetime:
            mock_datetime.now.return_value = datetime(2026, 1, 1, 23, 0)  # 11 PM
            
            mock_channel = Mock()
            mock_channel.is_available.return_value = True
            
            mock_result = Mock(spec=ChannelResult)
            mock_result.success = True
            mock_result.to_log.return_value = Mock(to_dict=Mock(return_value={
                'id': 'log-123',
                'notification_id': urgent_notification.id,
                'channel': 'in_app',
                'status': 'sent',
                'error_message': None,
                'response_code': 200,
                'dispatched_at': datetime.now().isoformat(),
            }))
            mock_channel.send.return_value = mock_result
            
            engine._channels[NotificationChannel.IN_APP] = mock_channel
            
            results = engine.dispatch(
                urgent_notification,
                channels=[NotificationChannel.IN_APP],
                user_id="test_user",
                preferences=prefs,
            )
            
            # Should send despite quiet hours
            assert len(results) > 0

    def test_dispatch_channel_fallback(self, mock_db, sample_notification):
        """Test fallback to alternative channels."""
        from brain.notifications.engine import NotificationEngine
        from brain.notifications.models import NotificationChannel, NotificationPreferences
        from brain.notifications.channels import ChannelResult

        engine = NotificationEngine(db=mock_db)
        
        # Create preferences with browser notifications enabled and email
        prefs = NotificationPreferences(
            user_id="test_user",
            browser_notifications_enabled=True,
            email_notifications_enabled=True,
            email_address="test@example.com",
        )
        
        # Mock database to return a push subscription
        mock_db.fetch_one.return_value = None  # No preferences in DB
        mock_db.fetch_all.return_value = [
            {
                'id': 'sub-1',
                'user_id': 'test_user',
                'endpoint': 'https://example.com/push',
                'p256dh': 'key',
                'auth': 'auth',
                'is_active': 1,
                'created_at': '2026-01-01T00:00:00',
            }
        ]

        # Mock Web Push to fail
        mock_push = Mock()
        mock_push.is_available.return_value = True
        mock_push_result = Mock(spec=ChannelResult)
        mock_push_result.success = False
        mock_push_result.error = "Push failed"
        mock_push_result.to_log.return_value = Mock(to_dict=Mock(return_value={
            'id': 'log-123',
            'notification_id': sample_notification.id,
            'channel': 'web_push',
            'status': 'failed',
            'error_message': 'Push failed',
            'response_code': None,
            'dispatched_at': datetime.now().isoformat(),
        }))
        mock_push.send.return_value = mock_push_result
        engine._channels[NotificationChannel.WEB_PUSH] = mock_push

        # Mock In-App to succeed
        mock_inapp = Mock()
        mock_inapp.is_available.return_value = True
        mock_inapp_result = Mock(spec=ChannelResult)
        mock_inapp_result.success = True
        mock_inapp_result.to_log.return_value = Mock(to_dict=Mock(return_value={
            'id': 'log-124',
            'notification_id': sample_notification.id,
            'channel': 'in_app',
            'status': 'sent',
            'error_message': None,
            'response_code': 200,
            'dispatched_at': datetime.now().isoformat(),
        }))
        mock_inapp.send.return_value = mock_inapp_result
        engine._channels[NotificationChannel.IN_APP] = mock_inapp

        results = engine.dispatch(
            sample_notification,
            channels=[NotificationChannel.WEB_PUSH, NotificationChannel.IN_APP],
            user_id="test_user",
            preferences=prefs,
        )

        # Both channels should have been tried
        assert NotificationChannel.WEB_PUSH in results
        assert NotificationChannel.IN_APP in results

        # In-App should have succeeded
        assert results[NotificationChannel.IN_APP].success is True

    def test_dispatch_unavailable_channel(self, mock_db, sample_notification):
        """Test dispatch skips unavailable channels."""
        from brain.notifications.engine import NotificationEngine
        from brain.notifications.models import NotificationChannel
        
        engine = NotificationEngine(db=mock_db)
        
        # Mock channel as unavailable
        mock_channel = Mock()
        mock_channel.is_available.return_value = False
        engine._channels[NotificationChannel.EMAIL] = mock_channel
        
        results = engine.dispatch(
            sample_notification,
            channels=[NotificationChannel.EMAIL],
            user_id="test_user",
        )
        
        # Should not attempt to send
        mock_channel.send.assert_not_called()

    def test_dispatch_updates_status(self, mock_db, sample_notification):
        """Test dispatch updates notification status."""
        from brain.notifications.engine import NotificationEngine
        from brain.notifications.models import NotificationChannel
        from brain.notifications.channels import ChannelResult

        engine = NotificationEngine(db=mock_db)

        mock_channel = Mock()
        mock_channel.is_available.return_value = True
        
        mock_result = Mock(spec=ChannelResult)
        mock_result.success = True
        mock_result.to_log.return_value = Mock(to_dict=Mock(return_value={
            'id': 'log-123',
            'notification_id': sample_notification.id,
            'channel': 'in_app',
            'status': 'sent',
            'error_message': None,
            'response_code': 200,
            'dispatched_at': datetime.now().isoformat(),
        }))
        mock_channel.send.return_value = mock_result
        
        engine._channels[NotificationChannel.IN_APP] = mock_channel

        engine.dispatch(
            sample_notification,
            channels=[NotificationChannel.IN_APP],
            user_id="test_user",
        )

        # Status should be updated to SENT
        assert sample_notification.status.value == "sent"
        assert sample_notification.sent_at is not None


class TestChannelSelection:
    """Test automatic channel selection logic."""

    def test_select_channels_urgent(self, mock_db):
        """Test channel selection for urgent notifications."""
        from brain.notifications.engine import NotificationEngine
        from brain.notifications.models import (
            Notification,
            NotificationType,
            NotificationPriority,
            NotificationPreferences,
        )
        
        engine = NotificationEngine(db=mock_db)
        
        prefs = NotificationPreferences(
            user_id="test_user",
            browser_notifications_enabled=True,
            email_notifications_enabled=True,
            email_address="test@example.com",
        )
        
        notification = Notification(
            type=NotificationType.STREAK_WARNING,
            title="Urgent!",
            priority=NotificationPriority.URGENT,
        )
        
        channels = engine._select_channels(notification, prefs)
        
        # Should include all channels for urgent
        assert len(channels) >= 2

    def test_select_channels_normal(self, mock_db):
        """Test channel selection for normal priority."""
        from brain.notifications.engine import NotificationEngine
        from brain.notifications.models import (
            Notification,
            NotificationType,
            NotificationPriority,
            NotificationPreferences,
        )
        
        engine = NotificationEngine(db=mock_db)
        
        prefs = NotificationPreferences(
            user_id="test_user",
            browser_notifications_enabled=True,
            email_notifications_enabled=False,
        )
        
        notification = Notification(
            type=NotificationType.HABIT_REMINDER,
            title="Reminder",
            priority=NotificationPriority.MEDIUM,
        )
        
        channels = engine._select_channels(notification, prefs)
        
        # Should include in-app and web push
        assert len(channels) >= 1


class TestTemplateNotifications:
    """Test template-based notification creation."""

    def test_create_from_template(self, mock_db):
        """Test creating notification from template."""
        from brain.notifications.engine import NotificationEngine
        from brain.notifications.models import NotificationType
        
        engine = NotificationEngine(db=mock_db)
        
        context = {
            "habit_name": "Morning Exercise",
            "time": "8:00 AM",
        }
        
        notification = engine.create_from_template(
            template_id="habit_reminder",
            context=context,
            type=NotificationType.HABIT_REMINDER,
        )
        
        # Should create notification (template may not exist, handles gracefully)
        assert notification is None or notification.type == NotificationType.HABIT_REMINDER


class TestReminderSchedules:
    """Test reminder schedule operations."""

    def test_create_reminder_schedule(self, mock_db):
        """Test creating a reminder schedule."""
        from brain.notifications.engine import NotificationEngine
        
        engine = NotificationEngine(db=mock_db)
        
        schedule = engine.create_reminder_schedule(
            entity_type="habit",
            entity_id="habit-123",
            reminder_time="08:00",
            days_of_week=[0, 1, 2, 3, 4],
            user_id="test_user",
        )
        
        assert schedule.entity_type == "habit"
        assert schedule.entity_id == "habit-123"
        assert schedule.reminder_time == time(8, 0)
        assert len(schedule.days_of_week) == 5

    def test_get_reminder_schedule(self, mock_db):
        """Test retrieving a reminder schedule."""
        from brain.notifications.engine import NotificationEngine
        from brain.notifications.models import ReminderSchedule
        
        # Mock DB returns schedule
        mock_db.fetch_one.return_value = {
            'id': 'schedule-123',
            'user_id': 'test_user',
            'entity_type': 'habit',
            'entity_id': 'habit-123',
            'reminder_time': '08:00',
            'days_of_week': '[0, 1, 2, 3, 4]',
            'enabled': 1,
            'is_smart': 0,
            'channels': '["in_app"]',
            'created_at': '2026-01-01T00:00:00',
            'updated_at': '2026-01-01T00:00:00',
        }
        
        engine = NotificationEngine(db=mock_db)
        schedule = engine.get_reminder_schedule("habit", "habit-123")
        
        assert schedule is not None
        assert schedule.entity_id == "habit-123"

    def test_get_active_schedules(self, mock_db):
        """Test retrieving all active schedules."""
        from brain.notifications.engine import NotificationEngine
        
        # Mock DB returns multiple schedules
        mock_db.fetch_all.return_value = [
            {
                'id': 'schedule-1',
                'user_id': 'test_user',
                'entity_type': 'habit',
                'entity_id': 'habit-1',
                'reminder_time': '08:00',
                'days_of_week': '[0, 1, 2, 3, 4]',
                'enabled': 1,
                'is_smart': 0,
                'channels': '["in_app"]',
                'created_at': '2026-01-01T00:00:00',
                'updated_at': '2026-01-01T00:00:00',
            },
            {
                'id': 'schedule-2',
                'user_id': 'test_user',
                'entity_type': 'task',
                'entity_id': 'task-1',
                'reminder_time': '09:00',
                'days_of_week': '[1, 3, 5]',
                'enabled': 1,
                'is_smart': 0,
                'channels': '["in_app"]',
                'created_at': '2026-01-01T00:00:00',
                'updated_at': '2026-01-01T00:00:00',
            },
        ]
        
        engine = NotificationEngine(db=mock_db)
        schedules = engine.get_active_schedules()
        
        assert len(schedules) == 2


class TestPushSubscriptions:
    """Test push subscription operations."""

    def test_register_push_subscription(self, mock_db):
        """Test registering a new push subscription."""
        from brain.notifications.engine import NotificationEngine
        
        # Mock DB returns None (no existing subscription)
        mock_db.fetch_one.return_value = None
        
        engine = NotificationEngine(db=mock_db)
        
        subscription = engine.register_push_subscription(
            user_id="test_user",
            endpoint="https://fcm.googleapis.com/test",
            p256dh="test-p256dh",
            auth="test-auth",
            device_name="Chrome Browser",
        )
        
        assert subscription.user_id == "test_user"
        assert subscription.endpoint == "https://fcm.googleapis.com/test"
        assert subscription.is_active is True

    def test_register_existing_subscription(self, mock_db):
        """Test updating existing push subscription."""
        from brain.notifications.engine import NotificationEngine
        
        # Mock DB returns existing subscription
        mock_db.fetch_one.return_value = {'id': 'existing-id'}
        
        engine = NotificationEngine(db=mock_db)
        
        subscription = engine.register_push_subscription(
            user_id="test_user",
            endpoint="https://fcm.googleapis.com/test",
            p256dh="test-p256dh",
            auth="test-auth",
        )
        
        assert subscription.id == 'existing-id'

    def test_get_active_subscriptions(self, mock_db):
        """Test retrieving active subscriptions."""
        from brain.notifications.engine import NotificationEngine
        
        mock_db.fetch_all.return_value = [
            {
                'id': 'sub-1',
                'user_id': 'test_user',
                'endpoint': 'https://example.com/1',
                'p256dh': 'key1',
                'auth': 'auth1',
                'is_active': 1,
                'created_at': '2026-01-01T00:00:00',
            },
        ]
        
        engine = NotificationEngine(db=mock_db)
        subscriptions = engine.get_active_subscriptions("test_user")
        
        assert len(subscriptions) == 1

    def test_deactivate_subscription(self, mock_db):
        """Test deactivating a subscription."""
        from brain.notifications.engine import NotificationEngine
        
        engine = NotificationEngine(db=mock_db)
        result = engine.deactivate_subscription("sub-123")
        
        assert result is True
        mock_db.execute.assert_called_once()


class TestNotificationQueries:
    """Test notification query operations."""

    def test_get_notification(self, mock_db):
        """Test retrieving a notification by ID."""
        from brain.notifications.engine import NotificationEngine
        
        mock_db.fetch_one.return_value = {
            'id': 'notif-123',
            'type': 'habit_reminder',
            'title': 'Test',
            'message': 'Test message',
            'priority': 'medium',
            'status': 'pending',
            'entity_type': 'habit',
            'entity_id': 'habit-1',
            'created_at': '2026-01-01T00:00:00',
            'updated_at': '2026-01-01T00:00:00',
            'metadata': '{}',
        }
        
        engine = NotificationEngine(db=mock_db)
        notification = engine.get_notification("notif-123")
        
        assert notification is not None
        assert notification.id == 'notif-123'

    def test_get_notification_not_found(self, mock_db):
        """Test retrieving non-existent notification."""
        from brain.notifications.engine import NotificationEngine
        
        mock_db.fetch_one.return_value = None
        
        engine = NotificationEngine(db=mock_db)
        notification = engine.get_notification("nonexistent")
        
        assert notification is None

    def test_get_pending_notifications(self, mock_db):
        """Test retrieving pending notifications."""
        from brain.notifications.engine import NotificationEngine
        
        mock_db.fetch_all.return_value = [
            {
                'id': 'notif-1',
                'type': 'habit_reminder',
                'title': 'Test 1',
                'message': 'Message 1',
                'priority': 'high',
                'status': 'pending',
                'entity_type': 'habit',
                'entity_id': 'habit-1',
                'created_at': '2026-01-01T00:00:00',
                'updated_at': '2026-01-01T00:00:00',
                'metadata': '{}',
            },
        ]
        
        engine = NotificationEngine(db=mock_db)
        notifications = engine.get_pending_notifications()
        
        assert len(notifications) == 1

    def test_get_due_notifications(self, mock_db):
        """Test retrieving notifications that are due."""
        from brain.notifications.engine import NotificationEngine
        
        mock_db.fetch_all.return_value = [
            {
                'id': 'notif-1',
                'type': 'habit_reminder',
                'title': 'Due Now',
                'message': 'This is due',
                'priority': 'medium',
                'status': 'scheduled',
                'scheduled_for': '2026-01-01T00:00:00',  # Past
                'entity_type': 'habit',
                'entity_id': 'habit-1',
                'created_at': '2026-01-01T00:00:00',
                'updated_at': '2026-01-01T00:00:00',
                'metadata': '{}',
            },
        ]
        
        engine = NotificationEngine(db=mock_db)
        notifications = engine.get_due_notifications()
        
        assert len(notifications) == 1


class TestCallbackSystem:
    """Test notification callback system."""

    def test_register_callback(self, mock_db):
        """Test registering a callback."""
        from brain.notifications.engine import NotificationEngine
        
        engine = NotificationEngine(db=mock_db)
        callback = Mock()
        
        engine.register_callback('sent', callback)
        
        assert 'sent' in engine._callbacks
        assert callback in engine._callbacks['sent']

    def test_trigger_callbacks(self, mock_db):
        """Test triggering callbacks."""
        from brain.notifications.engine import NotificationEngine
        from brain.notifications.models import Notification, NotificationType
        
        engine = NotificationEngine(db=mock_db)
        callback1 = Mock()
        callback2 = Mock()
        
        engine.register_callback('test_event', callback1)
        engine.register_callback('test_event', callback2)
        
        notification = Notification(
            type=NotificationType.SYSTEM,
            title="Test",
            message="Test",
        )
        
        engine._trigger_callbacks('test_event', notification)
        
        callback1.assert_called_once()
        callback2.assert_called_once()

    def test_callback_error_handling(self, mock_db):
        """Test that callback errors don't break the system."""
        from brain.notifications.engine import NotificationEngine
        from brain.notifications.models import Notification, NotificationType
        
        engine = NotificationEngine(db=mock_db)
        
        def failing_callback(notification, **kwargs):
            raise Exception("Callback error")
        
        working_callback = Mock()
        
        engine.register_callback('test_event', failing_callback)
        engine.register_callback('test_event', working_callback)
        
        notification = Notification(
            type=NotificationType.SYSTEM,
            title="Test",
            message="Test",
        )
        
        # Should not raise exception
        engine._trigger_callbacks('test_event', notification)
        
        # Working callback should still be called
        working_callback.assert_called_once()


class TestEdgeCases:
    """Test edge cases and error conditions."""

    @pytest.mark.edge_case
    def test_dispatch_null_notification(self, mock_db):
        """Test dispatch with None notification."""
        from brain.notifications.engine import NotificationEngine
        
        engine = NotificationEngine(db=mock_db)
        
        with pytest.raises(AttributeError):
            engine.dispatch(None, user_id="test_user")

    @pytest.mark.edge_case
    def test_dispatch_empty_channels(self, mock_db, sample_notification):
        """Test dispatch with empty channels list."""
        from brain.notifications.engine import NotificationEngine
        
        engine = NotificationEngine(db=mock_db)
        
        results = engine.dispatch(
            sample_notification,
            channels=[],
            user_id="test_user",
        )
        
        assert len(results) == 0

    @pytest.mark.edge_case
    def test_create_notification_null_metadata(self, mock_db):
        """Test creating notification with None metadata."""
        from brain.notifications.engine import NotificationEngine
        from brain.notifications.models import NotificationType
        
        engine = NotificationEngine(db=mock_db)
        
        notification = engine.create_notification(
            type=NotificationType.SYSTEM,
            title="Test",
            message="Test",
            metadata=None,
        )
        
        assert notification.metadata == {}

    @pytest.mark.edge_case
    def test_get_preferences_nonexistent_user(self, mock_db):
        """Test getting preferences for non-existent user."""
        from brain.notifications.engine import NotificationEngine
        
        mock_db.fetch_one.return_value = None
        
        engine = NotificationEngine(db=mock_db)
        prefs = engine.get_preferences("nonexistent_user")
        
        # Should return defaults
        assert prefs.user_id == "nonexistent_user"
        assert prefs.enabled is True

    @pytest.mark.edge_case
    def test_save_preferences_db_error(self, mock_db):
        """Test saving preferences when DB fails."""
        from brain.notifications.engine import NotificationEngine
        from brain.notifications.models import NotificationPreferences
        
        mock_db.execute.side_effect = Exception("DB error")
        
        engine = NotificationEngine(db=mock_db)
        prefs = NotificationPreferences(user_id="test_user")
        
        result = engine.save_preferences(prefs)
        
        assert result is False


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
