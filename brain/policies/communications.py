"""
Communications Policy - Prevent spam, enforce rate limits, and ensure compliance
📚 REQUIRED READING BEFORE MODIFICATION:
- BRAIN_USAGE_GUIDE.md
- brain/design/02_policy_packs.md
- LLM_AGENT_QUICKSTART.md
"""

from datetime import datetime, timedelta
import logging
from brain.core.command_event import CommandEvent
from brain.core.result import PolicyResult
import db

logger = logging.getLogger(__name__)

class CommunicationsPolicy:
    """
    Communications Policy enforces communication best practices:
    - Rate limiting (prevent spam)
    - Duplicate message prevention
    - Quiet hours warnings for SMS

    This policy helps prevent:
    - Sending too many messages too quickly
    - Duplicate messages to the same customer
    - Sending SMS during late night/early morning hours
    """

    # Rate limits: (max_count, window_seconds)
    RATE_LIMITS = {
        "SendMessage": (10, 60),  # 10 messages per minute
        "SendBulkMessage": (100, 3600),  # 100 bulk messages per hour
        "SendInvoiceEmail": (20, 60),  # 20 invoice emails per minute
        "SendQuoteEmail": (20, 60),  # 20 quote emails per minute
        "SendJobConfirmation": (30, 60),  # 30 confirmations per minute
        "SendJobReminder": (30, 60),  # 30 reminders per minute
    }

    # Quiet hours for SMS (24-hour format)
    QUIET_HOURS_START = 21  # 9 PM
    QUIET_HOURS_END = 8     # 8 AM
    FAILED_CHECKS_THRESHOLD = 3

    def __init__(self):
        self._rate_limit_failures = 0

    def check(self, event: CommandEvent) -> PolicyResult:
        """
        Run all communications checks.

        Returns:
            PolicyResult - ALLOW, DENY, or WARN
        """
        # Only apply to communication commands
        comm_commands = ["SendMessage", "SendBulkMessage", "SendInvoiceEmail",
                        "SendQuoteEmail", "SendJobConfirmation", "SendJobReminder"]

        if event.command_type not in comm_commands:
            return PolicyResult.allow()

        # Run checks in order
        result = self._check_rate_limit(event)
        if result.is_denied:
            return result

        result = self._check_duplicate_message(event)
        if result.is_denied:
            return result

        result = self._check_quiet_hours(event)
        if result.status == "WARN":
            # Log warning but don't block
            print(f"[WARN] Communications Warning: {result.message}")

        return PolicyResult.allow()

    def _check_rate_limit(self, event: CommandEvent) -> PolicyResult:
        """
        COMM-001: Enforce rate limits on messaging.

        Prevents sending too many messages too quickly, which could:
        - Trigger spam filters
        - Annoy customers
        - Exceed API quotas from SMS/email providers
        """
        if event.command_type not in self.RATE_LIMITS:
            return PolicyResult.allow()

        limit, window_seconds = self.RATE_LIMITS[event.command_type]

        # Count recent messages of this type
        cutoff_time = (datetime.now() - timedelta(seconds=window_seconds)).isoformat()

        try:
            # Query communication_log for recent messages
            recent_count = db.count_recent_communications(
                command_type=event.command_type,
                since=cutoff_time,
                user_id=event.user_id
            )

            if recent_count >= limit:
                window_minutes = window_seconds / 60
                return PolicyResult.deny(
                    f"Rate limit exceeded: {limit} {event.command_type} per {window_minutes:.0f} minutes. "
                    f"Current: {recent_count}. Please wait before sending more.",
                    error_code="COMM_RATE_LIMIT_EXCEEDED"
                )
        except Exception as exc:
            # If rate limit check fails, allow anyway (don't block legitimate traffic)
            logger.warning("Rate limit check failed for %s", event.command_type, exc_info=exc)

        return PolicyResult.allow()

    def _check_duplicate_message(self, event: CommandEvent) -> PolicyResult:
        """
        COMM-002: Prevent sending duplicate messages within short window.

        Prevents accidentally sending the same message multiple times to the same customer
        (e.g., double-clicking send button, or system retry).
        """
        # Only check for single-recipient commands
        if event.command_type in ["SendBulkMessage"]:
            return PolicyResult.allow()

        customer_id = event.params.get("customer_id")
        message_body = event.params.get("message", "")
        channel = event.params.get("channel", "sms")

        if not customer_id or not message_body:
            return PolicyResult.allow()

        # Check for duplicate in last 5 minutes
        cutoff_time = (datetime.now() - timedelta(minutes=5)).isoformat()

        try:
            duplicate = db.find_recent_duplicate_message(
                customer_id=customer_id,
                message_body=message_body,
                channel=channel,
                since=cutoff_time
            )

            if duplicate:
                sent_at = duplicate.get("sent_at", "recently")
                return PolicyResult.deny(
                    f"Duplicate message detected. Same message was sent to this customer at {sent_at}. "
                    f"Wait at least 5 minutes before resending.",
                    error_code="COMM_DUPLICATE_MESSAGE"
                )
        except Exception as exc:
            # If duplicate check fails, allow anyway
            logger.warning("Duplicate message check failed for %s", event.command_type, exc_info=exc)

        return PolicyResult.allow()

    def _check_quiet_hours(self, event: CommandEvent) -> PolicyResult:
        """
        COMM-004: Warn about sending SMS during quiet hours.

        This is a soft check (warning only) to alert users about sending messages
        during late night/early morning hours, which may annoy customers.
        """
        # Only apply to SMS messages
        channel = event.params.get("channel", "sms")
        if channel != "sms":
            return PolicyResult.allow()

        current_hour = datetime.now().hour

        # Check if current time is during quiet hours
        if self.QUIET_HOURS_START <= current_hour or current_hour < self.QUIET_HOURS_END:
            return PolicyResult.warn(
                f"Sending SMS during quiet hours ({self.QUIET_HOURS_START}:00-{self.QUIET_HOURS_END}:00). "
                f"Consider scheduling for later to avoid disturbing customers."
            )

        return PolicyResult.allow()
