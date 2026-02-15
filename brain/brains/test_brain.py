"""
TestBrain - The Tester

Responsibilities:
- Run test suite
- Interpret results
- Track pass rate changes
- Report test outcomes

This brain verifies that fixes work.
"""
import subprocess
import sys
import re
from typing import Optional, List, Dict, Any
from dataclasses import dataclass
from brain.nervous_system import NervousSystem, get_nervous_system


@dataclass
class TestResult:
    """Result of running tests"""
    total_tests: int
    passed: int
    failed: int
    pass_rate: int
    all_passed: bool
    failing_tests: List[str]
    raw_output: str


@dataclass
class Comparison:
    """Comparison between two test runs"""
    before_rate: int
    after_rate: int
    improved: bool
    regression: bool
    fixed_count: int
    broken_count: int
    message: str


class TestBrain:
    """
    Meta-Brain: Runs tests and interprets results

    Workflow:
    1. Run the full test suite
    2. Parse results
    3. Compare to previous run (if available)
    4. Emit TEST_COMPLETE event
    """

    def __init__(self, nervous_system: Optional[NervousSystem] = None):
        self.nervous_system = nervous_system or get_nervous_system()
        self.last_result: Optional[TestResult] = None
        self._register_listeners()

    def _register_listeners(self):
        """Register for events from other brains"""
        pass

    def run_tests(self) -> TestResult:
        """
        Run all tests and return results.

        Returns:
            TestResult with pass/fail counts
        """
        import os
        result = subprocess.run(
            [sys.executable, "run_all_tests.py"],
            capture_output=True,
            text=True,
            cwd=os.getcwd()  # Use current working directory
        )

        output = result.stdout + result.stderr
        test_result = self._parse_output(output)

        # Store for comparison
        self.last_result = test_result

        return test_result

    def _parse_output(self, output: str) -> TestResult:
        """Parse test runner output"""
        # Find counts
        tests_match = re.search(r"Tests Run:\s*(\d+)", output)
        passed_match = re.search(r"Passed:\s*(\d+)", output)
        failed_match = re.search(r"Failed:\s*(\d+)", output)
        pass_rate_match = re.search(r"Pass Rate:\s*(\d+)%", output)

        total = int(tests_match.group(1)) if tests_match else 0
        passed = int(passed_match.group(1)) if passed_match else 0
        failed = int(failed_match.group(1)) if failed_match else 0
        pass_rate = int(pass_rate_match.group(1)) if pass_rate_match else 0

        # Find failing test names
        failing_tests = []
        fail_pattern = r"Testing (\w+)\.\.\. ❌ FAIL"
        for match in re.finditer(fail_pattern, output):
            failing_tests.append(match.group(1))

        return TestResult(
            total_tests=total,
            passed=passed,
            failed=failed,
            pass_rate=pass_rate,
            all_passed=(failed == 0 and total > 0),
            failing_tests=failing_tests,
            raw_output=output
        )

    def compare(self, before: TestResult, after: TestResult) -> Comparison:
        """Compare two test results"""
        before_rate = before.pass_rate
        after_rate = after.pass_rate

        improved = after_rate > before_rate
        regression = after_rate < before_rate

        # Count fixes and breaks
        before_failing = set(before.failing_tests)
        after_failing = set(after.failing_tests)

        fixed = before_failing - after_failing
        broken = after_failing - before_failing

        # Create message
        if after.all_passed:
            message = "ALL TESTS PASSING! You're done!"
        elif improved:
            message = f"Improved from {before_rate}% to {after_rate}% (+{after_rate - before_rate}%)"
        elif regression:
            message = f"REGRESSION: Dropped from {before_rate}% to {after_rate}%"
        else:
            message = f"No change: Still at {after_rate}%"

        return Comparison(
            before_rate=before_rate,
            after_rate=after_rate,
            improved=improved,
            regression=regression,
            fixed_count=len(fixed),
            broken_count=len(broken),
            message=message
        )

    def verify_fix(self, before_rate: int) -> Comparison:
        """
        Run tests and compare to previous pass rate.

        Args:
            before_rate: Pass rate before the fix

        Returns:
            Comparison showing if fix worked
        """
        # First, run tests to get the current total test count
        current_result = self.run_tests()
        total_tests = current_result.total_tests

        # Create a "before" result from the rate using the actual test count
        before = TestResult(
            total_tests=total_tests,
            passed=int(total_tests * before_rate / 100),
            failed=total_tests - int(total_tests * before_rate / 100),
            pass_rate=before_rate,
            all_passed=False,
            failing_tests=[],
            raw_output=""
        )

        # Compare to current result
        return self.compare(before, current_result)

    def is_complete(self, result: TestResult) -> bool:
        """Check if all tests pass (repair complete)"""
        return result.all_passed

    def get_summary(self, result: TestResult) -> str:
        """Generate human-readable summary"""
        status = "COMPLETE" if result.all_passed else "IN PROGRESS"

        summary = f"""
## Test Results: {status}

**Pass Rate:** {result.pass_rate}%
**Tests:** {result.passed}/{result.total_tests} passing

"""
        if result.failing_tests:
            summary += "**Failing Tests:**\n"
            for test in result.failing_tests:
                summary += f"- {test}\n"

        if result.all_passed:
            summary += "\n**ALL TESTS PASSED!**\n"
        else:
            summary += f"\n**Next:** Fix the first failing test ({result.failing_tests[0] if result.failing_tests else 'unknown'})\n"

        return summary


# Convenience functions
def run_all_tests() -> TestResult:
    """Quick test run"""
    brain = TestBrain()
    return brain.run_tests()


def verify_fix_worked(before_rate: int) -> Comparison:
    """Verify a fix improved things"""
    brain = TestBrain()
    return brain.verify_fix(before_rate)
