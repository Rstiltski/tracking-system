"""
Social Accountability Engine (Phase 3.4)

Implements "Ulysses Pacts" (Commitment Contracts) and Social Broadcasting
based on Social Facilitation Theory and Loss Aversion principles.

Core Concepts:
1. Social Facilitation (Zajonc's Drive Theory): Performance improves when observed
2. Commitment Contracts: Voluntarily restricting future choices to prevent
   acting on short-term impulses
3. Loss Aversion: Penalties are 2x more motivating than equivalent rewards

Key Components:
- AccountabilityPact: A commitment contract with stakes
- AccountabilityPartner: An observer who can view progress
- WebhookBroadcaster: Dispatches events to external channels (Discord/Slack)
- AccountabilityEngine: Monitors contracts and enforces consequences

Reference:
- Zajonc, R.B. (1965). "Social Facilitation"
- Thaler, R. & Sunstein, C. (2008). "Nudge"
- stickK.com - Commitment contract platform

Effect: Commitment contracts increase goal success rates from ~10% to ~50%
"""

import logging
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any, Callable
from datetime import datetime, timedelta
from enum import Enum
import uuid

from brain.core.events import EventBus, Event, publish_event

logger = logging.getLogger(__name__)


# --- Enums ---

class StakeType(Enum):
    """Types of stakes for commitment contracts."""
    FINANCIAL = "financial"           # Real money at risk
    REPUTATIONAL = "reputational"     # Social shame/embarrassment
    VIRTUAL = "virtual"               # Points/XP at risk
    ANTI_CHARITY = "anti_charity"     # Donation to disliked organization


class VisibilityLevel(Enum):
    """Who can see the pact and its outcomes."""
    PUBLIC = "public"                 # Visible to everyone
    PARTNER_ONLY = "partner_only"     # Only accountability partners
    PRIVATE = "private"               # Only the user


class PactStatus(Enum):
    """Lifecycle status of a pact."""
    ACTIVE = "active"                 # Currently being monitored
    FULFILLED = "fulfilled"           # Successfully completed
    FAILED = "failed"                 # Deadline passed without completion
    VOIDED = "voided"                 # Cancelled before deadline


class BroadcastChannel(Enum):
    """Supported broadcast channels."""
    DISCORD_PUBLIC = "discord_public"
    DISCORD_PRIVATE = "discord_private"
    SLACK_TEAM = "slack_team"
    EMAIL = "email"
    WEBHOOK_CUSTOM = "webhook_custom"


# --- Data Classes ---

@dataclass
class AccountabilityPartner:
    """
    An accountability partner who can observe progress.
    
    Partners can have "Spectator Mode" enabled (Hawthorne Effect):
    they can view but not edit the user's data.
    
    Attributes:
        partner_id: Unique identifier for the partner
        partner_name: Display name
        partner_email: Email for notifications
        webhook_url: Optional webhook for automated broadcasts
        spectator_mode: If True, can view but not edit
        relationship_type: Type of relationship (peer, coach, system)
    """
    partner_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    partner_name: str = ""
    partner_email: Optional[str] = None
    webhook_url: Optional[str] = None
    spectator_mode: bool = True
    relationship_type: str = "peer"  # peer, coach, mentor, system
    created_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'partner_id': self.partner_id,
            'partner_name': self.partner_name,
            'partner_email': self.partner_email,
            'webhook_url': self.webhook_url,
            'spectator_mode': self.spectator_mode,
            'relationship_type': self.relationship_type,
            'created_at': self.created_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AccountabilityPartner':
        return cls(
            partner_id=data.get('partner_id', str(uuid.uuid4())),
            partner_name=data.get('partner_name', ''),
            partner_email=data.get('partner_email'),
            webhook_url=data.get('webhook_url'),
            spectator_mode=data.get('spectator_mode', True),
            relationship_type=data.get('relationship_type', 'peer'),
            created_at=datetime.fromisoformat(data['created_at']) if 'created_at' in data else datetime.now()
        )


