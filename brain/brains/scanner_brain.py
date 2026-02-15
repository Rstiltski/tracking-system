"""
ScannerBrain - The Inspector

Responsibilities:
- Run tests to find errors
- Scan code for syntax issues
- Detect import problems
- Report findings to other brains

This brain FINDS problems but does not FIX them.
It emits events that other brains listen for.
"""
import subprocess
import sys
import re
from typing import Optional, List, Dict, Any
from dataclasses import dataclass
from brain.nervous_system import NervousSystem, get_nervous_system


@dataclass
class ScanResult:
    """Result of a scan operation"""
    total_tests: int
    passed: int
    failed: int
    pass_rate: int
    errors: List[Dict[str, Any]]
    first_error: Optional[Dict[str, Any]] = None


@dataclass
class ErrorInfo:
    """Information about a single error"""
    test_name: str
    error_type: str  # syntax, import, database, logic
    error_message: str
    file_path: Optional[str] = None
    line_number: Optional[int] = None
    priority: int = 4  # 1=syntax, 2=import, 3=database, 4=logic


class ScannerBrain:
    """
    Meta-Brain: Finds errors in the codebase

    Workflow:
    1. Run all tests
    2. Parse output to find errors
    3. Classify each error by type
    4. Emit ERRORS_FOUND event with details
    """

    def __init__(self, nervous_system: Optional[NervousSystem] = None):
        self.nervous_system = nervous_system or get_nervous_system()
        self._register_listeners()

    def _register_listeners(self):
        """Register for events from other brains"""
        # ScannerBrain can be triggered by SCAN_REQUESTED event
        pass

    def scan(self) -> ScanResult:
        """
        Run all tests and return scan results.

        Returns:
            ScanResult with all errors found
        """
        # Run the test suite
        import os
        result = subprocess.run(
            [sys.executable, "run_all_tests.py"],
            capture_output=True,
            text=True,
            cwd=os.getcwd()  # Use current working directory
        )

        output = result.stdout + result.stderr

        # Parse the output
        return self._parse_test_output(output)

    def _parse_test_output(self, output: str) -> ScanResult:
        """Parse test runner output to extract errors"""
        errors = []

        # Find all failing tests
        # Pattern: "Testing test_name... ❌ FAIL"
        fail_pattern = r"Testing (\w+)\.\.\. ❌ FAIL"
        error_section_pattern = r"--- ERROR OUTPUT.*?---\s*(.*?)\s*--- END ERROR OUTPUT"

        # Find pass rate
        pass_rate_match = re.search(r"Pass Rate:\s*(\d+)%", output)
        pass_rate = int(pass_rate_match.group(1)) if pass_rate_match else 0

        # Find test counts
        tests_match = re.search(r"Tests Run:\s*(\d+)", output)
        passed_match = re.search(r"Passed:\s*(\d+)", output)
        failed_match = re.search(r"Failed:\s*(\d+)", output)

        total_tests = int(tests_match.group(1)) if tests_match else 0
        passed = int(passed_match.group(1)) if passed_match else 0
        failed = int(failed_match.group(1)) if failed_match else 0

        # Extract each error
        current_test = None
        lines = output.split('\n')
        in_error_section = False
        error_lines = []

        for line in lines:
            # Check for test failure
            fail_match = re.search(fail_pattern, line)
            if fail_match:
                current_test = fail_match.group(1)
                continue

            # Check for error section start
            if "--- ERROR OUTPUT" in line:
                in_error_section = True
                error_lines = []
                continue

            # Check for error section end
            if "--- END ERROR OUTPUT" in line:
                in_error_section = False
                if current_test and error_lines:
                    error_text = '\n'.join(error_lines)
                    error_info = self._classify_error(current_test, error_text)
                    errors.append(error_info)
                continue

            # Collect error lines
            if in_error_section:
                error_lines.append(line.strip())

        # Sort errors by priority
        errors.sort(key=lambda e: e.get('priority', 4))

        return ScanResult(
            total_tests=total_tests,
            passed=passed,
            failed=failed,
            pass_rate=pass_rate,
            errors=errors,
            first_error=errors[0] if errors else None
        )

    def _classify_error(self, test_name: str, error_text: str) -> Dict[str, Any]:
        """Classify an error by type and extract details"""
        error_info = {
            'test_name': test_name,
            'error_message': error_text,
            'error_type': 'logic',
            'priority': 4,
            'file_path': None,
            'line_number': None
        }

        # Check for syntax error (priority 1)
        if 'SyntaxError' in error_text:
            error_info['error_type'] = 'syntax'
            error_info['priority'] = 1

        # Check for missing module (priority 2)
        elif 'ModuleNotFoundError' in error_text:
            error_info['error_type'] = 'missing_package'
            error_info['priority'] = 2
            # Extract module name
            match = re.search(r"No module named ['\"](\w+)['\"]", error_text)
            if match:
                error_info['missing_module'] = match.group(1)

        # Check for import error (priority 2)
        elif 'ImportError' in error_text:
            error_info['error_type'] = 'import'
            error_info['priority'] = 2

        # Check for database error (priority 3)
        elif 'OperationalError' in error_text or 'no such table' in error_text or 'no such column' in error_text:
            error_info['error_type'] = 'database'
            error_info['priority'] = 3

        # Extract file path and line number
        file_match = re.search(r'File "([^"]+)", line (\d+)', error_text)
        if file_match:
            error_info['file_path'] = file_match.group(1)
            error_info['line_number'] = int(file_match.group(2))

        return error_info

    def get_fix_suggestion(self, error: Dict[str, Any]) -> str:
        """Get a fix suggestion for an error"""
        error_type = error.get('error_type', 'logic')

        if error_type == 'syntax':
            return f"Fix syntax error in {error.get('file_path', 'unknown')} at line {error.get('line_number', '?')}"

        elif error_type == 'missing_package':
            module = error.get('missing_module', 'unknown')
            return f"pip install {module}"

        elif error_type == 'import':
            return "Check if the class/function exists in the module. If circular import, use TYPE_CHECKING."

        elif error_type == 'database':
            return "python3 fix_all_schema_issues.py"

        else:
            return f"Review logic error in {error.get('file_path', 'unknown')}"


# Convenience function
def scan_for_errors() -> ScanResult:
    """Quick scan for errors"""
    brain = ScannerBrain()
    return brain.scan()
