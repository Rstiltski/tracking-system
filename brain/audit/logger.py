"""
Audit Logger - Logs all commands to append-only audit log
Refactored to handle anonymous logging safely and restore Class structure.
📚 REQUIRED READING BEFORE MODIFICATION:
- BRAIN_USAGE_GUIDE.md
- brain/design/06_audit_schema.md
- LLM_AGENT_QUICKSTART.md
"""
import json
from datetime import datetime
from typing import Optional, Any

# Conditional streamlit import for test compatibility
try:
    import streamlit as st
    HAS_STREAMLIT = True
except ImportError:
    HAS_STREAMLIT = False
    st = None

import logging
import sys

# Add global logging config to ensure sys.stderr is used
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("BrainAudit")

import db
from brain.audit.schema import ensure_audit_tables

class AuditLogger:
    """
    Logs all commands to append-only audit log.
    """

    def __init__(self):
        self._ensure_audit_tables()

    def _ensure_audit_tables(self):
        """Ensure audit log tables exist"""
        try:
            ensure_audit_tables()
        except Exception as e:
            logger.warning(f'Could not ensure audit tables: {e}')

    def log_command_received(self, event, risk_tier: int) -> int:
        """
        Log when command is received.
        Returns audit log entry ID.
        """
        user_id = getattr(event, 'user_id', None)
        if user_id is None:
            if HAS_STREAMLIT and hasattr(st, 'session_state') and 'user' in st.session_state and st.session_state.user:
                user_id = st.session_state.user.get('id')
            else:
                user_id = 0
        try:
            with db.get_conn() as conn:
                cursor = conn.cursor()
                if user_id == 0:
                    cursor.execute('SELECT 1 FROM users WHERE id = 0')
                    if not cursor.fetchone():
                        cursor.execute("INSERT OR IGNORE INTO users (id, username, password_hash, role, created_at, is_active) VALUES (0, 'system', 'system_placeholder_hash', 'Architect', datetime('now'), 0)")
                try:
                    params_json = json.dumps(getattr(event, 'params', {}))
                except Exception:
                    params_json = '{}'
                cursor.execute("""
                    INSERT INTO brain_audit_log (
                        command_id, sequence_number, command_type, command_params,
                        idempotency_key, user_id, company_id, session_id,
                        client_ip, user_agent, received_at, status, risk_tier,
                        confirmation_required, confirmation_token
                    ) VALUES (?, (SELECT COALESCE(MAX(sequence_number), 0) + 1 FROM brain_audit_log), ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (getattr(event, 'command_id', 'unknown'), getattr(event, 'command_type', 'unknown'), params_json, getattr(event, 'idempotency_key', None), user_id, getattr(event, 'company_id', None), getattr(event, 'session_id', None), getattr(event, 'client_ip', None), getattr(event, 'user_agent', None), getattr(event, 'timestamp', datetime.now().isoformat()), 'PENDING', risk_tier, False, getattr(event, 'confirmation_token', None)))
                audit_id = cursor.lastrowid
                conn.commit()
                return audit_id
        except Exception as e:
            logger.warning(f'Audit log failed: {e}')
            return 0

    def log_command_started(self, command_id: str):
        """Log when command execution starts"""
        try:
            with db.get_conn() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE brain_audit_log
                    SET started_at = ?, status = 'EXECUTING'
                    WHERE command_id = ?
                """, (datetime.now().isoformat(), command_id))
                conn.commit()
        except Exception as e:
            print(f"ERROR: Audit log failed to start command {command_id}: {e}")

    def log_command_completed(self, command_id: str, result, duration_ms: int, plan: Optional[list]=None, tool_results: Optional[list]=None):
        """Log when command execution completes"""
        try:
            # Import here to avoid circular import
            try:
                from brain.core.result import BrainResult
            except ImportError:
                pass
            
            try:
                data_json = json.dumps(result.data) if result.data else None
                plan_json = json.dumps(plan) if plan else None
                tools_json = json.dumps(tool_results) if tool_results else None
            except Exception:
                data_json, plan_json, tools_json = (None, None, None)
            with db.get_conn() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE brain_audit_log
                    SET
                        completed_at = ?,
                        duration_ms = ?,
                        status = ?,
                        result_data = ?,
                        error_code = ?,
                        error_message = ?,
                        stack_trace = ?,
                        plan = ?,
                        tool_results = ?,
                        entity_type = ?,
                        entity_id = ?,
                        state_before = ?,
                        state_after = ?
                    WHERE command_id = ?
                """, (datetime.now().isoformat(), duration_ms, result.status, data_json, result.error_code, result.error_message, result.stack_trace, plan_json, tools_json, result.entity_type, result.entity_id, result.state_before, result.state_after, command_id))
                conn.commit()
        except Exception as e:
            print(f"ERROR: Audit log failed to complete command {command_id}: {e}")

    def log_tool_call(self, command_id: str, tool_name: str, tool_params: dict, tool_result: Any, success: bool, error_code: Optional[str]=None, error_message: Optional[str]=None, duration_ms: Optional[int]=None):
        """Log individual tool call"""
        try:
            with db.get_conn() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO brain_tool_calls (
                        command_id, tool_name, tool_params, tool_result,
                        success, error_code, error_message,
                        started_at, completed_at, duration_ms
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (command_id, tool_name, json.dumps(tool_params, default=str), json.dumps(tool_result, default=str) if tool_result else None, success, error_code, error_message, datetime.now().isoformat(), datetime.now().isoformat(), duration_ms))
                conn.commit()
        except Exception as e:
            print(f"ERROR: Audit log failed to log tool call for {command_id}: {e}")

    def log_state_transition(self, command_id: str, entity_type: str, entity_id: int, state_before: str, state_after: str, transition_valid: bool, preconditions_met: bool, side_effects: Optional[list]=None):
        """Log state machine transition"""
        try:
            current_time = datetime.now().isoformat()
            with db.get_conn() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO brain_state_transitions (
                        command_id, entity_type, entity_id,
                        from_state, to_state, state_before, state_after,
                        transition_valid, preconditions_met, side_effects, transitioned_at, transition_time
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (command_id, entity_type, entity_id, 
                      state_before,  # Map to from_state
                      state_after,   # Map to to_state (this is the NOT NULL column)
                      state_before,  # Map to state_before 
                      state_after,   # Map to state_after
                      transition_valid, preconditions_met, 
                      json.dumps(side_effects) if side_effects else None, 
                      current_time,  # Map to transitioned_at
                      current_time)) # Map to transition_time (this is the other NOT NULL column)
                conn.commit()
        except Exception as e:
            print(f"ERROR: Audit log failed to log state transition for {command_id}: {e}")

    def get_command_by_idempotency_key(self, command_type: str, idempotency_key: str) -> Optional[dict]:
        """Get command by idempotency key."""
        try:
            with db.get_conn() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT command_id, status, result_data
                    FROM brain_audit_log
                    WHERE command_type = ? AND idempotency_key = ?
                    ORDER BY created_at DESC
                    LIMIT 1
                """, (command_type, idempotency_key))
                row = cursor.fetchone()
                if row:
                    return {'command_id': row[0], 'status': row[1], 'result_data': json.loads(row[2]) if row[2] else None}
        except Exception as e:
            print(f"ERROR: Audit log failed to get command by idempotency key {idempotency_key}: {e}")
        return None
