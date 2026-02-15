"""
Command Event for Brain System

Defines the command event class for tracking commands in the brain system.
"""
from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Any

@dataclass
class CommandEvent:
    """
    Represents a command event in the brain system.
    
    Used for audit logging and tracking of commands executed through the brain system.
    """
    command: str
    params: Dict[str, Any]
    timestamp: datetime
    brain_id: str
    user_id: str = ""
    session_id: str = ""
    ip_address: str = ""
    user_agent: str = ""
    result: str = ""  # Success/failure indicator
    execution_time_ms: float = 0.0
    error_message: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the CommandEvent to a dictionary."""
        return {
            'command': self.command,
            'params': self.params,
            'timestamp': self.timestamp.isoformat(),
            'brain_id': self.brain_id,
            'user_id': self.user_id,
            'session_id': self.session_id,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'result': self.result,
            'execution_time_ms': self.execution_time_ms,
            'error_message': self.error_message
        }