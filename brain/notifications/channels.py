"""
Notification Channels

Implements the Strategy Pattern for notification delivery.
Each channel (Web Push, Email, In-App) implements a common interface.

Reference:
- Phase 4.1 Research Document, Section 5: NotificationEngine Class
- PROJECT_RULES.md: Use Strategy Pattern for extensibility
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict, Any, Tuple
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from brain.notifications.models import (
    Notification,
    NotificationChannel,
    NotificationPriority,
    PushSubscription,
    NotificationLog,
)

logger = logging.getLogger(__name__)


@dataclass
class ChannelResult:
    """Result of a notification send attempt."""
    success: bool
    channel: NotificationChannel
    message: str = ""
    error: Optional[str] = None
    response_code: Optional[int] = None
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()
    
    def to_log(self, notification_id: str) -> NotificationLog:
        """Convert to a NotificationLog entry."""
        return NotificationLog(
            notification_id=notification_id,
            channel=self.channel,
            status="sent" if self.success else "failed",
            error_message=self.error,
            response_code=self.response_code,
            dispatched_at=self.timestamp,
        )


class NotificationChannelBase(ABC):
    """
    Abstract base class for notification channels.
    
    Implements the Strategy Pattern - each channel handles
    delivery in its own way but presents a common interface.
    """
    
    @property
    @abstractmethod
    def channel_type(self) -> NotificationChannel:
        """Return the channel type identifier."""
        pass
    
    @abstractmethod
    def send(
        self, 
        notification: Notification, 
        recipient: str,
        **kwargs
    ) -> ChannelResult:
        """
        Send a notification to a recipient.
        
        Args:
            notification: The notification to send
            recipient: Recipient identifier (email, subscription ID, etc.)
            **kwargs: Additional channel-specific parameters
            
        Returns:
            ChannelResult with success status and metadata
        """
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if this channel is properly configured and available."""
        pass


class InAppChannel(NotificationChannelBase):
    """
    In-app notification channel.
    
    Stores notifications in the database for display within the app.
    This is the fallback channel that always works.
    """
    
    @property
    def channel_type(self) -> NotificationChannel:
        return NotificationChannel.IN_APP
    
    def __init__(self, db=None):
        """
        Initialize in-app channel.
        
        Args:
            db: Database instance (optional, uses global if not provided)
        """
        self._db = db
    
    @property
    def db(self):
        """Get database instance."""
        if self._db is None:
            from tracking_app.database import get_db
            self._db = get_db()
        return self._db
    
    def send(
        self, 
        notification: Notification, 
        recipient: str = "default",
        **kwargs
    ) -> ChannelResult:
        """
        Store notification in database for in-app display.
        
        Args:
            notification: The notification to store
            recipient: User ID (not used for in-app, all notifications stored)
            
        Returns:
            ChannelResult indicating success
        """
        try:
            # Notification is already stored by the engine
            # This channel just marks it as available for in-app display
            logger.info(f"In-app notification stored: {notification.id}")
            
            return ChannelResult(
                success=True,
                channel=self.channel_type,
                message="Notification stored for in-app display",
            )
        except Exception as e:
            logger.error(f"Failed to store in-app notification: {e}")
            return ChannelResult(
                success=False,
                channel=self.channel_type,
                error=str(e),
            )
    
    def is_available(self) -> bool:
        """In-app channel is always available."""
        return True
    
    def get_unread(self, user_id: str, limit: int = 50) -> list:
        """
        Get unread notifications for a user.
        
        Args:
            user_id: User ID to get notifications for
            limit: Maximum number to return
            
        Returns:
            List of Notification objects
        """
        from brain.notifications.models import Notification
        
        rows = self.db.fetch_all(
            """SELECT * FROM notifications 
               WHERE read = 0 
               ORDER BY created_at DESC 
               LIMIT ?""",
            (limit,)
        )
        
        return [Notification.from_dict(row) for row in rows]
    
    def mark_read(self, notification_id: str) -> bool:
        """Mark a notification as read."""
        try:
            self.db.execute(
                """UPDATE notifications 
                   SET read = 1, updated_at = ? 
                   WHERE id = ?""",
                (datetime.now().isoformat(), notification_id)
            )
            return True
        except Exception as e:
            logger.error(f"Failed to mark notification as read: {e}")
            return False


