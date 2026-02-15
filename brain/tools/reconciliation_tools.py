"""
Reconciliation tools - Check and fix invariant violations
📚 REQUIRED READING BEFORE MODIFICATION:
- BRAIN_TOOLS_REFERENCE.md
- BRAIN_USAGE_GUIDE.md
- LLM_AGENT_QUICKSTART.md
"""
import json
from dataclasses import dataclass
from typing import Optional, List, Dict
from brain.core.tool import Tool, ToolInput
from brain.core.result import ToolOutput
from brain.invariants.money_invariants import MoneyInvariants
from brain.invariants.linking_invariants import LinkingInvariants
from brain.invariants.idempotency_invariants import IdempotencyInvariants
from brain.invariants.checker import ViolationSeverity
import db

@dataclass
class ReconcileInvariantsInput(ToolInput):
    """Input for reconciliation command."""
    check_types: Optional[List[str]] = None
    auto_fix: bool = False

    def __post_init__(self):
        if self.check_types is None:
            self.check_types = ['money', 'linking', 'idempotency']

class ReconcileInvariantsTool(Tool):
    """
    Check all business invariants and report violations.
    
    This tool runs all invariant checkers and returns a report
    of any violations found. Optionally attempts to auto-fix
    violations where possible.
    """

    @property
    def input_schema(self):
        return ReconcileInvariantsInput

    def execute(self, input_data: ReconcileInvariantsInput) -> ToolOutput:
        try:
            with db.get_conn() as conn:
                checkers = {}
                if 'money' in input_data.check_types:
                    checkers['money'] = MoneyInvariants()
                if 'linking' in input_data.check_types:
                    checkers['linking'] = LinkingInvariants()
                if 'idempotency' in input_data.check_types:
                    checkers['idempotency'] = IdempotencyInvariants()
                all_violations = []
                violations_by_checker = {}
                for checker_name, checker in checkers.items():
                    violations = checker.check_all(conn)
                    violations_by_checker[checker_name] = violations
                    all_violations.extend(violations)
                violation_counts = {'critical': sum((1 for v in all_violations if v.severity == ViolationSeverity.CRITICAL)), 'high': sum((1 for v in all_violations if v.severity == ViolationSeverity.HIGH)), 'medium': sum((1 for v in all_violations if v.severity == ViolationSeverity.MEDIUM)), 'low': sum((1 for v in all_violations if v.severity == ViolationSeverity.LOW))}
                formatted_violations = []
                for violation in all_violations:
                    formatted_violations.append({'code': violation.code, 'severity': violation.severity.value, 'entity_type': violation.entity_type, 'entity_id': violation.entity_id, 'message': violation.message, 'details': violation.details})
                fixed_count = 0
                fix_errors = []
                if input_data.auto_fix:
                    # Attempt to auto-fix certain violation types
                    for violation in all_violations:
                        try:
                            if violation.code == 'INV_MONEY_BALANCE_MISMATCH':
                                # Fix invoice balance: recalculate balance_due = total - paid
                                inv_id = violation.entity_id
                                details = violation.details or {}
                                expected_balance = details.get('expected_balance')
                                if inv_id and expected_balance is not None:
                                    conn.execute(
                                        "UPDATE invoices SET balance_due = ? WHERE id = ?",
                                        (expected_balance, inv_id)
                                    )
                                    fixed_count += 1
                            elif violation.code == 'INV_LINK_JOB_INVOICE_MISMATCH':
                                # Fix job-invoice link mismatch by syncing invoice_no/job_id
                                details = violation.details or {}
                                job_id = details.get('job_id')
                                invoice_no = details.get('job_invoice_no') or details.get('invoice_no')
                                if job_id and invoice_no:
                                    # Update invoice to point to job
                                    conn.execute(
                                        "UPDATE invoices SET job_id = ? WHERE invoice_no = ?",
                                        (job_id, invoice_no)
                                    )
                                    fixed_count += 1
                            elif violation.code == 'INV_MONEY_DEPOSIT_MISMATCH':
                                # Fix deposit exceeding quoted price by setting to quoted price
                                job_id = violation.entity_id
                                details = violation.details or {}
                                quoted_price = details.get('quoted_price', 0)
                                if job_id:
                                    conn.execute(
                                        "UPDATE jobs SET deposit = ? WHERE id = ?",
                                        (quoted_price, job_id)
                                    )
                                    fixed_count += 1
                        except Exception as fix_error:
                            fix_errors.append(f"Failed to fix {violation.code} for {violation.entity_type} {violation.entity_id}: {str(fix_error)}")
                return ToolOutput(success=True, data={'total_violations': len(all_violations), 'violation_counts': violation_counts, 'violations': formatted_violations, 'violations_by_checker': {name: len(violations) for name, violations in violations_by_checker.items()}, 'auto_fix_enabled': input_data.auto_fix, 'fixed_count': fixed_count, 'fix_errors': fix_errors, 'has_critical': violation_counts.get('critical', 0) > 0})
        except Exception as e:
            return ToolOutput(success=False, error_code='TOOL_RECONCILE_FAILED', error_message=f'Reconciliation failed: {str(e)}')

@dataclass
class GetReconciliationHistoryInput(ToolInput):
    """Input for getting reconciliation history."""
    limit: int = 10

class GetReconciliationHistoryTool(Tool):
    """Get history of reconciliation runs."""

    @property
    def input_schema(self):
        return GetReconciliationHistoryInput

    def execute(self, input_data: GetReconciliationHistoryInput) -> ToolOutput:
        try:
            with db.get_conn() as conn:
                cursor = conn.cursor()
                cursor.execute("\n                    SELECT \n                        command_id,\n                        received_at,\n                        completed_at,\n                        duration_ms,\n                        status,\n                        result_data\n                    FROM brain_audit_log\n                    WHERE command_type = 'ReconcileInvariants'\n                    ORDER BY received_at DESC\n                    LIMIT ?\n                ", (input_data.limit,))
                runs = []
                for row in cursor.fetchall():
                    result_data = json.loads(row[5]) if row[5] else {}
                    runs.append({
                        'command_id': row[0] if row else None,
                        'started_at': row[1],
                        'completed_at': row[2],
                        'duration_ms': row[3],
                        'status': row[4],
                        'total_violations': result_data.get('total_violations', 0),
                        'has_critical': result_data.get('has_critical', False),
                        'violation_counts': result_data.get('violation_counts', {})
                    })
                return ToolOutput(success=True, data={'runs': runs, 'total_runs': len(runs)})
        except Exception as e:
            return ToolOutput(success=False, error_code='TOOL_GET_RECONCILIATION_HISTORY_FAILED', error_message=str(e))