@dataclass
class AccountabilityPact:
    """
    A commitment contract (Ulysses Pact).
    
    Represents a binding agreement where the user pledges something
    of value that is lost only upon failure.
    
    Attributes:
        pact_id: Unique identifier
        user_id: User who created the pact
        title: Short title for the pact
        description: Detailed description
        
        linked_entity_type: Type of entity (habit, goal, job)
        linked_entity_id: ID of the linked entity
        target_event_type: Event that signifies success
        
        deadline: When the pact expires
        stakes_type: Type of stake at risk
        stakes_amount: Value at risk
        stakes_recipient: Where stakes go on failure (for anti-charity)
        
        partners: List of accountability partners
        broadcast_channels: Where to announce results
        visibility: Who can see this pact
        
        status: Current lifecycle status
        verification_method: How completion is verified (automatic/manual)
        
    Example:
        pact = AccountabilityPact(
            user_id="user-123",
            title="Morning Workout Commitment",
            description="Complete 30 min workout every morning",
            linked_entity_type="habit",
            linked_entity_id="habit-workout",
            target_event_type="habit.completed",
            deadline=datetime.now() + timedelta(days=30),
            stakes_type=StakeType.ANTI_CHARITY,
            stakes_amount=50.0,
            stakes_recipient="Anti-Environmental Fund"
        )
    """
    pact_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = ""
    title: str = ""
    description: str = ""
    
    # The Goal/Habit being tracked
    linked_entity_type: str = ""  # e.g., 'habit', 'job', 'goal'
    linked_entity_id: str = ""
    
    # Validation Logic
    target_event_type: str = "habit.completed"  # Event that signifies success
    deadline: datetime = field(default_factory=lambda: datetime.now() + timedelta(days=7))
    
    # Stakes
    stakes_type: StakeType = StakeType.REPUTATIONAL
    stakes_amount: float = 0.0
    stakes_recipient: str = ""  # e.g., 'NRA', 'Greenpeace', 'Partner Name'
    
    # Social
    partners: List[AccountabilityPartner] = field(default_factory=list)
    broadcast_channels: List[BroadcastChannel] = field(default_factory=list)
    visibility: VisibilityLevel = VisibilityLevel.PARTNER_ONLY
    
    # Status
    status: PactStatus = PactStatus.ACTIVE
    verification_method: str = "automatic"  # "automatic" or "manual"
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)
    fulfilled_at: Optional[datetime] = None
    failed_at: Optional[datetime] = None
    
    @property
    def is_expired(self) -> bool:
        """Check if the pact deadline has passed."""
        return datetime.now() > self.deadline
    
    @property
    def is_active(self) -> bool:
        """Check if the pact is still being monitored."""
        return self.status == PactStatus.ACTIVE
    
    @property
    def stakes_description(self) -> str:
        """Human-readable description of what's at stake."""
        if self.stakes_type == StakeType.FINANCIAL:
            return f"${self.stakes_amount:.2f} at risk"
        elif self.stakes_type == StakeType.ANTI_CHARITY:
            return f"${self.stakes_amount:.2f} to {self.stakes_recipient}"
        elif self.stakes_type == StakeType.REPUTATIONAL:
            return f"Reputation with {len(self.partners)} partner(s)"
        else:
            return f"{self.stakes_amount:.0f} points at risk"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'pact_id': self.pact_id,
            'user_id': self.user_id,
            'title': self.title,
            'description': self.description,
            'linked_entity_type': self.linked_entity_type,
            'linked_entity_id': self.linked_entity_id,
            'target_event_type': self.target_event_type,
            'deadline': self.deadline.isoformat(),
            'stakes_type': self.stakes_type.value,
            'stakes_amount': self.stakes_amount,
            'stakes_recipient': self.stakes_recipient,
            'partners': [p.to_dict() for p in self.partners],
            'broadcast_channels': [c.value for c in self.broadcast_channels],
            'visibility': self.visibility.value,
            'status': self.status.value,
            'verification_method': self.verification_method,
            'created_at': self.created_at.isoformat(),
            'fulfilled_at': self.fulfilled_at.isoformat() if self.fulfilled_at else None,
            'failed_at': self.failed_at.isoformat() if self.failed_at else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AccountabilityPact':
        partners = [AccountabilityPartner.from_dict(p) for p in data.get('partners', [])]
        channels = [BroadcastChannel(c) for c in data.get('broadcast_channels', [])]
        
        return cls(
            pact_id=data.get('pact_id', str(uuid.uuid4())),
            user_id=data.get('user_id', ''),
            title=data.get('title', ''),
            description=data.get('description', ''),
            linked_entity_type=data.get('linked_entity_type', ''),
            linked_entity_id=data.get('linked_entity_id', ''),
            target_event_type=data.get('target_event_type', 'habit.completed'),
            deadline=datetime.fromisoformat(data['deadline']) if 'deadline' in data else datetime.now(),
            stakes_type=StakeType(data.get('stakes_type', 'reputational')),
            stakes_amount=data.get('stakes_amount', 0.0),
            stakes_recipient=data.get('stakes_recipient', ''),
            partners=partners,
            broadcast_channels=channels,
            visibility=VisibilityLevel(data.get('visibility', 'partner_only')),
            status=PactStatus(data.get('status', 'active')),
            verification_method=data.get('verification_method', 'automatic'),
            created_at=datetime.fromisoformat(data['created_at']) if 'created_at' in data else datetime.now(),
            fulfilled_at=datetime.fromisoformat(data['fulfilled_at']) if data.get('fulfilled_at') else None,
            failed_at=datetime.fromisoformat(data['failed_at']) if data.get('failed_at') else None
        )