class WebPushChannel(NotificationChannelBase):
    """
    Web Push notification channel.
    
    Sends push notifications to browsers via the Web Push API.
    Requires VAPID configuration.
    
    Reference:
    - Phase 4.1 Research Document, Section 5.2
    - Web Push API specification
    """
    
    @property
    def channel_type(self) -> NotificationChannel:
        return NotificationChannel.WEB_PUSH
    
    def __init__(
        self, 
        vapid_private_key: str = "",
        vapid_subject: str = "",
        db=None
    ):
        """
        Initialize Web Push channel.
        
        Args:
            vapid_private_key: VAPID private key for authentication
            vapid_subject: VAPID subject (mailto: or URL)
            db: Database instance
        """
        self._vapid_private_key = vapid_private_key
        self._vapid_subject = vapid_subject
        self._db = db
        self._pywebpush = None
    
    @property
    def db(self):
        """Get database instance."""
        if self._db is None:
            from tracking_app.database import get_db
            self._db = get_db()
        return self._db
    
    def _load_vapid_config(self) -> Tuple[str, str]:
        """Load VAPID configuration from database."""
        if self._vapid_private_key and self._vapid_subject:
            return self._vapid_private_key, self._vapid_subject
        
        # Try to load from database
        row = self.db.fetch_one(
            "SELECT private_key, subject FROM vapid_config WHERE id = 1"
        )
        
        if row:
            self._vapid_private_key = row['private_key']
            self._vapid_subject = row['subject']
        
        return self._vapid_private_key, self._vapid_subject
    
    def send(
        self, 
        notification: Notification, 
        recipient: str,
        **kwargs
    ) -> ChannelResult:
        """
        Send a Web Push notification.
        
        Args:
            notification: The notification to send
            recipient: PushSubscription ID or subscription info dict
            
        Returns:
            ChannelResult with success status
        """
        try:
            # Load VAPID config
            private_key, subject = self._load_vapid_config()
            
            if not private_key:
                return ChannelResult(
                    success=False,
                    channel=self.channel_type,
                    error="VAPID private key not configured",
                )
            
            # Get subscription info
            subscription_info = self._get_subscription_info(recipient)
            
            if not subscription_info:
                return ChannelResult(
                    success=False,
                    channel=self.channel_type,
                    error="Invalid or expired subscription",
                )
            
            # Lazy import pywebpush
            if self._pywebpush is None:
                try:
                    from pywebpush import webpush, WebPushException
                    self._pywebpush = webpush
                    self._WebPushException = WebPushException
                except ImportError:
                    return ChannelResult(
                        success=False,
                        channel=self.channel_type,
                        error="pywebpush not installed. Run: pip install pywebpush",
                    )
            
            # Prepare payload
            payload = {
                "title": notification.title,
                "body": notification.message,
                "icon": notification.metadata.get("icon", "/static/icon.png"),
                "badge": notification.metadata.get("badge", "/static/badge.png"),
                "tag": notification.id,
                "data": {
                    "url": notification.action_url,
                    "entity_type": notification.entity_type,
                    "entity_id": notification.entity_id,
                }
            }
            
            # Send push
            import json
            self._pywebpush(
                subscription_info=subscription_info,
                data=json.dumps(payload),
                vapid_private_key=private_key,
                vapid_claims={"sub": subject}
            )
            
            logger.info(f"Web Push sent: {notification.id}")
            
            return ChannelResult(
                success=True,
                channel=self.channel_type,
                message="Push notification sent",
            )
            
        except self._WebPushException as e:
            # Handle specific Web Push errors
            response_code = getattr(e.response, 'status_code', None) if hasattr(e, 'response') else None
            
            # 410 Gone means subscription is no longer valid
            if response_code == 410:
                self._deactivate_subscription(recipient)
                return ChannelResult(
                    success=False,
                    channel=self.channel_type,
                    error="Subscription expired (410 Gone)",
                    response_code=410,
                )
            
            # 429 Too Many Requests - rate limited
            if response_code == 429:
                return ChannelResult(
                    success=False,
                    channel=self.channel_type,
                    error="Rate limited (429 Too Many Requests)",
                    response_code=429,
                )
            
            logger.error(f"Web Push error: {e}")
            return ChannelResult(
                success=False,
                channel=self.channel_type,
                error=str(e),
                response_code=response_code,
            )
            
        except Exception as e:
            logger.error(f"Failed to send Web Push: {e}")
            return ChannelResult(
                success=False,
                channel=self.channel_type,
                error=str(e),
            )
    
    def _get_subscription_info(self, recipient: str) -> Optional[Dict[str, Any]]:
        """
        Get subscription info for a recipient.
        
        Args:
            recipient: Subscription ID or subscription info dict
            
        Returns:
            Subscription info dict or None if not found
        """
        # If recipient is already a dict with subscription info
        if isinstance(recipient, dict) and 'endpoint' in recipient:
            return recipient
        
        # If recipient is a PushSubscription object
        if isinstance(recipient, PushSubscription):
            return recipient.to_subscription_info()
        
        # Otherwise, look up by ID in database
        row = self.db.fetch_one(
            """SELECT endpoint, p256dh, auth 
               FROM push_subscriptions 
               WHERE id = ? AND is_active = 1""",
            (recipient,)
        )
        
        if row:
            return {
                "endpoint": row['endpoint'],
                "keys": {
                    "p256dh": row['p256dh'],
                    "auth": row['auth']
                }
            }
        
        return None
    
    def _deactivate_subscription(self, subscription_id: str) -> None:
        """Mark a subscription as inactive (e.g., after 410 Gone)."""
        try:
            self.db.execute(
                """UPDATE push_subscriptions 
                   SET is_active = 0 
                   WHERE id = ?""",
                (subscription_id,)
            )
            logger.info(f"Deactivated expired subscription: {subscription_id}")
        except Exception as e:
            logger.error(f"Failed to deactivate subscription: {e}")
    
    def is_available(self) -> bool:
        """Check if Web Push is properly configured."""
        private_key, subject = self._load_vapid_config()
        return bool(private_key and subject)
    
    def get_active_subscriptions(self, user_id: str) -> list:
        """
        Get all active push subscriptions for a user.
        
        Args:
            user_id: User ID to get subscriptions for
            
        Returns:
            List of PushSubscription objects
        """
        rows = self.db.fetch_all(
            """SELECT * FROM push_subscriptions 
               WHERE user_id = ? AND is_active = 1""",
            (user_id,)
        )
        
        return [PushSubscription.from_dict(row) for row in rows]


