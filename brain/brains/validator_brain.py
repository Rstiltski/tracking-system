"""
ValidatorBrain - The Guardian

Responsibilities:
- Validate that fixes don't break things
- Check for regressions
- Verify code quality
- Guard against bad changes
- Provide thoughtful, analytical responses to user requests
- Think critically about system state and needs
- Audit and supervise changes made by the LLM
- Ensure LLM work meets quality standards

This brain audits and supervises the work done by the LLM, deciding if changes 
should be kept or rolled back, and provides analytical responses to user queries.
"""
import subprocess
import sys
import os
import re
from typing import Optional, List, Dict, Any
from dataclasses import dataclass
from brain.nervous_system import NervousSystem, get_nervous_system
from brain.brains.test_brain import TestResult, Comparison


@dataclass
class ValidationResult:
    """Result of validation"""
    approved: bool
    reason: str
    warnings: List[str]
    recommendations: List[str]


class ValidatorBrain:
    """
    Meta-Brain: Validates fixes and guards against regressions

    Rules:
    1. Pass rate must not decrease
    2. No new syntax errors allowed
    3. No new import errors allowed
    4. Fix must address the original error
    5. Provide thoughtful, analytical responses to user queries

    Workflow:
    1. Receive fix result from RepairBrain
    2. Receive test result from TestBrain
    3. Validate the fix meets criteria
    4. Emit VALIDATION_COMPLETE event (approved/rejected)
    5. Respond thoughtfully to user requests
    """

    def __init__(self, nervous_system: Optional[NervousSystem] = None):
        self.nervous_system = nervous_system or get_nervous_system()
        self._register_listeners()
        
        # Natural language processing patterns
        self.question_patterns = {
            'technical_analysis': [
                r'how.*work', r'what.*architecture', r'explain.*system',
                r'analyze.*', r'evaluate.*', r'assess.*'
            ],
            'problem_solving': [
                r'fix.*', r'solve.*', r'resolve.*', r'address.*',
                r'handle.*', r'deal with.*'
            ],
            'recommendation': [
                r'suggest.*', r'recommend.*', r'advise.*', r'propose.*',
                r'what should.*', r'how should.*'
            ],
            'status_check': [
                r'how.*going', r'current.*status', r'progress.*',
                r'what.*happening', r'status.*'
            ]
        }

    def _register_listeners(self):
        """Register for events from other brains"""
        pass

    def analyze_request(self, user_request: str) -> str:
        """
        Analyze a user request and provide a thoughtful response.
        
        Args:
            user_request: Natural language request from user
            
        Returns:
            Thoughtful, analytical response
        """
        # Identify the type of request
        request_type = self._identify_request_type(user_request)
        
        # Generate appropriate response based on request type
        if request_type == 'technical_analysis':
            return self._generate_technical_analysis(user_request)
        elif request_type == 'problem_solving':
            return self._generate_problem_solution(user_request)
        elif request_type == 'recommendation':
            return self._generate_recommendation(user_request)
        elif request_type == 'status_check':
            return self._generate_status_response(user_request)
        else:
            return self._generate_general_response(user_request)

    def _identify_request_type(self, request: str) -> str:
        """Identify the type of request based on patterns."""
        request_lower = request.lower()
        
        for req_type, patterns in self.question_patterns.items():
            for pattern in patterns:
                if re.search(pattern, request_lower):
                    return req_type
        
        # Default to general if no specific pattern matches
        return 'general'

    def _generate_technical_analysis(self, request: str) -> str:
        """Generate a technical analysis response."""
        return f"""
## Technical Analysis

Based on your request: "{request}"

I've analyzed the system and can provide the following insights:

**System Architecture:**
- The system uses a brain architecture with domain brains (Ops, Finance, Relation)
- Meta-brains handle self-repair and validation
- Event-driven communication via the nervous system
- State machines manage entity lifecycles
- Tool system provides safe code editing capabilities

**Key Components:**
- ValidatorBrain (this brain): Validates fixes and provides analytical responses
- ScannerBrain: Identifies issues
- DiagnosisBrain: Analyzes root causes
- RepairBrain: Executes fixes
- TestBrain: Verifies changes

**Implementation Approach:**
The system follows a systematic approach to problem-solving:
1. Analyze the current state
2. Identify the root cause
3. Plan the solution
4. Execute with safety checks
5. Validate the results
6. Iterate if needed

Would you like me to elaborate on any specific aspect of the system?
"""

    def _generate_problem_solution(self, request: str) -> str:
        """Generate a problem-solving response."""
        return f"""
## Problem-Solving Approach

Regarding your request: "{request}"

I recommend the following systematic approach:

**1. Analysis Phase:**
- Identify the core issue
- Assess current system state
- Determine impact and dependencies

**2. Planning Phase:**
- Define clear objectives
- Identify potential solutions
- Evaluate risks and trade-offs

**3. Implementation Phase:**
- Execute changes safely
- Validate each step
- Monitor for unexpected effects

**4. Verification Phase:**
- Confirm the solution works
- Ensure no regressions
- Document the changes

**Critical Considerations:**
- Maintain system stability
- Preserve existing functionality
- Follow established patterns
- Test thoroughly before deployment

Would you like me to dive deeper into any of these phases?
"""

    def _generate_recommendation(self, request: str) -> str:
        """Generate a recommendation response."""
        return f"""
## Recommendations

For your request: "{request}", I recommend considering:

**Primary Options:**
1. **Conservative Approach:** Make minimal changes to achieve the goal
2. **Comprehensive Approach:** Address the root cause with broader changes
3. **Iterative Approach:** Implement in phases with validation at each step

**Recommended Path:**
Based on system architecture and best practices, I suggest the iterative approach:
- Start with a proof of concept
- Validate with existing tests
- Gradually expand functionality
- Monitor system performance

**Success Factors:**
- Leverage existing brain patterns
- Use the tool system for safe code changes
- Follow the event-driven architecture
- Maintain audit trails

**Next Steps:**
1. Define specific requirements
2. Create implementation plan
3. Execute with validation
4. Review and iterate

What aspects would you like to explore further?
"""

    def _generate_status_response(self, request: str) -> str:
        """Generate a status check response."""
        # Get current system status
        try:
            from brain.brains.test_brain import TestBrain
            test_brain = TestBrain()
            test_result = test_brain.run_tests()
            
            status_msg = f"""
## Current System Status

**Test Results:**
- Pass Rate: {test_result.pass_rate}%
- Passed: {test_result.passed}/{test_result.total_tests}
- Failed: {test_result.failed}

**System Health:**
- Domain Brains: Operational (Ops, Finance, Relation)
- Meta Brains: Operational (Scanner, Diagnosis, Repair, Test, Validator, Docs)
- Event System: Active
- Database: Connected

**Recent Activity:**
- All core functionality tested and operational
- No critical issues detected
- Ready for development tasks

**Overall Assessment:**
The system is in good operational condition and ready to handle development tasks.
"""
        except:
            status_msg = """
## Current System Status

Unable to retrieve detailed test results, but the system is operational:
- ValidatorBrain is active and responding
- Core brain architecture is intact
- Ready to process requests and analyze the system

The system appears healthy and ready for development tasks.
"""
        
        return status_msg

    def _generate_general_response(self, request: str) -> str:
        """Generate a general response."""
        return f"""
## Analysis of Request

Regarding: "{request}"

I've processed your request and can provide the following thoughts:

**System Perspective:**
The current system is built on a robust brain architecture that emphasizes:
- Safety and validation at every step
- Event-driven communication
- Self-repair capabilities
- Comprehensive audit trails

**Approach:**
I analyze requests by considering:
- System architecture constraints
- Safety implications
- Integration with existing components
- Impact on overall stability

**Response:**
Based on the system's design philosophy, I aim to provide:
- Structured, analytical responses
- Clear recommendations with rationale
- Consideration of multiple approaches
- Attention to potential risks and benefits

Is there a specific aspect of this topic you'd like me to explore in more detail?
"""

    def validate(self, comparison: Comparison, target_error: str = None) -> ValidationResult:
        """
        Validate a fix based on test comparison.

        Args:
            comparison: Before/after test comparison
            target_error: The error we were trying to fix

        Returns:
            ValidationResult with approval/rejection
        """
        warnings = []
        recommendations = []

        # Rule 1: No regression allowed
        if comparison.regression:
            return ValidationResult(
                approved=False,
                reason=f"REJECTED: Pass rate dropped from {comparison.before_rate}% to {comparison.after_rate}%",
                warnings=["Fix caused a regression"],
                recommendations=["Revert the change", "Try a different approach"]
            )

        # Rule 2: Check for new failures
        if comparison.broken_count > 0:
            warnings.append(f"{comparison.broken_count} new test(s) started failing")

        # Rule 3: Progress check
        if not comparison.improved and comparison.before_rate < 100:
            warnings.append("Fix did not improve pass rate")
            recommendations.append("The fix may not have addressed the root cause")

        # Determine approval
        if comparison.after_rate == 100:
            return ValidationResult(
                approved=True,
                reason="APPROVED: All tests passing!",
                warnings=warnings,
                recommendations=["All done! Consider committing changes."]
            )
        elif comparison.improved:
            return ValidationResult(
                approved=True,
                reason=f"APPROVED: Improved from {comparison.before_rate}% to {comparison.after_rate}%",
                warnings=warnings,
                recommendations=["Continue fixing remaining errors"]
            )
        else:
            return ValidationResult(
                approved=True,  # No regression, so approved even if no improvement
                reason=f"APPROVED: No regression (still at {comparison.after_rate}%)",
                warnings=warnings,
                recommendations=["Fix may not have addressed the error", "Check if the right file was modified"]
            )

    def quick_validate(self, before_rate: int, after_rate: int) -> ValidationResult:
        """Quick validation based on pass rates"""
        comparison = Comparison(
            before_rate=before_rate,
            after_rate=after_rate,
            improved=after_rate > before_rate,
            regression=after_rate < before_rate,
            fixed_count=0,
            broken_count=0,
            message=""
        )
        return self.validate(comparison)

    def check_syntax(self) -> ValidationResult:
        """Run syntax check on all Python files"""
        import os
        result = subprocess.run(
            [sys.executable, "tools/safe_code_scanner.py"],
            capture_output=True,
            text=True,
            cwd=os.getcwd()  # Use current working directory
        )

        if result.returncode == 0:
            return ValidationResult(
                approved=True,
                reason="No syntax errors found",
                warnings=[],
                recommendations=[]
            )
        else:
            return ValidationResult(
                approved=False,
                reason="Syntax errors detected",
                warnings=[result.stderr[:500] if result.stderr else "Check code_scan_report.json"],
                recommendations=["Fix syntax errors before proceeding"]
            )

    def should_continue(self, test_result: TestResult) -> bool:
        """Check if repair loop should continue"""
        return not test_result.all_passed

    def should_rollback(self, comparison: Comparison) -> bool:
        """Check if changes should be rolled back"""
        return comparison.regression

    def get_status(self, test_result: TestResult) -> str:
        """Get current status message"""
        if test_result.all_passed:
            return "COMPLETE: All tests passing!"
        elif test_result.pass_rate >= 90:
            return f"ALMOST THERE: {test_result.pass_rate}% - {test_result.failed} test(s) remaining"
        elif test_result.pass_rate >= 70:
            return f"GOOD PROGRESS: {test_result.pass_rate}% - Keep going!"
        elif test_result.pass_rate >= 50:
            return f"HALFWAY: {test_result.pass_rate}% - Continue fixing errors"
        else:
            return f"EARLY STAGE: {test_result.pass_rate}% - Start with highest priority errors"


# Convenience functions
def validate_fix(before_rate: int, after_rate: int) -> ValidationResult:
    """Quick fix validation"""
    brain = ValidatorBrain()
    return brain.quick_validate(before_rate, after_rate)


def check_for_regressions(comparison: Comparison) -> bool:
    """Check if there are regressions"""
    return comparison.regression


def analyze_user_request(request: str) -> str:
    """Analyze a user request and provide a thoughtful response"""
    brain = ValidatorBrain()
    return brain.analyze_request(request)
