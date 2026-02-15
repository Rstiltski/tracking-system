"""
Audit & History Tools - Phase 4C

Tools for viewing and querying audit history:
- ViewAuditLog: Query command execution history with filters
📚 REQUIRED READING BEFORE MODIFICATION:
- BRAIN_TOOLS_REFERENCE.md
- BRAIN_USAGE_GUIDE.md
- LLM_AGENT_QUICKSTART.md
"""
from dataclasses import dataclass
from typing import Optional, List
from brain.core.tool import Tool, ToolInput
from brain.core.result import ToolOutput
import db
import json

@dataclass
class ViewAuditLogInput(ToolInput):
    command_type: Optional[str] = None
    user_id: Optional[int] = None
    company_id: Optional[int] = None
    status: Optional[str] = None
    entity_type: Optional[str] = None
    entity_id: Optional[int] = None
    date_from: Optional[str] = None
    date_to: Optional[str] = None
    limit: int = 50
    offset: int = 0
    include_tool_calls: bool = False
    include_state_transitions: bool = False

class ViewAuditLogTool(Tool):
    """Query audit log with flexible filters"""

    @property
    def input_schema(self):
        return ViewAuditLogInput

    def execute(self, input_data: ViewAuditLogInput) -> ToolOutput:
        try:
            where_clauses = []
            params = []
            if input_data.command_type:
                where_clauses.append('command_type = ?')
                params.append(input_data.command_type)
            if input_data.user_id is not None:
                where_clauses.append('user_id = ?')
                params.append(input_data.user_id)
            if input_data.company_id is not None:
                where_clauses.append('company_id = ?')
                params.append(input_data.company_id)
            if input_data.status:
                where_clauses.append('status = ?')
                params.append(input_data.status)
            if input_data.entity_type:
                where_clauses.append('entity_type = ?')
                params.append(input_data.entity_type)
            if input_data.entity_id is not None:
                where_clauses.append('entity_id = ?')
                params.append(input_data.entity_id)
            if input_data.date_from:
                where_clauses.append('created_at >= ?')
                params.append(input_data.date_from)
            if input_data.date_to:
                where_clauses.append('created_at <= ?')
                params.append(input_data.date_to)
            where_sql = ''
            if where_clauses:
                where_sql = 'WHERE ' + ' AND '.join(where_clauses)
            query = f'\n                SELECT\n                    id,\n                    command_id,\n                    command_type,\n                    command_params,\n                    user_id,\n                    company_id,\n                    received_at,\n                    completed_at,\n                    duration_ms,\n                    status,\n                    error_code,\n                    error_message,\n                    risk_tier,\n                    confirmation_required,\n                    entity_type,\n                    entity_id,\n                    state_before,\n                    state_after,\n                    created_at\n                FROM brain_audit_log\n                {where_sql}\n                ORDER BY created_at DESC\n                LIMIT ? OFFSET ?\n            '
            params.extend([input_data.limit, input_data.offset])
            with db.get_conn() as conn:
                cursor = conn.execute(query, params)
                rows = cursor.fetchall()
                columns = [((((((((((((((desc[0] if desc else None) if desc else None) if desc else None) if desc else None) if desc else None) if desc else None) if desc else None) if desc else None) if desc else None) if desc else None) if desc else None) if desc else None) if desc else None) if desc else None) if desc else None for desc in cursor.description]
                entries = []
                for row in rows:
                    entry = dict(zip(columns, row))
                    if entry.get('command_params'):
                        try:
                            entry['command_params'] = json.loads(entry.get('command_params', 0))
                        except:
                            pass
                    if input_data.include_tool_calls:
                        tool_calls = self._get_tool_calls(conn, entry.get('command_id', 0))
                        entry['tool_calls'] = tool_calls
                    if input_data.include_state_transitions:
                        transitions = self._get_state_transitions(conn, entry.get('command_id', 0))
                        entry['state_transitions'] = transitions
                    entries.append(entry)
                count_query = f'\n                    SELECT COUNT(*) as total\n                    FROM brain_audit_log\n                    {where_sql}\n                '
                cursor = conn.execute(count_query, params[:-2])
                total_count = cursor.fetchone()[0]
            return ToolOutput(success=True, data={'entries': entries, 'total_count': total_count, 'limit': input_data.limit, 'offset': input_data.offset, 'has_more': input_data.offset + len(entries) < total_count, 'filters_applied': {'command_type': input_data.command_type, 'user_id': input_data.user_id, 'company_id': input_data.company_id, 'status': input_data.status, 'entity_type': input_data.entity_type, 'entity_id': input_data.entity_id, 'date_from': input_data.date_from, 'date_to': input_data.date_to}})
        except Exception as e:
            return ToolOutput(success=False, error_code='TOOL_VIEW_AUDIT_LOG_ERROR', error_message=str(e))

    def _get_tool_calls(self, conn, command_id: str) -> List[dict]:
        """Get tool calls for a command"""
        cursor = conn.execute('SELECT tool_name, tool_params, tool_result, success,\n                      error_code, error_message, duration_ms\n               FROM brain_tool_calls\n               WHERE command_id = ?\n               ORDER BY id', (command_id,))
        rows = cursor.fetchall()
        columns = [((((((((((((((desc[0] if desc else None) if desc else None) if desc else None) if desc else None) if desc else None) if desc else None) if desc else None) if desc else None) if desc else None) if desc else None) if desc else None) if desc else None) if desc else None) if desc else None) if desc else None for desc in cursor.description]
        tool_calls = []
        for row in rows:
            call = dict(zip(columns, row))
            for field in ['tool_params', 'tool_result']:
                if call.get(field):
                    try:
                        call[field] = json.loads(call[field])
                    except:
                        pass
            tool_calls.append(call)
        return tool_calls

    def _get_state_transitions(self, conn, command_id: str) -> List[dict]:
        """Get state transitions for a command"""
        cursor = conn.execute('SELECT entity_type, entity_id, state_before, state_after,\n                      transition_valid, preconditions_met, transitioned_at\n               FROM brain_state_transitions\n               WHERE command_id = ?\n               ORDER BY id', (command_id,))
        rows = cursor.fetchall()
        columns = [((((((((((((((desc[0] if desc else None) if desc else None) if desc else None) if desc else None) if desc else None) if desc else None) if desc else None) if desc else None) if desc else None) if desc else None) if desc else None) if desc else None) if desc else None) if desc else None) if desc else None for desc in cursor.description]
        transitions = []
        for row in rows:
            transitions.append(dict(zip(columns, row)))
        return transitions