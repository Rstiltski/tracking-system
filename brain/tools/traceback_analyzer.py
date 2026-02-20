#!/usr/bin/env python3
"""
Traceback Analyzer - Automated Root Cause Analysis

This standalone script analyzes audit logs to trace errors back to their root cause.
Runs locally without external API calls (token-efficient).

Usage:
    python brain/tools/traceback_analyzer.py --error <command_id>
    python brain/tools/traceback_analyzer.py --last-failed
    python brain/tools/traceback_analyzer.py --analyze-all --since "2026-02-01"
    python brain/tools/traceback_analyzer.py --entity-type invoice --entity-id 789

Features:
    - Deterministic execution tracing
    - Automated root cause identification
    - Chain of events reconstruction
    - Rule violation detection
    - Actionable recommendations

📚 REQUIRED READING BEFORE MODIFICATION:
- brain/design/06_audit_schema.md
- brain/audit/README.md
"""

import argparse
import json
import sqlite3
import sys
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional
from pathlib import Path


class ErrorCategory(Enum):
    """Categories of errors for classification."""
    POLICY_VIOLATION = "POLICY_VIOLATION"
    STATE_TRANSITION_FAILED = "STATE_TRANSITION_FAILED"
    INVARIANT_VIOLATION = "INVARIANT_VIOLATION"
    TOOL_EXECUTION_FAILED = "TOOL_EXECUTION_FAILED"
    DATA_INTEGRITY = "DATA_INTEGRITY"
    VALIDATION_ERROR = "VALIDATION_ERROR"
    PERMISSION_DENIED = "PERMISSION_DENIED"
    RESOURCE_NOT_FOUND = "RESOURCE_NOT_FOUND"
    EXTERNAL_SERVICE = "EXTERNAL_SERVICE"
    TIMEOUT = "TIMEOUT"
    UNKNOWN = "UNKNOWN"


class Severity(Enum):
    """Severity levels for errors."""
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    INFO = "INFO"


@dataclass
class ChainEvent:
    """An event in the error chain."""
    sequence_number: int
    command_id: str
    command_type: str
    timestamp: datetime
    status: str
    user_id: Optional[int] = None
    entity_type: Optional[str] = None
    entity_id: Optional[int] = None
    state_before: Optional[str] = None
    state_after: Optional[str] = None
    error_code: Optional[str] = None
    error_message: Optional[str] = None
    duration_ms: Optional[int] = None
    impact: str = ""
    tool_calls: List[Dict] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        return {
            "sequence_number": self.sequence_number,
            "command_id": self.command_id,
            "command_type": self.command_type,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "status": self.status,
            "user_id": self.user_id,
            "entity_type": self.entity_type,
            "entity_id": self.entity_id,
            "state_before": self.state_before,
            "state_after": self.state_after,
            "error_code": self.error_code,
            "error_message": self.error_message,
            "duration_ms": self.duration_ms,
            "impact": self.impact,
            "tool_calls": self.tool_calls
        }


@dataclass
class RootCause:
    """Identified root cause of an error."""
    category: ErrorCategory
    severity: Severity
    description: str
    originating_command_id: Optional[str] = None
    originating_command_type: Optional[str] = None
    error_code: Optional[str] = None
    rule_violated: Optional[str] = None
    data_state: Dict[str, Any] = field(default_factory=dict)
    confidence: float = 0.0
    
    def to_dict(self) -> Dict:
        return {
            "category": self.category.value,
            "severity": self.severity.value,
            "description": self.description,
            "originating_command_id": self.originating_command_id,
            "originating_command_type": self.originating_command_type,
            "error_code": self.error_code,
            "rule_violated": self.rule_violated,
            "data_state": self.data_state,
            "confidence": self.confidence
        }


@dataclass
class Recommendation:
    """Actionable recommendation for fixing an error."""
    priority: int
    action: str
    details: str
    sql_query: Optional[str] = None
    command_to_run: Optional[str] = None
    
    def to_dict(self) -> Dict:
        return {
            "priority": self.priority,
            "action": self.action,
            "details": self.details,
            "sql_query": self.sql_query,
            "command_to_run": self.command_to_run
        }


