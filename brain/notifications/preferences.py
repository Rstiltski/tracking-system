"""
Notification Preferences Manager

Implements preference management with decision logic for notifications.
Handles global toggles, quiet hours, per-type settings, and channel preferences.

Phase 4.4 Feature: User Preference Management

Decision Hierarchy:
1. Global Toggle - If disabled, no notifications
2. Channel Check - If channel disabled, skip
3. Type Check - If notification type disabled, skip
4. Quiet Hours - If within quiet hours, skip (unless urgent)

Reference:
- Phase 4.4 Research Document: Notification Settings UI
- PROJECT_RULES.md: Singleton pattern for Streamlit compatibility
"""

from datetime import datetime, time
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field
import logging
import threading

from brain.notifications.models import (
    NotificationPreferences,
    NotificationType,
    NotificationChannel,
    NotificationPriority,
)

logger = logging.getLogger(__name__)


class PreferenceManager:
    """
    Manages user notification preferences.
    
    Provides a clean API for:
    - Getting/setting user preferences
    - Decision logic for notification delivery
    - Quiet hours calculations
    - Test notification functionality
    
    Singleton pattern for Streamlit compatibility.
    
    Example:
        pm = PreferenceManager()
        
        # Check if notification should be sent
        if pm.should_notify(user_id, 'habit', 'email'):
            send_notification()
        
        # Update preferences
        prefs = pm.get_user_preferences(user_id)
        prefs.quiet_hours_start = time(22, 0)
        pm.save_preferences(prefs)
    """
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls, *args, **kwargs):
        """Singleton pattern for Streamlit compatibility."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self, db=None):
        """Initialize preference manager."""
        # Prevent re-initialization
        if hasattr(self, '_initialized') and self._initialized:
            return
        
        self._db = db
        self._initialized = True
    
    @property
    def db(self):
        """Get database instance."""
        if self._db is None:
            from tracking_app.database import get_db
            self._db = get_db()
        return self._db
    
    # ==========================================
    # Preference Retrieval
    # ==========================================
    
    def get_user_preferences(self, user_id: str = "default") -> NotificationPreferences:
        """
        Get notification preferences for a user.
        
        Args:
            user_id: User ID to get preferences for
            
        Returns:
            NotificationPreferences instance (defaults if not found)
        """
        row = self.db.fetch_one(
            "SELECT * FROM notification_preferences WHERE user_id = ?",
            (user_id,)
        )
        
        if row:
            return NotificationPreferences.from_dict(row)
        
        # Return default preferences
        return NotificationPreferences(user_id=user_id)
    
    def save_preferences(self, preferences: NotificationPreferences) -> bool:
        """
        Save notification preferences.
        
        Args:
            preferences: NotificationPreferences to save
            
        Returns:
            True if saved successfully
        """
        try:
            data = preferences.to_dict()
            
            self.db.execute(
                """INSERT OR REPLACE INTO notification_preferences 
                   (user_id, enabled, quiet_hours_start, quiet_hours_end,
                    default_sound, vibration_enabled, habit_reminders_enabled,
                    task_reminders_enabled, goal_reminders_enabled,
                    achievement_notifications_enabled, streak_warnings_enabled,
                    daily_digest_enabled, browser_notifications_enabled,
                    email_notifications_enabled, email_address,
                    smart_scheduling_enabled, min_reminder_lead_minutes,
                    created_at, updated_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    data['user_id'], data['enabled'], data['quiet_hours_start'],
                    data['quiet_hours_end'], data['default_sound'],
                    data['vibration_enabled'], data['habit_reminders_enabled'],
                    data['task_reminders_enabled'], data['goal_reminders_enabled'],
                    data['achievement_notifications_enabled'],
                    data['streak_warnings_enabled'], data['daily_digest_enabled'],
                    data['browser_notifications_enabled'],
                    data['email_notifications_enabled'], data['email_address'],
                    data['smart_scheduling_enabled'], data['min_reminder_lead_minutes'],
                    data['created_at'], data['updated_at']
                )
            )
            
            logger.info(f"Saved preferences for user {preferences.user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save preferences: {e}")
            return False
    
    # ==========================================
    # Decision Logic
    # ==========================================
    
    def should_notify(
        self,
        user_id: str,
        notification_type: NotificationType,
        channel: NotificationChannel,
        priority: NotificationPriority = NotificationPriority.MEDIUM
    ) -> bool:
        """
        Decision engine for allowing notifications.
        
        Checks in order:
        1. Global toggle
        2. Channel enabled
        3. Notification type enabled
        4. Quiet hours (skipped for urgent)
        
        Args:
            user_id: User ID to check
            notification_type: Type of notification
            channel: Delivery channel
            priority: Notification priority
            
        Returns:
            True if notification should be sent
        """
        prefs = self.get_user_preferences(user_id)
        
        # 1. Global Check
        if not prefs.enabled:
            logger.debug(f"Notifications disabled globally for user {user_id}")
            return False
        
        # 2. Channel Check
        if not self._is_channel_enabled(prefs, channel):
            logger.debug(f"Channel {channel} disabled for user {user_id}")
            return False
        
        # 3. Type Check
        if not prefs.is_type_enabled(notification_type):
            logger.debug(f"Type {notification_type} disabled for user {user_id}")
            return False
        
        # 4. Quiet Hours Check (skip for urgent)
        if priority != NotificationPriority.URGENT and prefs.is_quiet_hours():
            logger.debug(f"Quiet hours active for user {user_id}")
            return False
        
        return True
    
    def _is_channel_enabled(
        self,
        prefs: NotificationPreferences,
        channel: NotificationChannel
    ) -> bool:
        """Check if a channel is enabled in preferences."""
        channel_mapping = {
            NotificationChannel.IN_APP: True,  # In-app always enabled
            NotificationChannel.WEB_PUSH: prefs.browser_notifications_enabled,
            NotificationChannel.EMAIL: prefs.email_notifications_enabled,
            NotificationChannel.DESKTOP: prefs.browser_notifications_enabled,
        }
        return channel_mapping.get(channel, True)
    
    # ==========================================
    # Quiet Hours Helpers
    # ==========================================
    
    def is_quiet_hours(self, user_id: str = "default") -> bool:
        """
        Check if current time is within quiet hours.
        
        Args:
            user_id: User ID to check
            
        Returns:
            True if within quiet hours
        """
        prefs = self.get_user_preferences(user_id)
        return prefs.is_quiet_hours()
    
    def get_quiet_hours_status(self, user_id: str = "default") -> Dict[str, Any]:
        """
        Get detailed quiet hours status.
        
        Args:
            user_id: User ID to check
            
        Returns:
            Dict with quiet hours details
        """
        prefs = self.get_user_preferences(user_id)
        
        return {
            'is_quiet_hours': prefs.is_quiet_hours(),
            'quiet_hours_start': prefs.quiet_hours_start,
            'quiet_hours_end': prefs.quiet_hours_end,
            'current_time': datetime.now().time(),
            'enabled': prefs.quiet_hours_start is not None,
        }
    
    # ==========================================
    # Type-Specific Settings
    # ==========================================
    
    def get_enabled_types(self, user_id: str = "default") -> Dict[str, bool]:
        """
        Get all notification type enable/disable states.
        
        Args:
            user_id: User ID to check
            
        Returns:
            Dict mapping type names to enabled states
        """
        prefs = self.get_user_preferences(user_id)
        
        return {
            'habit': prefs.habit_reminders_enabled,
            'task': prefs.task_reminders_enabled,
            'goal': prefs.goal_reminders_enabled,
            'achievement': prefs.achievement_notifications_enabled,
            'streak_warning': prefs.streak_warnings_enabled,
            'daily_digest': prefs.daily_digest_enabled,
        }
    
    def set_type_enabled(
        self,
        user_id: str,
        notification_type: str,
        enabled: bool
    ) -> bool:
        """
        Enable or disable a specific notification type.
        
        Args:
            user_id: User ID
            notification_type: Type name (habit, task, goal, etc.)
            enabled: Whether to enable
            
        Returns:
            True if updated successfully
        """
        prefs = self.get_user_preferences(user_id)
        
        type_mapping = {
            'habit': 'habit_reminders_enabled',
            'task': 'task_reminders_enabled',
            'goal': 'goal_reminders_enabled',
            'achievement': 'achievement_notifications_enabled',
            'streak_warning': 'streak_warnings_enabled',
            'daily_digest': 'daily_digest_enabled',
        }
        
        field_name = type_mapping.get(notification_type)
        if not field_name:
            logger.warning(f"Unknown notification type: {notification_type}")
            return False
        
        setattr(prefs, field_name, enabled)
        prefs.updated_at = datetime.now()
        
        return self.save_preferences(prefs)
    
    # ==========================================
    # Channel Settings
    # ==========================================
    
    def get_enabled_channels(self, user_id: str = "default") -> Dict[str, bool]:
        """
        Get all channel enable/disable states.
        
        Args:
            user_id: User ID to check
            
        Returns:
            Dict mapping channel names to enabled states
        """
        prefs = self.get_user_preferences(user_id)
        
        return {
            'browser': prefs.browser_notifications_enabled,
            'email': prefs.email_notifications_enabled,
        }
    
    def set_channel_enabled(
        self,
        user_id: str,
        channel: str,
        enabled: bool
    ) -> bool:
        """
        Enable or disable a specific channel.
        
        Args:
            user_id: User ID
            channel: Channel name (browser, email)
            enabled: Whether to enable
            
        Returns:
            True if updated successfully
        """
        prefs = self.get_user_preferences(user_id)
        
        channel_mapping = {
            'browser': 'browser_notifications_enabled',
            'email': 'email_notifications_enabled',
        }
        
        field_name = channel_mapping.get(channel)
        if not field_name:
            logger.warning(f"Unknown channel: {channel}")
            return False
        
        setattr(prefs, field_name, enabled)
        prefs.updated_at = datetime.now()
        
        return self.save_preferences(prefs)
    
    # ==========================================
    # Global Settings
    # ==========================================
    
    def set_global_enabled(self, user_id: str, enabled: bool) -> bool:
        """
        Enable or disable all notifications.
        
        Args:
            user_id: User ID
            enabled: Whether to enable
            
        Returns:
            True if updated successfully
        """
        prefs = self.get_user_preferences(user_id)
        prefs.enabled = enabled
        prefs.updated_at = datetime.now()
        
        return self.save_preferences(prefs)
    
    def set_quiet_hours(
        self,
        user_id: str,
        start_time: Optional[time],
        end_time: Optional[time]
    ) -> bool:
        """
        Set quiet hours window.
        
        Args:
            user_id: User ID
            start_time: Start of quiet hours (None to disable)
            end_time: End of quiet hours (None to disable)
            
        Returns:
            True if updated successfully
        """
        prefs = self.get_user_preferences(user_id)
        prefs.quiet_hours_start = start_time
        prefs.quiet_hours_end = end_time
        prefs.updated_at = datetime.now()
        
        return self.save_preferences(prefs)
    
    def set_email_address(self, user_id: str, email: Optional[str]) -> bool:
        """
        Set email address for notifications.
        
        Args:
            user_id: User ID
            email: Email address (None to clear)
            
        Returns:
            True if updated successfully
        """
        prefs = self.get_user_preferences(user_id)
        prefs.email_address = email
        prefs.updated_at = datetime.now()
        
        return self.save_preferences(prefs)
    
    # ==========================================
    # Test Notification
    # ==========================================
    
    def send_test_notification(
        self,
        user_id: str = "default",
        channel: Optional[NotificationChannel] = None
    ) -> Dict[str, Any]:
        """
        Send a test notification to verify settings.
        
        Args:
            user_id: User ID
            channel: Specific channel to test (None = all enabled)
            
        Returns:
            Dict with test results
        """
        from brain.notifications.engine import get_engine
        from brain.notifications.models import Notification
        
        engine = get_engine()
        prefs = self.get_user_preferences(user_id)
        
        # Create test notification
        notification = Notification(
            type=NotificationType.SYSTEM,
            title="🧪 Test Notification",
            message="This is a test notification to verify your settings are working correctly.",
            priority=NotificationPriority.MEDIUM,
            entity_type="test",
            entity_id="test_notification",
        )
        
        results = {}
        
        # Determine channels to test
        if channel:
            channels = [channel]
        else:
            channels = []
            if prefs.browser_notifications_enabled:
                channels.append(NotificationChannel.WEB_PUSH)
            if prefs.email_notifications_enabled and prefs.email_address:
                channels.append(NotificationChannel.EMAIL)
            channels.append(NotificationChannel.IN_APP)
        
        # Send via each channel
        for ch in channels:
            if self.should_notify(user_id, NotificationType.SYSTEM, ch):
                result = engine.dispatch(notification, channels=[ch], user_id=user_id)
                results[ch.value] = {
                    'sent': any(r.success for r in result.values()),
                    'details': {k: v.message for k, v in result.items()}
                }
            else:
                results[ch.value] = {
                    'sent': False,
                    'reason': 'Channel disabled or quiet hours'
                }
        
        return {
            'notification_id': notification.id,
            'channels_tested': list(results.keys()),
            'results': results,
            'success': any(r.get('sent', False) for r in results.values()),
        }
    
    # ==========================================
    # Notification History
    # ==========================================
    
    def get_notification_history(
        self,
        user_id: str = "default",
        limit: int = 50,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Get notification history for a user.
        
        Args:
            user_id: User ID
            limit: Maximum number of records
            offset: Offset for pagination
            
        Returns:
            List of notification records
        """
        # Join notifications with logs
        rows = self.db.fetch_all(
            """SELECT n.id, n.type, n.title, n.message, n.priority,
                      n.entity_type, n.entity_id, n.created_at, n.read,
                      nl.channel, nl.status as delivery_status
               FROM notifications n
               LEFT JOIN notification_logs nl ON n.id = nl.notification_id
               ORDER BY n.created_at DESC
               LIMIT ? OFFSET ?""",
            (limit, offset)
        )
        
        return rows
    
    def get_notification_stats(self, user_id: str = "default") -> Dict[str, Any]:
        """
        Get notification statistics for a user.
        
        Args:
            user_id: User ID
            
        Returns:
            Dict with statistics
        """
        # Total notifications
        total = self.db.fetch_one(
            "SELECT COUNT(*) as count FROM notifications"
        )
        
        # By status
        by_status = self.db.fetch_all(
            """SELECT status, COUNT(*) as count 
               FROM notification_logs 
               GROUP BY status"""
        )
        
        # By type
        by_type = self.db.fetch_all(
            """SELECT type, COUNT(*) as count 
               FROM notifications 
               GROUP BY type"""
        )
        
        # Unread count
        unread = self.db.fetch_one(
            "SELECT COUNT(*) as count FROM notifications WHERE read = 0"
        )
        
        return {
            'total_notifications': total['count'] if total else 0,
            'unread_count': unread['count'] if unread else 0,
            'by_status': {r['status']: r['count'] for r in by_status},
            'by_type': {r['notification_type']: r['count'] for r in by_type},
        }
    
    # ==========================================
    # Reset to Defaults
    # ==========================================
    
    def reset_to_defaults(self, user_id: str) -> bool:
        """
        Reset preferences to default values.
        
        Args:
            user_id: User ID
            
        Returns:
            True if reset successfully
        """
        defaults = NotificationPreferences(user_id=user_id)
        return self.save_preferences(defaults)


# Singleton getter
_preference_manager: Optional[PreferenceManager] = None
_preference_lock = threading.Lock()


def get_preference_manager() -> PreferenceManager:
    """Get the global PreferenceManager instance."""
    global _preference_manager
    
    if _preference_manager is None:
        with _preference_lock:
            if _preference_manager is None:
                _preference_manager = PreferenceManager()
    
    return _preference_manager