@dataclass
class PactVerification:
    """
    Record of a pact verification attempt.
    
    Tracks when and how a pact was verified (successfully or not).
    """
    pact_id: str
    verified_at: datetime
    success: bool
    verification_method: str
    event_id: Optional[str] = None
    notes: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'pact_id': self.pact_id,
            'verified_at': self.verified_at.isoformat(),
            'success': self.success,
            'verification_method': self.verification_method,
            'event_id': self.event_id,
            'notes': self.notes
        }


@dataclass
class BroadcastMessage:
    """
    A formatted message ready for broadcast.
    
    Supports different formats for different platforms.
    """
    title: str
    description: str
    color: int  # Hex color for Discord embeds
    emoji: str
    fields: List[Dict[str, Any]] = field(default_factory=list)
    footer: str = "TrackLife Accountability System"
    
    def to_discord_payload(self, username: str = "Accountability Bot") -> Dict[str, Any]:
        """Format for Discord webhook."""
        return {
            "username": username,
            "embeds": [{
                "title": f"{self.emoji} {self.title}",
                "description": self.description,
                "color": self.color,
                "fields": self.fields,
                "footer": {"text": self.footer}
            }]
        }
    
    def to_slack_payload(self) -> Dict[str, Any]:
        """Format for Slack webhook."""
        # Convert hex color to Slack format
        color = f"#{self.color:06x}"
        
        return {
            "attachments": [{
                "title": f"{self.emoji} {self.title}",
                "text": self.description,
                "color": color,
                "fields": self.fields,
                "footer": self.footer
            }]
        }
    
    def to_email_payload(self) -> Dict[str, Any]:
        """Format for email notification."""
        return {
            "subject": f"{self.emoji} {self.title}",
            "body": self.description,
            "fields": self.fields
        }


# --- Broadcasting System ---