@dataclass
class TracebackResult:
    """Complete result of a traceback analysis."""
    command_id: str
    command_type: str
    status: str
    error_message: str
    error_category: ErrorCategory
    root_cause: RootCause
    chain_of_events: List[ChainEvent]
    recommendations: List[Recommendation]
    confidence_score: float
    analyzed_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict:
        return {
            "command_id": self.command_id,
            "command_type": self.command_type,
            "status": self.status,
            "error_message": self.error_message,
            "error_category": self.error_category.value,
            "root_cause": self.root_cause.to_dict(),
            "chain_of_events": [e.to_dict() for e in self.chain_of_events],
            "recommendations": [r.to_dict() for r in self.recommendations],
            "confidence_score": self.confidence_score,
            "analyzed_at": self.analyzed_at.isoformat()
        }


class TracebackAnalyzer:
    """
    Analyzes errors and traces them to root cause.
    
    This is a standalone, token-efficient analyzer that:
    1. Reads from the local SQLite database
    2. Reconstructs the chain of events leading to an error
    3. Uses pattern matching to identify root causes
    4. Generates actionable recommendations
    
    No external API calls required - runs entirely locally.
    """
    
    ERROR_PATTERNS = {
        "POLICY_": ErrorCategory.POLICY_VIOLATION,
        "AUTH_": ErrorCategory.PERMISSION_DENIED,
        "SECURITY_": ErrorCategory.PERMISSION_DENIED,
        "INT_MONEY_": ErrorCategory.INVARIANT_VIOLATION,
        "INT_LINKING_": ErrorCategory.INVARIANT_VIOLATION,
        "INT_IDEMPOTENCY_": ErrorCategory.INVARIANT_VIOLATION,
        "INT_": ErrorCategory.INVARIANT_VIOLATION,
        "STATE_": ErrorCategory.STATE_TRANSITION_FAILED,
        "TRANSITION_": ErrorCategory.STATE_TRANSITION_FAILED,
        "VALIDATION_": ErrorCategory.VALIDATION_ERROR,
        "INVALID_": ErrorCategory.VALIDATION_ERROR,
        "NOT_FOUND": ErrorCategory.RESOURCE_NOT_FOUND,
        "MISSING_": ErrorCategory.RESOURCE_NOT_FOUND,
        "TOOL_": ErrorCategory.TOOL_EXECUTION_FAILED,
        "EXECUTION_": ErrorCategory.TOOL_EXECUTION_FAILED,
        "TIMEOUT": ErrorCategory.TIMEOUT,
    }
    
    ROOT_CAUSE_PATTERNS = {
        "overpayment": {
            "keywords": ["exceeds remaining balance", "overpayment", "amount exceeds"],
            "category": ErrorCategory.INVARIANT_VIOLATION,
            "severity": Severity.HIGH,
            "template": "Payment amount exceeds remaining balance",
            "rule": "MONEY_002: Payment cannot exceed remaining balance"
        },
        "invalid_transition": {
            "keywords": ["invalid transition", "cannot transition", "not allowed from state"],
            "category": ErrorCategory.STATE_TRANSITION_FAILED,
            "severity": Severity.HIGH,
            "template": "Invalid state transition attempted",
            "rule": "STATE_001: Invalid state transition"
        },
        "missing_field": {
            "keywords": ["is required", "cannot be null", "missing required"],
            "category": ErrorCategory.VALIDATION_ERROR,
            "severity": Severity.MEDIUM,
            "template": "Required field is missing or null",
            "rule": "VALIDATION_001: Required field validation"
        },
        "permission": {
            "keywords": ["permission denied", "not authorized", "access denied"],
            "category": ErrorCategory.PERMISSION_DENIED,
            "severity": Severity.HIGH,
            "template": "User lacks permission for this action",
            "rule": "AUTH_001: Permission denied"
        },
        "duplicate": {
            "keywords": ["duplicate", "already exists", "unique constraint"],
            "category": ErrorCategory.INVARIANT_VIOLATION,
            "severity": Severity.MEDIUM,
            "template": "Duplicate entry detected",
            "rule": "INT_IDEMPOTENCY_001: Duplicate prevention"
        },
    }
    
    def __init__(self, db_path: str = None):
        if db_path is None:
            project_root = Path(__file__).parent.parent.parent
            db_path = str(project_root / "tracking.db")
        
        self.db_path = db_path
        self._conn = None
    
    @property
    def conn(self):
        if self._conn is None:
            self._conn = sqlite3.connect(self.db_path)
            self._conn.row_factory = sqlite3.Row
        return self._conn
    
    def close(self):
        if self._conn:
            self._conn.close()
            self._conn = None
    
    def analyze_error(self, command_id: str) -> Optional[TracebackResult]:
        """Analyze an error by command ID."""
        error_command = self._load_command(command_id)
        if error_command is None:
            return None
        
        if error_command["status"] not in ("FAILED", "ERROR"):
            return TracebackResult(
                command_id=command_id,
                command_type=error_command["command_type"],
                status=error_command["status"],
                error_message="Command did not fail - no error to trace",
                error_category=ErrorCategory.UNKNOWN,
                root_cause=RootCause(
                    category=ErrorCategory.UNKNOWN,
                    severity=Severity.INFO,
                    description="No error to trace"
                ),
                chain_of_events=[],
                recommendations=[],
                confidence_score=0.0
            )
        
        chain = self._get_preceding_chain(
            datetime.fromisoformat(error_command["received_at"]),
            limit=50
        )
        
        error_event = self._command_to_event(error_command, "ERROR - This command failed")
        error_event.sequence_number = len(chain) + 1
        
        error_category = self._classify_error(error_command)
        root_cause = self._identify_root_cause(error_command, chain)
        recommendations = self._generate_recommendations(error_command, root_cause, chain)
        confidence = self._calculate_confidence(root_cause, chain)
        
        return TracebackResult(
            command_id=command_id,
            command_type=error_command["command_type"],
            status=error_command["status"],
            error_message=error_command.get("error_message", "Unknown error"),
            error_category=error_category,
            root_cause=root_cause,
            chain_of_events=chain + [error_event],
            recommendations=recommendations,
            confidence_score=confidence
        )
    
    def analyze_last_failed(self) -> Optional[TracebackResult]:
        """Analyze the most recent failed command."""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT command_id 
            FROM brain_audit_log 
            WHERE status = 'FAILED' 
            ORDER BY created_at DESC 
            LIMIT 1
        """)
        row = cursor.fetchone()
        if row:
            return self.analyze_error(row["command_id"])
        return None
    
    def analyze_all_errors(
        self, 
        since: Optional[datetime] = None,
        until: Optional[datetime] = None,
        limit: int = 100
    ) -> List[TracebackResult]:
        """Analyze all errors in a time range."""
        cursor = self.conn.cursor()
        
        query = "SELECT command_id FROM brain_audit_log WHERE status = 'FAILED'"
        params = []
        
        if since:
            query += " AND created_at >= ?"
            params.append(since.isoformat())
        
        if until:
            query += " AND created_at <= ?"
            params.append(until.isoformat())
        
        query += " ORDER BY created_at DESC LIMIT ?"
        params.append(limit)
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        results = []
        for row in rows:
            result = self.analyze_error(row["command_id"])
            if result:
                results.append(result)
        
        return results
    
    def analyze_entity_history(self, entity_type: str, entity_id: int) -> List[Dict]:
        """Get the complete command history for an entity."""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM brain_audit_log
            WHERE entity_type = ? AND entity_id = ?
            ORDER BY sequence_number ASC
        """, (entity_type, entity_id))
        
        return [dict(row) for row in cursor.fetchall()]
    
    def _load_command(self, command_id: str) -> Optional[Dict]:
        """Load a command from the audit log."""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM brain_audit_log WHERE command_id = ?
        """, (command_id,))
        row = cursor.fetchone()
        return dict(row) if row else None
    
    def _get_preceding_chain(self, timestamp: datetime, limit: int = 50) -> List[ChainEvent]:
        """Get the chain of events preceding a timestamp."""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM brain_audit_log
            WHERE received_at < ?
            ORDER BY received_at DESC
            LIMIT ?
        """, (timestamp.isoformat(), limit))
        
        commands = [dict(row) for row in cursor.fetchall()]
        commands.reverse()
        
        chain = []
        for i, cmd in enumerate(commands):
            impact = self._assess_impact(cmd)
            chain.append(self._command_to_event(cmd, impact))
        
        return chain
    
    def _command_to_event(self, cmd: Dict, impact: str = "") -> ChainEvent:
        """Convert a command record to a ChainEvent."""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT tool_name, success, error_code, error_message, duration_ms
            FROM brain_tool_calls
            WHERE command_id = ?
            ORDER BY id
        """, (cmd["command_id"],))
        
        tool_calls = [dict(row) for row in cursor.fetchall()]
        
        return ChainEvent(
            sequence_number=cmd.get("sequence_number", 0),
            command_id=cmd["command_id"],
            command_type=cmd["command_type"],
            timestamp=datetime.fromisoformat(cmd["received_at"]) if cmd.get("received_at") else None,
            status=cmd["status"],
            user_id=cmd.get("user_id"),
            entity_type=cmd.get("entity_type"),
            entity_id=cmd.get("entity_id"),
            state_before=cmd.get("state_before"),
            state_after=cmd.get("state_after"),
            error_code=cmd.get("error_code"),
            error_message=cmd.get("error_message"),
            duration_ms=cmd.get("duration_ms"),
            impact=impact,
            tool_calls=tool_calls
        )
    
    def _assess_impact(self, cmd: Dict) -> str:
        """Assess the impact of a command on the error chain."""
        status = cmd.get("status", "")
        cmd_type = cmd.get("command_type", "")
        entity_type = cmd.get("entity_type", "")
        state_after = cmd.get("state_after", "")
        
        if status == "FAILED":
            return f"Failed: {cmd_type}"
        
        if state_after:
            return f"State -> {state_after}"
        
        if "Create" in cmd_type:
            return f"Created {entity_type}"
        elif "Update" in cmd_type:
            return f"Updated {entity_type}"
        elif "Delete" in cmd_type:
            return f"Deleted {entity_type}"
        
        return cmd_type
    
    def _classify_error(self, error_command: Dict) -> ErrorCategory:
        """Classify the error based on error code and message."""
        error_code = error_command.get("error_code", "") or ""
        error_message = error_command.get("error_message", "") or ""
        
        for pattern, category in self.ERROR_PATTERNS.items():
            if error_code.startswith(pattern):
                return category
        
        combined = f"{error_code} {error_message}".lower()
        
        if "exceeds" in combined or "balance" in combined:
            return ErrorCategory.INVARIANT_VIOLATION
        if "transition" in combined or "state" in combined:
            return ErrorCategory.STATE_TRANSITION_FAILED
        if "not found" in combined or "missing" in combined:
            return ErrorCategory.RESOURCE_NOT_FOUND
        if "permission" in combined or "unauthorized" in combined:
            return ErrorCategory.PERMISSION_DENIED
        
        return ErrorCategory.UNKNOWN
    
    def _identify_root_cause(self, error_command: Dict, chain: List[ChainEvent]) -> RootCause:
        """Identify the root cause from the error chain."""
        error_code = error_command.get("error_code", "") or ""
        error_message = error_command.get("error_message", "") or ""
        combined = f"{error_code} {error_message}".lower()
        
        for pattern_name, pattern_data in self.ROOT_CAUSE_PATTERNS.items():
            for keyword in pattern_data["keywords"]:
                if keyword.lower() in combined:
                    description = self._build_root_cause_description(
                        error_command, chain, pattern_data
                    )
                    
                    return RootCause(
                        category=pattern_data["category"],
                        severity=pattern_data["severity"],
                        description=description,
                        originating_command_id=self._find_originating_command(
                            error_command, chain, pattern_name
                        ),
                        originating_command_type=error_command.get("command_type"),
                        error_code=error_code,
                        rule_violated=pattern_data.get("rule"),
                        confidence=0.85
                    )
        
        return self._generic_root_cause(error_command, chain)
    
    def _build_root_cause_description(
        self, error_command: Dict, chain: List[ChainEvent], pattern_data: Dict
    ) -> str:
        """Build a human-readable root cause description."""
        template = pattern_data.get("template", "Error occurred")
        params = json.loads(error_command.get("command_params", "{}"))
        
        description = template
        
        if "exceeds" in description.lower() or "balance" in description.lower():
            if params.get("amount"):
                balance = self._extract_balance_from_chain(chain, params.get("invoice_id"))
                description = f"Payment amount ({params.get('amount')}) exceeds remaining balance ({balance})"
        
        if "transition" in description.lower():
            state_before = error_command.get("state_before", "unknown")
            description = f"Invalid state transition from {state_before}"
        
        return description
    
    def _extract_balance_from_chain(self, chain: List[ChainEvent], entity_id: Optional[int]) -> str:
        """Try to extract balance information from the chain."""
        if entity_id is None:
            return "unknown"
        
        for event in reversed(chain):
            if event.command_type == "PaymentRecord" and event.entity_id == entity_id:
                return "partially paid"
        
        return "full balance"
    
    def _find_originating_command(
        self, error_command: Dict, chain: List[ChainEvent], pattern_name: str
    ) -> Optional[str]:
        """Find the command that originated the error condition."""
        entity_type = error_command.get("entity_type")
        entity_id = error_command.get("entity_id")
        
        if entity_type and entity_id:
            for event in chain:
                if event.entity_type == entity_type and event.entity_id == entity_id:
                    return event.command_id
        
        return None
    
    def _generic_root_cause(self, error_command: Dict, chain: List[ChainEvent]) -> RootCause:
        """Generate a generic root cause when no pattern matches."""
        error_message = error_command.get("error_message", "Unknown error")
        error_code = error_command.get("error_code", "")
        
        parts = []
        if error_code:
            parts.append(f"Error code: {error_code}")
        parts.append(error_message)
        
        entity_type = error_command.get("entity_type")
        entity_id = error_command.get("entity_id")
        
        related_events = []
        if entity_type and entity_id:
            for event in chain:
                if event.entity_type == entity_type and event.entity_id == entity_id:
                    related_events.append(event.command_type)
        
        description = " | ".join(parts)
        if related_events:
            description += f" | Related: {', '.join(related_events[-3:])}"
        
        return RootCause(
            category=ErrorCategory.UNKNOWN,
            severity=Severity.MEDIUM,
            description=description,
            originating_command_id=error_command.get("command_id"),
            originating_command_type=error_command.get("command_type"),
            error_code=error_code,
            confidence=0.5
        )
    
    def _generate_recommendations(
        self, error_command: Dict, root_cause: RootCause, chain: List[ChainEvent]
    ) -> List[Recommendation]:
        """Generate actionable recommendations."""
        recommendations = []
        error_category = root_cause.category
        params = json.loads(error_command.get("command_params", "{}"))
        entity_type = error_command.get("entity_type")
        entity_id = error_command.get("entity_id")
        
        if error_category == ErrorCategory.INVARIANT_VIOLATION:
            if "balance" in root_cause.description.lower():
                recommendations.append(Recommendation(
                    priority=1,
                    action="Verify balance before retry",
                    details="Check the current balance before attempting payment",
                    sql_query=f"SELECT balance_due FROM {entity_type}s WHERE id = {entity_id}" if entity_type else None
                ))
                recommendations.append(Recommendation(
                    priority=2,
                    action="Adjust payment amount",
                    details="Ensure payment amount does not exceed remaining balance"
                ))
        
        elif error_category == ErrorCategory.STATE_TRANSITION_FAILED:
            recommendations.append(Recommendation(
                priority=1,
                action="Verify current state",
                details="Check the current state of the entity",
                sql_query=f"SELECT status FROM {entity_type}s WHERE id = {entity_id}" if entity_type else None
            ))
            recommendations.append(Recommendation(
                priority=2,
                action="Review valid transitions",
                details=f"Check state machine for valid transitions from {error_command.get('state_before', 'unknown')}"
            ))
        
        elif error_category == ErrorCategory.VALIDATION_ERROR:
            recommendations.append(Recommendation(
                priority=1,
                action="Fix validation errors",
                details=root_cause.description
            ))
        
        elif error_category == ErrorCategory.PERMISSION_DENIED:
            recommendations.append(Recommendation(
                priority=1,
                action="Check user permissions",
                details="Verify user has required role/permission for this action"
            ))
        
        elif error_category == ErrorCategory.RESOURCE_NOT_FOUND:
            recommendations.append(Recommendation(
                priority=1,
                action="Verify resource exists",
                details="Check if the referenced resource exists",
                sql_query=f"SELECT * FROM {entity_type}s WHERE id = {entity_id}" if entity_type else None
            ))
        
        recommendations.append(Recommendation(
            priority=99,
            action="Review audit log",
            details="Check the full audit log for more context",
            command_to_run=f"python brain/tools/traceback_analyzer.py --entity-type {entity_type} --entity-id {entity_id}" if entity_type and entity_id else None
        ))
        
        return recommendations
    
    def _calculate_confidence(self, root_cause: RootCause, chain: List[ChainEvent]) -> float:
        """Calculate confidence score for the analysis."""
        base_confidence = root_cause.confidence
        
        if len(chain) >= 10:
            base_confidence += 0.05
        elif len(chain) >= 5:
            base_confidence += 0.02
        
        if root_cause.category != ErrorCategory.UNKNOWN:
            base_confidence += 0.05
        
        if root_cause.originating_command_id:
            base_confidence += 0.05
        
        return min(1.0, base_confidence)
    
    def print_report(self, result: TracebackResult):
        """Print a formatted report to console."""
        print("=" * 65)
        print("                    TRACEBACK ANALYSIS REPORT")
        print("=" * 65)
        print(f"Command ID: {result.command_id}")
        print(f"Command Type: {result.command_type}")
        print(f"Status: {result.status}")
        print(f"Error Category: {result.error_category.value}")
        print(f"Confidence: {result.confidence_score:.0%}")
        print()
        
        print("ROOT CAUSE:")
        self._print_tree(result.root_cause.description, indent=0)
        print()
        
        print(f"CHAIN OF EVENTS ({len(result.chain_of_events)} events):")
        print("-" * 65)
        print(f"{'#':<4} {'Time':<20} {'Command':<20} {'Impact':<18}")
        print("-" * 65)
        
        for event in result.chain_of_events[-10:]:
            time_str = event.timestamp.strftime("%Y-%m-%d %H:%M:%S") if event.timestamp else "N/A"
            cmd_str = event.command_type[:18] if len(event.command_type) > 18 else event.command_type
            impact_str = event.impact[:16] if len(event.impact) > 16 else event.impact
            print(f"{event.sequence_number:<4} {time_str:<20} {cmd_str:<20} {impact_str:<18}")
        
        print("-" * 65)
        print()
        
        if result.root_cause.rule_violated:
            print("RULE VIOLATIONS:")
            print(f"  -> {result.root_cause.rule_violated} [BLOCKED]")
            print()
        
        print("RECOMMENDATIONS:")
        for rec in sorted(result.recommendations, key=lambda r: r.priority):
            print(f"{rec.priority}. {rec.action}")
            print(f"   {rec.details}")
            if rec.sql_query:
                print(f"   SQL: {rec.sql_query}")
        
        print()
        print("=" * 65)
    
    def _print_tree(self, text: str, indent: int):
        """Print a tree structure."""
        prefix = "    " * indent + ("-> " if indent > 0 else "")
        print(f"{prefix}{text}")


def main():
    """Main entry point for command-line usage."""
    parser = argparse.ArgumentParser(
        description="Traceback Analyzer - Automated Root Cause Analysis",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument("--error", "-e", help="Analyze a specific error by command ID")
    parser.add_argument("--last-failed", "-l", action="store_true", help="Analyze the most recent failed command")
    parser.add_argument("--analyze-all", "-a", action="store_true", help="Analyze all errors in time range")
    parser.add_argument("--since", "-s", help="Start date for analysis (YYYY-MM-DD)")
    parser.add_argument("--until", "-u", help="End date for analysis (YYYY-MM-DD)")
    parser.add_argument("--entity-type", "-t", help="Entity type for history lookup")
    parser.add_argument("--entity-id", "-i", type=int, help="Entity ID for history lookup")
    parser.add_argument("--db-path", "-d", help="Path to SQLite database")
    parser.add_argument("--json", "-j", action="store_true", help="Output as JSON")
    parser.add_argument("--limit", type=int, default=100, help="Maximum errors to analyze")
    
    args = parser.parse_args()
    
    analyzer = TracebackAnalyzer(db_path=args.db_path)
    
    try:
        if args.error:
            result = analyzer.analyze_error(args.error)
            if result:
                if args.json:
                    print(json.dumps(result.to_dict(), indent=2))
                else:
                    analyzer.print_report(result)
            else:
                print(f"Error: Command {args.error} not found")
                sys.exit(1)
        
        elif args.last_failed:
            result = analyzer.analyze_last_failed()
            if result:
                if args.json:
                    print(json.dumps(result.to_dict(), indent=2))
                else:
                    analyzer.print_report(result)
            else:
                print("No failed commands found")
                sys.exit(1)
        
        elif args.analyze_all:
            since = datetime.fromisoformat(args.since) if args.since else None
            until = datetime.fromisoformat(args.until) if args.until else None
            
            results = analyzer.analyze_all_errors(since=since, until=until, limit=args.limit)
            
            if args.json:
                print(json.dumps([r.to_dict() for r in results], indent=2))
            else:
                print(f"Analyzed {len(results)} errors:")
                print()
                for result in results:
                    print(f"  {result.command_id}: {result.error_category.value} - {result.root_cause.description[:50]}")
        
        elif args.entity_type and args.entity_id:
            history = analyzer.analyze_entity_history(args.entity_type, args.entity_id)
            
            if args.json:
                print(json.dumps(history, indent=2, default=str))
            else:
                print(f"History for {args.entity_type} {args.entity_id}:")
                print("-" * 65)
                for cmd in history:
                    time_str = cmd.get("received_at", "N/A")[:19]
                    print(f"  {time_str} | {cmd['command_type']:<20} | {cmd['status']}")
        
        else:
            parser.print_help()
    
    finally:
        analyzer.close()


if __name__ == "__main__":
    main()