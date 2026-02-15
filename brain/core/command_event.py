"""
CommandEvent - Represents a command to be executed by the Brain
📚 REQUIRED READING BEFORE MODIFICATION:
- BRAIN_USAGE_GUIDE.md
- BRAIN_TOOLS_REFERENCE.md
- AI_NATIVE_ARCHITECTURE_GUIDE.md
- LLM_AGENT_QUICKSTART.md
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Any
from uuid import uuid4

@dataclass
class CommandEvent:
    """
    A command to be executed by the Brain.

    Every user action, scheduled task, or system operation is represented as a CommandEvent.
    """
    command_id: str = field(default_factory=lambda: str(uuid4()))
    command_type: str = ''
    params: dict = field(default_factory=dict)
    user_id: int = 0
    company_id: int = 1
    session_id: Optional[str] = None
    client_ip: Optional[str] = None
    user_agent: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)
    idempotency_key: Optional[str] = None
    confirmation_token: Optional[str] = None
    metadata: dict = field(default_factory=dict)

    def __post_init__(self):
        """Validate command event after initialization"""
        if not self.command_type:
            raise ValueError('command_type is required')
        if self.user_id is None:
            raise ValueError('user_id is required')

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization"""
        return {'command_id': self.command_id, 'command_type': self.command_type, 'params': self.params, 'user_id': self.user_id, 'company_id': self.company_id, 'session_id': self.session_id, 'client_ip': self.client_ip, 'user_agent': self.user_agent, 'timestamp': self.timestamp.isoformat() if self.timestamp else None, 'idempotency_key': self.idempotency_key, 'confirmation_token': self.confirmation_token, 'metadata': self.metadata}

    @classmethod
    def from_dict(cls, data: dict) -> 'CommandEvent':
        """Create from dictionary"""
        if 'timestamp' in data and isinstance(data.get('timestamp', 0), str):
            data['timestamp'] = datetime.fromisoformat(data.get('timestamp', 0))
        return cls(**data)