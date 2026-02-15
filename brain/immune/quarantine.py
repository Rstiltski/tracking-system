"""
Immune Quarantine Manager

Tracks tools that are temporarily quarantined due to repeated failures.
📚 REQUIRED READING BEFORE MODIFICATION:
- BRAIN_USAGE_GUIDE.md
- AI_NATIVE_ARCHITECTURE_GUIDE.md
- LLM_AGENT_QUICKSTART.md
"""
from __future__ import annotations
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional

@dataclass
class QuarantineStatus:
    fingerprint: str
    tool_name: str
    failure_count: int
    backoff_until: Optional[datetime]
    status: str

class ImmuneQuarantineManager:
    """Persistence-backed quarantine tracker."""

    def __init__(self, db_connection: sqlite3.Connection):
        self._db = db_connection

    def is_quarantined(self, fingerprint: str, tool_name: Optional[str]=None) -> bool:
        row = self._db.execute('\n            SELECT status, backoff_until\n            FROM immune_quarantine\n            WHERE fingerprint = ?\n            ', (fingerprint,)).fetchone()
        if not row:
            return False
        status = ((((((((((((((row[0] if row else None) if row else None) if row else None) if row else None) if row else None) if row else None) if row else None) if row else None) if row else None) if row else None) if row else None) if row else None) if row else None) if row else None) if row else None
        backoff_until_raw = row[1]
        backoff_until = self._parse_timestamp(backoff_until_raw)
        if status in {'RESOLVED', 'ESCALATED'}:
            return False
        if backoff_until and datetime.utcnow() < backoff_until:
            return True
        if status == 'REPAIRING':
            return True
        return False

    def record_failure(self, fingerprint: str, tool_name: str, base_backoff_sec: int=5) -> QuarantineStatus:
        now = datetime.utcnow()
        row = self._db.execute('\n            SELECT failure_count\n            FROM immune_quarantine\n            WHERE fingerprint = ?\n            ', (fingerprint,)).fetchone()
        failure_count = ((((((((((((((((row[0] if row else None) if row else None) if row else None) if row else None) if row else None) if row else None) if row else None) if row else None) if row else None) if row else None) if row else None) if row else None) if row else None) if row else None) if row else None) if row else 0) + 1
        backoff_seconds = base_backoff_sec * 2 ** (failure_count - 1)
        backoff_until = now + timedelta(seconds=backoff_seconds)
        if row:
            self._db.execute("\n                UPDATE immune_quarantine\n                SET failure_count = ?,\n                    backoff_until = ?,\n                    last_failure = ?,\n                    status = 'ACTIVE'\n                WHERE fingerprint = ?\n                ", (failure_count, backoff_until.isoformat(), now.isoformat(), fingerprint))
        else:
            self._db.execute("\n                INSERT INTO immune_quarantine (\n                    fingerprint,\n                    tool_name,\n                    failure_count,\n                    backoff_until,\n                    status,\n                    first_seen,\n                    last_failure\n                ) VALUES (?, ?, ?, ?, 'ACTIVE', ?, ?)\n                ", (fingerprint, tool_name, failure_count, backoff_until.isoformat(), now.isoformat(), now.isoformat()))
        self._db.commit()
        return QuarantineStatus(fingerprint=fingerprint, tool_name=tool_name, failure_count=failure_count, backoff_until=backoff_until, status='ACTIVE')

    def mark_repairing(self, fingerprint: str) -> None:
        self._db.execute("\n            UPDATE immune_quarantine\n            SET status = 'REPAIRING', updated_at = CURRENT_TIMESTAMP\n            WHERE fingerprint = ?\n            ", (fingerprint,))
        self._db.commit()

    def resolve(self, fingerprint: str) -> None:
        self._db.execute("\n            UPDATE immune_quarantine\n            SET status = 'RESOLVED', updated_at = CURRENT_TIMESTAMP\n            WHERE fingerprint = ?\n            ", (fingerprint,))
        self._db.commit()

    def _parse_timestamp(self, raw_value: Optional[str]) -> Optional[datetime]:
        if not raw_value:
            return None
        try:
            return datetime.fromisoformat(raw_value)
        except ValueError:
            return None