class WebhookBroadcaster:
    """
    Handles sending rich messages to external platforms.
    
    Supports Discord, Slack, and custom webhooks.
    Uses the Adapter pattern to normalize payloads across platforms.
    
    Example:
        broadcaster = WebhookBroadcaster()
        broadcaster.configure_channel(
            BroadcastChannel.DISCORD_PUBLIC,
            "https://discord.com/api/webhooks/..."
        )
        broadcaster.announce_success(pact)
    """
    
    def __init__(self):
        self.webhooks: Dict[BroadcastChannel, str] = {}
        self.http_client: Optional[Any] = None  # Lazy-loaded requests
    
    def configure_channel(self, channel: BroadcastChannel, webhook_url: str) -> None:
        """Configure a webhook URL for a channel."""
        self.webhooks[channel] = webhook_url
        logger.info(f"Configured webhook for {channel.value}")
    
    def remove_channel(self, channel: BroadcastChannel) -> bool:
        """Remove a configured webhook."""
        if channel in self.webhooks:
            del self.webhooks[channel]
            return True
        return False
    
    def announce_pact_created(self, pact: AccountabilityPact) -> None:
        """Announce a new pact has been created."""
        message = BroadcastMessage(
            title=f"NEW PLEDGE: {pact.title}",
            description=f"User has committed to: _{pact.description}_\n"
                       f"**Stakes:** {pact.stakes_description}\n"
                       f"**Deadline:** {pact.deadline.strftime('%Y-%m-%d %H:%M')}",
            color=0x3498db,  # Blue
            emoji="🛡️",
            fields=[
                {"name": "Verification", "value": pact.verification_method.title(), "inline": True},
                {"name": "Visibility", "value": pact.visibility.value.replace('_', ' ').title(), "inline": True}
            ]
        )
        self._broadcast(pact.broadcast_channels, message)
    
    def announce_success(self, pact: AccountabilityPact, details: Optional[Dict] = None) -> None:
        """Send a celebratory message for pact fulfillment."""
        message = BroadcastMessage(
            title=f"VICTORY: {pact.title}",
            description=f"🎉 User successfully completed their commitment!\n"
                       f"**Task:** {pact.description}",
            color=0x2ecc71,  # Green
            emoji="🏆",
            fields=[
                {"name": "Stakes Saved", "value": pact.stakes_description, "inline": True},
                {"name": "Completed", "value": pact.fulfilled_at.strftime('%Y-%m-%d %H:%M') if pact.fulfilled_at else "Now", "inline": True}
            ]
        )
        self._broadcast(pact.broadcast_channels, message, username="Victory Bot 🏆")
    
    def announce_failure(self, pact: AccountabilityPact) -> None:
        """Send a shame/penalty message for pact failure."""
        # Build stakes text based on type
        stakes_text = ""
        if pact.stakes_type == StakeType.FINANCIAL:
            stakes_text = f"💸 **PENALTY OWED:** ${pact.stakes_amount:.2f}"
        elif pact.stakes_type == StakeType.ANTI_CHARITY:
            stakes_text = f"😈 **PAIN PLEDGE:** Donate ${pact.stakes_amount:.2f} to {pact.stakes_recipient}"
        elif pact.stakes_type == StakeType.REPUTATIONAL:
            stakes_text = f"📉 **Reputation Impact:** Public failure recorded"
        else:
            stakes_text = f"⚡ **{pact.stakes_amount:.0f} points lost**"
        
        message = BroadcastMessage(
            title=f"FAILED: {pact.title}",
            description=f"❌ The deadline has passed.\n\n{stakes_text}",
            color=0xe74c3c,  # Red
            emoji="🚨",
            fields=[
                {"name": "Deadline", "value": pact.deadline.strftime('%Y-%m-%d %H:%M'), "inline": True},
                {"name": "Status", "value": "Commitment Broken", "inline": True}
            ]
        )
        self._broadcast(pact.broadcast_channels, message, username="The Enforcer 👮")
    
    def announce_progress(self, pact: AccountabilityPact, progress: Dict[str, Any]) -> None:
        """Send a progress update."""
        message = BroadcastMessage(
            title=f"Progress Update: {pact.title}",
            description=f"📊 {progress.get('message', 'Making progress!')}",
            color=0xf39c12,  # Orange
            emoji="📈",
            fields=[
                {"name": "Days Remaining", "value": str((pact.deadline - datetime.now()).days), "inline": True},
                {"name": "Status", "value": "On Track" if progress.get('on_track', True) else "Needs Attention", "inline": True}
            ]
        )
        self._broadcast(pact.broadcast_channels, message, username="Progress Bot 📊")
    
    def _broadcast(
        self, 
        channels: List[BroadcastChannel], 
        message: BroadcastMessage,
        username: str = "Accountability Bot"
    ) -> None:
        """Dispatch message to all configured channels."""
        for channel in channels:
            url = self.webhooks.get(channel)
            if not url:
                logger.debug(f"No webhook configured for {channel.value}")
                continue
            
            try:
                if channel in [BroadcastChannel.DISCORD_PUBLIC, BroadcastChannel.DISCORD_PRIVATE]:
                    payload = message.to_discord_payload(username=username)
                elif channel == BroadcastChannel.SLACK_TEAM:
                    payload = message.to_slack_payload()
                else:
                    payload = message.to_discord_payload(username=username)
                
                self._send_webhook(url, payload)
                logger.info(f"Broadcast sent to {channel.value}")
                
            except Exception as e:
                logger.error(f"Failed to broadcast to {channel.value}: {e}")
    
    def _send_webhook(self, url: str, payload: Dict[str, Any]) -> None:
        """Send HTTP POST to webhook URL."""
        # Lazy-load requests to avoid import issues
        if self.http_client is None:
            try:
                import requests
                self.http_client = requests
            except ImportError:
                logger.warning("requests library not available for webhook")
                return
        
        response = self.http_client.post(url, json=payload, timeout=10)
        response.raise_for_status()


