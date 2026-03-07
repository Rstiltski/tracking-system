# 📊 Monitoring - System Health and Anomaly Detection

**Comprehensive monitoring for system health, anomaly detection, and diagnostics.**

---

## Overview

The `brain/monitoring/` directory provides comprehensive monitoring capabilities including system health checks, anomaly detection, and diagnostic tools.

---

## Components

| File | Purpose |
|------|---------|
| `health_checker.py` | System health monitoring |
| `anomaly_detector.py` | Anomaly detection in system behavior |

---

## Quick Start

### Health Check

```python
from brain.monitoring.health_checker import HealthChecker

checker = HealthChecker()

# Run all health checks
health = checker.run_all_checks()

print(f"Status: {health.status.value}")
print(f"Score: {health.score * 100:.1f}%")

# Print formatted report
checker.print_health_report()
```

### Anomaly Detection

```python
from brain.monitoring.anomaly_detector import AnomalyDetector

detector = AnomalyDetector()

# Detect anomalies in last 24 hours
report = detector.detect_all(hours=24)

print(f"Total anomalies: {len(report.anomalies)}")
print(f"Critical: {len(report.critical_anomalies)}")

# Print formatted report
detector.print_report(report)
```

---

## Health Checks

### Default Checks

| Check | Description |
|-------|-------------|
| `database_connection` | Database connectivity and size |
| `audit_log_status` | Audit log health and entries |
| `error_rate` | System error rate |
| `command_performance` | Command execution speed |
| `table_integrity` | Database integrity check |

### Health Status Levels

| Status | Description |
|--------|-------------|
| `HEALTHY` | All systems operational |
| `DEGRADED` | Some issues, but operational |
| `UNHEALTHY` | Significant issues |
| `CRITICAL` | System is failing |

### Custom Health Checks

```python
from brain.monitoring.health_checker import HealthChecker, HealthCheckResult, HealthStatus

checker = HealthChecker()

# Define custom check
def check_custom_metric() -> HealthCheckResult:
    # Your check logic
    return HealthCheckResult(
        name="custom_check",
        status=HealthStatus.HEALTHY,
        message="Custom check passed",
        severity=CheckSeverity.INFO
    )

# Register it
checker.register_check("custom_check", check_custom_metric)
```

---

## Anomaly Detection

### Anomaly Types

| Type | Description |
|------|-------------|
| `ERROR_SPIKE` | Sudden increase in errors |
| `PERFORMANCE_DEGRADATION` | Slower response times |
| `UNUSUAL_PATTERN` | Abnormal command patterns |
| `RULE_VIOLATION` | Repeated rule violations |
| `VOLUME_ANOMALY` | Unusual request volume |
| `STATE_ANOMALY` | Invalid state transitions |

### Severity Levels

| Level | Description |
|-------|-------------|
| `LOW` | Minor deviation |
| `MEDIUM` | Notable issue |
| `HIGH` | Significant problem |
| `CRITICAL` | Immediate attention required |

### Detection Thresholds

| Metric | Threshold |
|--------|-----------|
| Error rate spike | >2x baseline |
| Performance degradation | >50% slower |
| Volume anomaly | >3x baseline |
| Repeated failures | >5 occurrences |

---

## Traceback Analyzer

For automated root cause analysis, use the standalone traceback analyzer:

```bash
# Analyze specific error
python brain/tools/traceback_analyzer.py --error <command_id>

# Analyze last failed command
python brain/tools/traceback_analyzer.py --last-failed

# Analyze all errors in date range
python brain/tools/traceback_analyzer.py --analyze-all --since "2026-02-01"

# Get entity history
python brain/tools/traceback_analyzer.py --entity-type invoice --entity-id 789
```

### Output Format

```
=================================================================
                    TRACEBACK ANALYSIS REPORT
=================================================================
Command ID: 660e8400-e29b-41d4-a716-446655440001
Status: FAILED
Error Category: INVARIANT_VIOLATION
Confidence: 95%

ROOT CAUSE:
-> Payment amount exceeds remaining balance

CHAIN OF EVENTS (5 events):
-----------------------------------------------------------------
#    Time                 Command              Impact
-----------------------------------------------------------------
 1   2026-01-14 09:00:00 InvoiceCreate        Created invoice
 2   2026-01-14 10:00:00 InvoiceSend          State -> SENT
 3   2026-01-14 14:00:00 PaymentRecord        State -> PAID
-----------------------------------------------------------------

RECOMMENDATIONS:
1. Verify balance before retry
   Check the current balance before attempting payment
2. Adjust payment amount
   Ensure payment amount does not exceed remaining balance

=================================================================
```

---

## Integration with Brain

The monitoring system integrates with the Brain architecture:

```python
from brain.core.brain import Brain
from brain.monitoring.health_checker import HealthChecker

brain = Brain()
checker = HealthChecker()

# Check health before critical operations
health = checker.run_all_checks()
if health.status == HealthStatus.CRITICAL:
    # Delay or reject operation
    pass
```

---

## Cross-References

| Topic | File |
|-------|------|
| AI entry point | `../AI_START_HERE.md` |
| Security playbook | `../SECURITY_PLAYBOOK.md` |
| Audit Log | `brain/audit/README.md` |
| Traceback Analyzer | `brain/tools/traceback_analyzer.py` |
| Rules System | `brain/rules/README.md` |

---

**Last Updated:** March 2026
