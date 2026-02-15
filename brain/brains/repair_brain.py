"""
RepairBrain - The Fixer

Responsibilities:
- Execute ONE fix at a time
- Run commands (pip install, etc.)
- Track what was changed
- Report results

CRITICAL: This brain fixes ONE error, then stops.
Never fix multiple errors before verification.
"""
import subprocess
import sys
import os
from typing import Optional, Dict, Any, Tuple
from dataclasses import dataclass
from brain.nervous_system import NervousSystem, get_nervous_system
from brain.brains.diagnosis_brain import Diagnosis


@dataclass
class RepairResult:
    """Result of a repair operation"""
    success: bool
    action_taken: str
    command_output: Optional[str] = None
    error_message: Optional[str] = None
    file_modified: Optional[str] = None
    needs_verification: bool = True


class RepairBrain:
    """
    Meta-Brain: Executes fixes one at a time

    RULE: ONE FIX AT A TIME
    - Execute one fix
    - Report result
    - Wait for verification before next fix

    Workflow:
    1. Receive diagnosis from DiagnosisBrain
    2. Execute the fix (command or code change)
    3. Emit FIX_APPLIED event
    4. Wait for TestBrain to verify
    """

    def __init__(self, nervous_system: Optional[NervousSystem] = None):
        self.nervous_system = nervous_system or get_nervous_system()
        self.repair_history = []
        self._register_listeners()

    def _register_listeners(self):
        """Register for events from other brains"""
        pass

    def repair(self, diagnosis: Diagnosis) -> RepairResult:
        """
        Execute a single fix based on diagnosis.

        Args:
            diagnosis: Diagnosis from DiagnosisBrain

        Returns:
            RepairResult indicating success/failure
        """
        # Log the repair attempt
        self.repair_history.append({
            'diagnosis': diagnosis,
            'status': 'attempting'
        })

        # Route to appropriate fix method
        if diagnosis.fix_command:
            return self._execute_command(diagnosis)
        elif diagnosis.error_type == 'syntax':
            return self._report_manual_fix_needed(diagnosis, "syntax")
        elif diagnosis.error_type == 'import':
            return self._report_manual_fix_needed(diagnosis, "import")
        else:
            return self._report_manual_fix_needed(diagnosis, "logic")

    def _execute_command(self, diagnosis: Diagnosis) -> RepairResult:
        """Execute a command-based fix"""
        command = diagnosis.fix_command

        try:
            # Run the command
            import os
            result = subprocess.run(
                command.split(),
                capture_output=True,
                text=True,
                cwd=os.getcwd(),  # Use current working directory
                timeout=120  # 2 minute timeout
            )

            if result.returncode == 0:
                return RepairResult(
                    success=True,
                    action_taken=f"Executed: {command}",
                    command_output=result.stdout,
                    needs_verification=True
                )
            else:
                return RepairResult(
                    success=False,
                    action_taken=f"Attempted: {command}",
                    command_output=result.stdout,
                    error_message=result.stderr,
                    needs_verification=True
                )

        except subprocess.TimeoutExpired:
            return RepairResult(
                success=False,
                action_taken=f"Attempted: {command}",
                error_message="Command timed out after 120 seconds",
                needs_verification=False
            )
        except Exception as e:
            return RepairResult(
                success=False,
                action_taken=f"Attempted: {command}",
                error_message=str(e),
                needs_verification=False
            )

    def _report_manual_fix_needed(self, diagnosis: Diagnosis, fix_type: str) -> RepairResult:
        """Report that a manual fix is needed"""
        if fix_type == "syntax":
            action = f"""
MANUAL FIX REQUIRED: Syntax Error

File: {diagnosis.file_to_edit}
Line: {diagnosis.line_number}

To fix:
1. Read the file at the specified line
2. Fix the syntax error (missing parenthesis, bad indent, etc.)
3. Save the file
4. Run tests to verify
"""
        elif fix_type == "import":
            action = f"""
MANUAL FIX REQUIRED: Import Error

File: {diagnosis.file_to_edit}
Line: {diagnosis.line_number}

To fix:
1. Check if the class/function exists in the source module
2. If missing, add it to the source module
3. If circular import, use TYPE_CHECKING:

   from typing import TYPE_CHECKING
   if TYPE_CHECKING:
       from module import Class

4. Run tests to verify
"""
        else:
            action = f"""
MANUAL FIX REQUIRED: Logic Error

File: {diagnosis.file_to_edit}
Line: {diagnosis.line_number}

Root cause: {diagnosis.root_cause}

To fix:
1. Read the error message carefully
2. Review the code at the specified location
3. Fix the logic error
4. Run tests to verify
"""

        return RepairResult(
            success=False,  # Manual intervention needed
            action_taken=action,
            needs_verification=True,
            file_modified=diagnosis.file_to_edit
        )

    def install_package(self, package_name: str) -> RepairResult:
        """Convenience method to install a Python package"""
        diagnosis = Diagnosis(
            error_type='missing_package',
            priority=2,
            root_cause=f'{package_name} not installed',
            fix_strategy=f'Install {package_name}',
            fix_command=f'pip install {package_name}'
        )
        return self.repair(diagnosis)

    def fix_database(self) -> RepairResult:
        """Convenience method to fix database issues"""
        diagnosis = Diagnosis(
            error_type='database',
            priority=3,
            root_cause='Database schema issues',
            fix_strategy='Run schema fix script',
            fix_command='python3 fix_all_schema_issues.py'
        )
        return self.repair(diagnosis)

    def get_repair_history(self) -> list:
        """Get history of all repair attempts"""
        return self.repair_history

    def explain_result(self, result: RepairResult) -> str:
        """Generate human-readable explanation of repair result"""
        status = "SUCCESS" if result.success else "NEEDS ATTENTION"

        explanation = f"""
## Repair Result: {status}

**Action Taken:**
{result.action_taken}
"""
        if result.command_output:
            explanation += f"\n**Output:**\n```\n{result.command_output[:500]}\n```\n"

        if result.error_message:
            explanation += f"\n**Error:**\n```\n{result.error_message[:500]}\n```\n"

        if result.needs_verification:
            explanation += "\n**Next Step:** Run tests to verify the fix worked.\n"

        return explanation


# Convenience functions
def repair_error(diagnosis: Diagnosis) -> RepairResult:
    """Quick repair of a single error"""
    brain = RepairBrain()
    return brain.repair(diagnosis)


def install_missing_package(package: str) -> RepairResult:
    """Quick install of a missing package"""
    brain = RepairBrain()
    return brain.install_package(package)