# --- Core Engine ---

class AccountabilityEngine:
    """
    Main engine for managing social accountability.
    
    Monitors contracts and enforces consequences based on
    Social Facilitation Theory and Loss Aversion.
    
    Features:
    - Create and manage commitment pacts
    - Automatic verification via EventBus
    - Webhook broadcasting to Discord/Slack
    - Partner management with spectator mode
    - Deadline monitoring and penalty execution
    
    Example:
        engine = AccountabilityEngine()
        engine.start()
        
        # Create a pact
        pact = engine.create_pact(
            user_id="user-123",
            title="Morning Workout",
            description="30 min workout every morning",
            linked_entity_id="habit-workout",
            stakes_type=StakeType.ANTI_CHARITY,
            stakes_amount=50.0,
            stakes_recipient="Anti-Charity Fund"
        )
        
        # Add a partner
        engine.add_partner(pact.pact_id, AccountabilityPartner(
            partner_name="Accountability Buddy",
            partner_email="buddy@example.com"
        ))
    """
    
    def __init__(self):
        self.pacts: Dict[str, AccountabilityPact] = {}
        self.verifications: List[PactVerification] = []
        self.broadcaster = WebhookBroadcaster()
        self._is_active = False
        self._event_handler = None
    
    def start(self) -> None:
        """Activate the engine to start monitoring."""
        if not self._is_active:
            self._event_handler = self._handle_event
            EventBus.subscribe_global(self._event_handler)
            self._is_active = True
            logger.info("Accountability Engine activated and listening for events")
    
    def stop(self) -> None:
        """Deactivate the engine."""
        if self._is_active and self._event_handler:
            # Note: EventBus doesn't support unsubscribe_global yet
            # In production, we'd need to add that capability
            self._is_active = False
            logger.info("Accountability Engine deactivated")
    
    # --- Pact Management ---
    
    def create_pact(
        self,
        user_id: str,
        title: str,
        description: str,
        linked_entity_type: str = "habit",
        linked_entity_id: str = "",
        target_event_type: str = "habit.completed",
        deadline: Optional[datetime] = None,
        stakes_type: StakeType = StakeType.REPUTATIONAL,
        stakes_amount: float = 0.0,
        stakes_recipient: str = "",
        visibility: VisibilityLevel = VisibilityLevel.PARTNER_ONLY,
        broadcast_channels: Optional[List[BroadcastChannel]] = None
    ) -> AccountabilityPact:
        """
        Create a new accountability pact.
        
        Args:
            user_id: User creating the pact
            title: Short title for the commitment
            description: Detailed description
            linked_entity_type: Type of entity (habit, goal, job)
            linked_entity_id: ID of the linked entity
            target_event_type: Event that signifies success
            deadline: When the pact expires (default: 7 days)
            stakes_type: Type of stake at risk
            stakes_amount: Value at risk
            stakes_recipient: Where stakes go on failure
            visibility: Who can see this pact
            broadcast_channels: Where to announce results
            
        Returns:
            The created AccountabilityPact
        """
        pact = AccountabilityPact(
            user_id=user_id,
            title=title,
            description=description,
            linked_entity_type=linked_entity_type,
            linked_entity_id=linked_entity_id,
            target_event_type=target_event_type,
            deadline=deadline or datetime.now() + timedelta(days=7),
            stakes_type=stakes_type,
            stakes_amount=stakes_amount,
            stakes_recipient=stakes_recipient,
            visibility=visibility,
            broadcast_channels=broadcast_channels or []
        )
        
        self.pacts[pact.pact_id] = pact
        logger.info(f"Created pact: {pact.title} [{pact.pact_id}]")
        
        # Announce the new pledge
        if pact.broadcast_channels:
            self.broadcaster.announce_pact_created(pact)
        
        return pact
    
    def get_pact(self, pact_id: str) -> Optional[AccountabilityPact]:
        """Get a pact by ID."""
        return self.pacts.get(pact_id)
    
    def get_user_pacts(
        self, 
        user_id: str, 
        status: Optional[PactStatus] = None
    ) -> List[AccountabilityPact]:
        """Get all pacts for a user, optionally filtered by status."""
        pacts = [p for p in self.pacts.values() if p.user_id == user_id]
        if status:
            pacts = [p for p in pacts if p.status == status]
        return pacts
    
    def void_pact(self, pact_id: str, reason: str = "") -> bool:
        """Void a pact before its deadline."""
        pact = self.pacts.get(pact_id)
        if not pact or not pact.is_active:
            return False
        
        pact.status = PactStatus.VOIDED
        logger.info(f"Voided pact {pact_id}: {reason}")
        return True
    
    # --- Partner Management ---
    
    def add_partner(self, pact_id: str, partner: AccountabilityPartner) -> bool:
        """Add an accountability partner to a pact."""
        pact = self.pacts.get(pact_id)
        if not pact:
            return False
        
        pact.partners.append(partner)
        logger.info(f"Added partner {partner.partner_name} to pact {pact_id}")
        return True
    
    def remove_partner(self, pact_id: str, partner_id: str) -> bool:
        """Remove an accountability partner from a pact."""
        pact = self.pacts.get(pact_id)
        if not pact:
            return False
        
        original_count = len(pact.partners)
        pact.partners = [p for p in pact.partners if p.partner_id != partner_id]
        return len(pact.partners) < original_count
    
    # --- Verification ---
    
    def _handle_event(self, event: Event) -> None:
        """
        Handle incoming events from EventBus.
        
        Checks if any active pacts are fulfilled by this event.
        """
        for pact in list(self.pacts.values()):
            if not pact.is_active:
                continue
            
            # Check if this event fulfills the pact
            if self._event_matches_pact(event, pact):
                self._fulfill_pact(pact, event)
    
    def _event_matches_pact(self, event: Event, pact: AccountabilityPact) -> bool:
        """Check if an event fulfills a pact's success criteria."""
        # Match event type
        if event.event_type != pact.target_event_type:
            return False
        
        # Match entity ID (if specified)
        if pact.linked_entity_id:
            if str(event.entity_id) != str(pact.linked_entity_id):
                return False
        
        # Match user (if available in event)
        if event.user_id and str(event.user_id) != str(pact.user_id):
            return False
        
        return True
    
    def _fulfill_pact(self, pact: AccountabilityPact, event: Event) -> None:
        """Mark a pact as fulfilled."""
        pact.status = PactStatus.FULFILLED
        pact.fulfilled_at = datetime.now()
        
        # Record verification
        verification = PactVerification(
            pact_id=pact.pact_id,
            verified_at=datetime.now(),
            success=True,
            verification_method="automatic",
            event_id=str(event.entity_id) if event.entity_id else None
        )
        self.verifications.append(verification)
        
        logger.info(f"Pact fulfilled: {pact.title} [{pact.pact_id}]")
        
        # Announce success
        if pact.broadcast_channels:
            self.broadcaster.announce_success(pact)
    
    # --- Deadline Monitoring ---
    
    def check_deadlines(self) -> List[AccountabilityPact]:
        """
        Check all pacts for expired deadlines.
        
        Should be called periodically (e.g., hourly) by a scheduler.
        
        Returns:
            List of pacts that were failed by this check
        """
        now = datetime.now()
        failed_pacts = []
        
        for pact in list(self.pacts.values()):
            if pact.is_active and pact.is_expired:
                self._fail_pact(pact)
                failed_pacts.append(pact)
        
        return failed_pacts
    
    def _fail_pact(self, pact: AccountabilityPact) -> None:
        """Mark a pact as failed and execute penalties."""
        pact.status = PactStatus.FAILED
        pact.failed_at = datetime.now()
        
        # Record verification
        verification = PactVerification(
            pact_id=pact.pact_id,
            verified_at=datetime.now(),
            success=False,
            verification_method="automatic",
            notes="Deadline expired without completion"
        )
        self.verifications.append(verification)
        
        logger.info(f"Pact failed: {pact.title} [{pact.pact_id}]")
        
        # Announce failure
        if pact.broadcast_channels:
            self.broadcaster.announce_failure(pact)
        
        # Execute penalty based on stakes type
        self._execute_penalty(pact)
    
    def _execute_penalty(self, pact: AccountabilityPact) -> None:
        """Execute the penalty for a failed pact."""
        if pact.stakes_type == StakeType.FINANCIAL:
            self._record_virtual_debt(pact)
        elif pact.stakes_type == StakeType.ANTI_CHARITY:
            self._record_virtual_debt(pact)
        elif pact.stakes_type == StakeType.VIRTUAL:
            self._deduct_virtual_points(pact)
        # REPUTATIONAL is handled by the broadcast itself
    
    def _record_virtual_debt(self, pact: AccountabilityPact) -> None:
        """Create a debt record for financial stakes."""
        publish_event(
            event_type="debt.created",
            entity_type="debt",
            data={
                "user_id": pact.user_id,
                "amount": pact.stakes_amount,
                "reason": f"Failed Pact: {pact.title}",
                "recipient": pact.stakes_recipient,
                "pact_id": pact.pact_id,
                "requires_proof": True
            }
        )
        logger.info(f"Recorded debt of ${pact.stakes_amount} for failed pact {pact.pact_id}")
    
    def _deduct_virtual_points(self, pact: AccountabilityPact) -> None:
        """Deduct virtual points for failed pact."""
        publish_event(
            event_type="points.deducted",
            entity_type="points",
            data={
                "user_id": pact.user_id,
                "amount": pact.stakes_amount,
                "reason": f"Failed Pact: {pact.title}",
                "pact_id": pact.pact_id
            }
        )
        logger.info(f"Deducted {pact.stakes_amount} points for failed pact {pact.pact_id}")
    
    # --- Analytics ---
    
    def get_stats(self, user_id: Optional[str] = None) -> Dict[str, Any]:
        """Get accountability statistics."""
        pacts = list(self.pacts.values())
        if user_id:
            pacts = [p for p in pacts if p.user_id == user_id]
        
        if not pacts:
            return {
                "total_pacts": 0,
                "success_rate": 0.0,
                "total_stakes_risked": 0.0,
                "total_stakes_lost": 0.0
            }
        
        fulfilled = [p for p in pacts if p.status == PactStatus.FULFILLED]
        failed = [p for p in pacts if p.status == PactStatus.FAILED]
        
        total_stakes = sum(p.stakes_amount for p in pacts)
        stakes_lost = sum(p.stakes_amount for p in failed if p.stakes_type in [StakeType.FINANCIAL, StakeType.ANTI_CHARITY, StakeType.VIRTUAL])
        
        return {
            "total_pacts": len(pacts),
            "active_pacts": len([p for p in pacts if p.status == PactStatus.ACTIVE]),
            "fulfilled_pacts": len(fulfilled),
            "failed_pacts": len(failed),
            "voided_pacts": len([p for p in pacts if p.status == PactStatus.VOIDED]),
            "success_rate": len(fulfilled) / len(pacts) if pacts else 0.0,
            "total_stakes_risked": total_stakes,
            "total_stakes_lost": stakes_lost,
            "total_partners": sum(len(p.partners) for p in pacts)
        }
    
    def configure_webhook(self, channel: BroadcastChannel, url: str) -> None:
        """Configure a webhook URL for broadcasting."""
        self.broadcaster.configure_channel(channel, url)


# --- Singleton Instance ---

accountability_engine = AccountabilityEngine()


# --- Convenience Functions ---

def create_pact(
    user_id: str,
    title: str,
    description: str,
    **kwargs
) -> AccountabilityPact:
    """Convenience function to create a pact using the singleton engine."""
    return accountability_engine.create_pact(
        user_id=user_id,
        title=title,
        description=description,
        **kwargs
    )


def get_pact(pact_id: str) -> Optional[AccountabilityPact]:
    """Convenience function to get a pact using the singleton engine."""
    return accountability_engine.get_pact(pact_id)


def start_engine() -> None:
    """Start the accountability engine."""
    accountability_engine.start()


def stop_engine() -> None:
    """Stop the accountability engine."""
    accountability_engine.stop()