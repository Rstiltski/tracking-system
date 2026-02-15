"""
Core Types and Enums for the Brain.
📚 REQUIRED READING BEFORE MODIFICATION:
- BRAIN_USAGE_GUIDE.md
- BRAIN_TOOLS_REFERENCE.md
- AI_NATIVE_ARCHITECTURE_GUIDE.md
- LLM_AGENT_QUICKSTART.md
"""
from enum import Enum

class Role(str, Enum):
    """User Roles for permission checks."""
    OWNER = "Owner"  # ✅ This must be here
    ADMIN = "Admin"
    MANAGER = "Manager"
    STAFF = "Staff"
    CREW = "Crew"
    
    @classmethod
    def _missing_(cls, value):
        if isinstance(value, str):
            for member in cls:
                if member.value.lower() == value.lower():
                    return member
        return None

class CommandStatus(str, Enum):
    PENDING = "PENDING"
    EXECUTING = "EXECUTING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