class EmailChannel(NotificationChannelBase):
    """
    Email notification channel.
    
    Sends notifications via SMTP.
    Used as fallback for high-priority notifications.
    
    Reference:
    - Phase 4.1 Research Document, Section 5.3
    """
    
    @property
    def channel_type(self) -> NotificationChannel:
        return NotificationChannel.EMAIL
    
    def __init__(
        self,
        smtp_host: str = "localhost",
        smtp_port: int = 587,
        smtp_user: str = "",
        smtp_password: str = "",
        from_address: str = "notifications@example.com",
        use_tls: bool = True,
        db=None
    ):
        """
        Initialize Email channel.
        
        Args:
            smtp_host: SMTP server hostname
            smtp_port: SMTP server port
            smtp_user: SMTP authentication username
            smtp_password: SMTP authentication password
            from_address: Email address to send from
            use_tls: Whether to use TLS
            db: Database instance
        """
        self._smtp_host = smtp_host
        self._smtp_port = smtp_port
        self._smtp_user = smtp_user
        self._smtp_password = smtp_password
        self._from_address = from_address
        self._use_tls = use_tls
        self._db = db
    
    @property
    def db(self):
        """Get database instance."""
        if self._db is None:
            from tracking_app.database import get_db
            self._db = get_db()
        return self._db
    
    def _load_smtp_config(self) -> Dict[str, Any]:
        """Load SMTP configuration from environment or database."""
        import os
        
        return {
            "host": os.environ.get("SMTP_HOST", self._smtp_host),
            "port": int(os.environ.get("SMTP_PORT", self._smtp_port)),
            "user": os.environ.get("SMTP_USER", self._smtp_user),
            "password": os.environ.get("SMTP_PASSWORD", self._smtp_password),
            "from_address": os.environ.get("SMTP_FROM", self._from_address),
            "use_tls": os.environ.get("SMTP_USE_TLS", str(self._use_tls)).lower() == "true",
        }
    
    def send(
        self, 
        notification: Notification, 
        recipient: str,
        **kwargs
    ) -> ChannelResult:
        """
        Send an email notification.
        
        Args:
            notification: The notification to send
            recipient: Email address to send to
            
        Returns:
            ChannelResult with success status
        """
        try:
            config = self._load_smtp_config()
            
            if not recipient:
                return ChannelResult(
                    success=False,
                    channel=self.channel_type,
                    error="No recipient email address provided",
                )
            
            # Create message
            msg = MIMEMultipart("alternative")
            msg["Subject"] = notification.title
            msg["From"] = config["from_address"]
            msg["To"] = recipient
            
            # Plain text version
            text_content = notification.message
            if notification.action_url:
                text_content += f"\n\nTake action: {notification.action_url}"
            
            msg.attach(MIMEText(text_content, "plain"))
            
            # HTML version
            html_content = self._render_html_email(notification)
            msg.attach(MIMEText(html_content, "html"))
            
            # Send email
            with smtplib.SMTP(config["host"], config["port"]) as server:
                if config["use_tls"]:
                    server.starttls()
                
                if config["user"] and config["password"]:
                    server.login(config["user"], config["password"])
                
                server.sendmail(
                    config["from_address"],
                    recipient,
                    msg.as_string()
                )
            
            logger.info(f"Email sent to {recipient}: {notification.id}")
            
            return ChannelResult(
                success=True,
                channel=self.channel_type,
                message=f"Email sent to {recipient}",
            )
            
        except smtplib.SMTPException as e:
            logger.error(f"SMTP error: {e}")
            return ChannelResult(
                success=False,
                channel=self.channel_type,
                error=f"SMTP error: {str(e)}",
            )
        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            return ChannelResult(
                success=False,
                channel=self.channel_type,
                error=str(e),
            )
    
    def _render_html_email(self, notification: Notification) -> str:
        """
        Render an HTML email for a notification.
        
        Args:
            notification: The notification to render
            
        Returns:
            HTML string
        """
        # Simple HTML template
        priority_colors = {
            NotificationPriority.LOW: "#6b7280",
            NotificationPriority.MEDIUM: "#3b82f6",
            NotificationPriority.HIGH: "#f59e0b",
            NotificationPriority.URGENT: "#ef4444",
        }
        
        color = priority_colors.get(notification.priority, "#3b82f6")
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
        </head>
        <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; 
                     max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background: #f9fafb; border-radius: 8px; padding: 24px; border-left: 4px solid {color};">
                <h2 style="margin: 0 0 16px; color: #111827;">{notification.title}</h2>
                <p style="margin: 0 0 16px; color: #374151; line-height: 1.6;">
                    {notification.message}
                </p>
        """
        
        if notification.action_url:
            html += f"""
                <a href="{notification.action_url}" 
                   style="display: inline-block; background: {color}; color: white; 
                          padding: 12px 24px; border-radius: 6px; text-decoration: none;">
                    Take Action
                </a>
            """
        
        html += """
            </div>
            <p style="color: #9ca3af; font-size: 12px; margin-top: 16px;">
                This notification was sent by Veryfyn Tracking System.
            </p>
        </body>
        </html>
        """
        
        return html
    
    def is_available(self) -> bool:
        """Check if email is properly configured."""
        config = self._load_smtp_config()
        return bool(config["host"] and config["from_address"])


class DesktopChannel(NotificationChannelBase):
    """
    Desktop notification channel.
    
    Sends notifications via desktop notification systems.
    Currently supports in-app toast notifications via Streamlit.
    """
    
    @property
    def channel_type(self) -> NotificationChannel:
        return NotificationChannel.DESKTOP
    
    def send(
        self, 
        notification: Notification, 
        recipient: str = "default",
        **kwargs
    ) -> ChannelResult:
        """
        Send a desktop notification.
        
        For Streamlit, this would use st.toast().
        The actual implementation depends on the UI framework.
        
        Args:
            notification: The notification to send
            recipient: Not used for desktop notifications
            
        Returns:
            ChannelResult indicating success
        """
        # This is a placeholder - actual implementation would integrate
        # with Streamlit's st.toast() or similar
        logger.info(f"Desktop notification: {notification.title}")
        
        return ChannelResult(
            success=True,
            channel=self.channel_type,
            message="Desktop notification queued",
        )
    
    def is_available(self) -> bool:
        """Desktop channel is always available."""
        return True


# Channel registry for easy access
CHANNEL_REGISTRY = {
    NotificationChannel.IN_APP: InAppChannel,
    NotificationChannel.WEB_PUSH: WebPushChannel,
    NotificationChannel.EMAIL: EmailChannel,
    NotificationChannel.DESKTOP: DesktopChannel,
}


def get_channel(
    channel_type: NotificationChannel, 
    **kwargs
) -> NotificationChannelBase:
    """
    Get a channel instance by type.
    
    Args:
        channel_type: Type of channel to get
        **kwargs: Arguments to pass to channel constructor
        
    Returns:
        NotificationChannelBase instance
    """
    channel_class = CHANNEL_REGISTRY.get(channel_type)
    
    if channel_class is None:
        raise ValueError(f"Unknown channel type: {channel_type}")
    
    return channel_class(**kwargs)