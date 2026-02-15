"""
DiagnosisBrain - The Analyst

Responsibilities:
- Analyze errors from ScannerBrain
- Determine root cause
- Create fix strategy
- Prioritize fixes

This brain ANALYZES problems and creates a plan.
It does not execute fixes - that's RepairBrain's job.
"""
import re
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from brain.nervous_system import NervousSystem, get_nervous_system


@dataclass
class Diagnosis:
    """Diagnosis of a single error"""
    error_type: str
    priority: int
    root_cause: str
    fix_strategy: str
    fix_command: Optional[str] = None
    file_to_edit: Optional[str] = None
    line_number: Optional[int] = None
    confidence: float = 1.0  # 0-1, how confident in diagnosis


@dataclass
class FixPlan:
    """Plan for fixing all errors"""
    total_errors: int
    diagnoses: List[Diagnosis]
    recommended_order: List[int]  # Indices into diagnoses list
    estimated_fixes: int


class DiagnosisBrain:
    """
    Meta-Brain: Analyzes errors and creates fix plans

    Workflow:
    1. Receive errors from ScannerBrain
    2. Analyze each error deeply
    3. Determine root cause
    4. Create prioritized fix plan
    5. Emit DIAGNOSIS_COMPLETE event
    """

    # Known error patterns and their fixes
    ERROR_PATTERNS = {
        'missing_pydantic': {
            'pattern': r"No module named ['\"]pydantic['\"]",
            'root_cause': 'pydantic package not installed',
            'fix_strategy': 'Install pydantic package',
            'fix_command': 'pip install pydantic',
            'priority': 2
        },
        'missing_bcrypt': {
            'pattern': r"No module named ['\"]bcrypt['\"]",
            'root_cause': 'bcrypt package not installed',
            'fix_strategy': 'Install bcrypt package',
            'fix_command': 'pip install bcrypt',
            'priority': 2
        },
        'missing_cryptography': {
            'pattern': r"No module named ['\"]cryptography['\"]",
            'root_cause': 'cryptography package not installed',
            'fix_strategy': 'Install cryptography package',
            'fix_command': 'pip install cryptography',
            'priority': 2
        },
        'no_such_table': {
            'pattern': r"no such table: (\w+)",
            'root_cause': 'Database table missing',
            'fix_strategy': 'Run schema fix script',
            'fix_command': 'python3 fix_all_schema_issues.py',
            'priority': 3
        },
        'no_such_column': {
            'pattern': r"no such column: (\w+)",
            'root_cause': 'Database column missing',
            'fix_strategy': 'Run schema fix script',
            'fix_command': 'python3 fix_all_schema_issues.py',
            'priority': 3
        },
        'syntax_error': {
            'pattern': r"SyntaxError:",
            'root_cause': 'Python syntax error in code',
            'fix_strategy': 'Edit file to fix syntax',
            'fix_command': None,
            'priority': 1
        },
        'import_error': {
            'pattern': r"ImportError: cannot import name ['\"](\w+)['\"]",
            'root_cause': 'Missing class/function or circular import',
            'fix_strategy': 'Add missing export or fix circular import with TYPE_CHECKING',
            'fix_command': None,
            'priority': 2
        },
        'assertion_error': {
            'pattern': r"AssertionError:",
            'root_cause': 'Test assertion failed - logic error',
            'fix_strategy': 'Review and fix the logic in the code',
            'fix_command': None,
            'priority': 4
        },
        'type_error': {
            'pattern': r"TypeError:",
            'root_cause': 'Type mismatch in code',
            'fix_strategy': 'Fix the type issue in the code',
            'fix_command': None,
            'priority': 4
        },
        'attribute_error': {
            'pattern': r"AttributeError:",
            'root_cause': 'Missing attribute or method',
            'fix_strategy': 'Add missing attribute or fix the reference',
            'fix_command': None,
            'priority': 4
        }
    }

    def __init__(self, nervous_system: Optional[NervousSystem] = None):
        self.nervous_system = nervous_system or get_nervous_system()
        self._register_listeners()

    def _register_listeners(self):
        """Register for events from other brains"""
        pass

    def diagnose(self, errors: List[Dict[str, Any]]) -> FixPlan:
        """
        Analyze errors and create a fix plan.

        Args:
            errors: List of errors from ScannerBrain

        Returns:
            FixPlan with prioritized diagnoses
        """
        diagnoses = []

        for error in errors:
            diagnosis = self._diagnose_single_error(error)
            diagnoses.append(diagnosis)

        # Sort by priority
        diagnoses.sort(key=lambda d: d.priority)

        # Create recommended order (indices)
        recommended_order = list(range(len(diagnoses)))

        return FixPlan(
            total_errors=len(errors),
            diagnoses=diagnoses,
            recommended_order=recommended_order,
            estimated_fixes=len(diagnoses)
        )

    def _diagnose_single_error(self, error: Dict[str, Any]) -> Diagnosis:
        """Diagnose a single error"""
        error_message = error.get('error_message', '')
        error_type = error.get('error_type', 'logic')
        file_path = error.get('file_path')
        line_number = error.get('line_number')

        # Try to match known patterns
        for pattern_name, pattern_info in self.ERROR_PATTERNS.items():
            if re.search(pattern_info['pattern'], error_message):
                return Diagnosis(
                    error_type=pattern_name,
                    priority=pattern_info['priority'],
                    root_cause=pattern_info['root_cause'],
                    fix_strategy=pattern_info['fix_strategy'],
                    fix_command=pattern_info['fix_command'],
                    file_to_edit=file_path,
                    line_number=line_number,
                    confidence=0.9
                )

        # Unknown error - generic diagnosis
        return Diagnosis(
            error_type=error_type,
            priority=4,
            root_cause=f"Unknown error: {error_message[:100]}",
            fix_strategy="Review the error and fix manually",
            fix_command=None,
            file_to_edit=file_path,
            line_number=line_number,
            confidence=0.5
        )

    def get_first_fix(self, fix_plan: FixPlan) -> Optional[Diagnosis]:
        """Get the highest priority fix to execute"""
        if fix_plan.diagnoses:
            return fix_plan.diagnoses[0]
        return None

    def explain_diagnosis(self, diagnosis: Diagnosis) -> str:
        """Generate human-readable explanation of diagnosis"""
        explanation = f"""
## Diagnosis

**Error Type:** {diagnosis.error_type}
**Priority:** {diagnosis.priority} (1=highest, 4=lowest)
**Root Cause:** {diagnosis.root_cause}

### Fix Strategy
{diagnosis.fix_strategy}
"""
        if diagnosis.fix_command:
            explanation += f"\n**Command:** `{diagnosis.fix_command}`\n"

        if diagnosis.file_to_edit:
            explanation += f"\n**File:** {diagnosis.file_to_edit}"
            if diagnosis.line_number:
                explanation += f" (line {diagnosis.line_number})"

        explanation += f"\n\n**Confidence:** {diagnosis.confidence * 100:.0f}%"

        return explanation


# Convenience function
def diagnose_errors(errors: List[Dict[str, Any]]) -> FixPlan:
    """Quick diagnosis of errors"""
    brain = DiagnosisBrain()
    return brain.diagnose(errors)
