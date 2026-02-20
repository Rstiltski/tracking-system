"""
Health Checker - System Health Monitoring

This module provides comprehensive health checks for:
- Database connectivity
- Rule system integrity
- Audit log health
- Policy and invariant status
- Performance metrics

📚 REQUIRED READING BEFORE MODIFICATION:
- brain/design/06_audit_schema.md
"""

import sqlite3
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Callable
from pathlib import Path
import time


class HealthStatus(Enum):
    """Health check status levels."""
    HEALTHY = "HEALTHY"          # All systems operational
    DEGRADED = "DEGRADED"        # Some issues, but operational
    UNHEALTHY = "UNHEALTHY"      # Significant issues
    CRITICAL = "CRITICAL"        # System is failing


class CheckSeverity(Enum):
    """Severity levels for health check issues."""
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


@dataclass
class HealthCheckResult:
    """Result of a single health check."""
    name: str
    status: HealthStatus
    message: str
    severity: CheckSeverity
    details: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    duration_ms: int = 0
    
    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "status": self.status.value,
            "message": self.message,
            "severity": self.severity.value,
            "details": self.details,
            "timestamp": self.timestamp.isoformat(),
            "duration_ms": self.duration_ms
        }


@dataclass
class SystemHealth:
    """Overall system health status."""
    status: HealthStatus
    checks: List[HealthCheckResult]
    score: float  # 0.0 to 1.0
    checked_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict:
        return {
            "status": self.status.value,
            "checks": [c.to_dict() for c in self.checks],
            "score": self.score,
            "checked_at": self.checked_at.isoformat()
        }
    
    @property
    def healthy_checks(self) -> List[HealthCheckResult]:
        return [c for c in self.checks if c.status == HealthStatus.HEALTHY]
    
    @property
    def unhealthy_checks(self) -> List[HealthCheckResult]:
        return [c for c in self.checks if c.status != HealthStatus.HEALTHY]


class HealthChecker:
    """
    Comprehensive system health checker.
    
    Performs health checks on:
    - Database connectivity and integrity
    - Audit log status
    - Rule system status
    - Policy engine status
    - Performance metrics
    """
    
    def __init__(self, db_path: Optional[str] = None):
        """
        Initialize the health checker.
        
        Args:
            db_path: Path to SQLite database
        """
        if db_path is None:
            project_root = Path(__file__).parent.parent.parent
            db_path = str(project_root / "tracking.db")
        
        self.db_path = db_path
        self._conn = None
        self._checks: Dict[str, Callable[[], HealthCheckResult]] = {}
        self._register_default_checks()
    
    @property
    def conn(self):
        """Lazy database connection."""
        if self._conn is None:
            self._conn = sqlite3.connect(self.db_path)
            self._conn.row_factory = sqlite3.Row
        return self._conn
    
    def close(self):
        """Close database connection."""
        if self._conn:
            self._conn.close()
            self._conn = None
    
    def _register_default_checks(self):
        """Register default health checks."""
        self._checks = {
            "database_connection": self._check_database_connection,
            "audit_log_status": self._check_audit_log_status,
            "error_rate": self._check_error_rate,
            "command_performance": self._check_command_performance,
            "table_integrity": self._check_table_integrity,
        }
    
    def register_check(self, name: str, check_func: Callable[[], HealthCheckResult]):
        """Register a custom health check."""
        self._checks[name] = check_func
    
    def run_check(self, name: str) -> Optional[HealthCheckResult]:
        """Run a single health check by name."""
        if name not in self._checks:
            return None
        
        start_time = time.time()
        try:
            result = self._checks[name]()
            result.duration_ms = int((time.time() - start_time) * 1000)
            return result
        except Exception as e:
            return HealthCheckResult(
                name=name,
                status=HealthStatus.UNHEALTHY,
                message=f"Check failed with error: {str(e)}",
                severity=CheckSeverity.ERROR,
                duration_ms=int((time.time() - start_time) * 1000)
            )
    
    def run_all_checks(self) -> SystemHealth:
        """Run all registered health checks."""
        checks = []
        
        for name in self._checks:
            result = self.run_check(name)
            if result:
                checks.append(result)
        
        # Determine overall status
        status = HealthStatus.HEALTHY
        if any(c.status == HealthStatus.CRITICAL for c in checks):
            status = HealthStatus.CRITICAL
        elif any(c.status == HealthStatus.UNHEALTHY for c in checks):
            status = HealthStatus.UNHEALTHY
        elif any(c.status == HealthStatus.DEGRADED for c in checks):
            status = HealthStatus.DEGRADED
        
        # Calculate health score
        score = len([c for c in checks if c.status == HealthStatus.HEALTHY]) / len(checks) if checks else 0.0
        
        return SystemHealth(
            status=status,
            checks=checks,
            score=score
        )
    
    def _check_database_connection(self) -> HealthCheckResult:
        """Check database connectivity."""
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT 1")
            cursor.fetchone()
            
            # Get database size
            cursor.execute("PRAGMA page_count")
            page_count = cursor.fetchone()[0]
            cursor.execute("PRAGMA page_size")
            page_size = cursor.fetchone()[0]
            db_size_mb = (page_count * page_size) / (1024 * 1024)
            
            return HealthCheckResult(
                name="database_connection",
                status=HealthStatus.HEALTHY,
                message="Database connection successful",
                severity=CheckSeverity.INFO,
                details={
                    "db_size_mb": round(db_size_mb, 2),
                    "page_count": page_count
                }
            )
        except Exception as e:
            return HealthCheckResult(
                name="database_connection",
                status=HealthStatus.CRITICAL,
                message=f"Database connection failed: {str(e)}",
                severity=CheckSeverity.CRITICAL
            )
    
    def _check_audit_log_status(self) -> HealthCheckResult:
        """Check audit log health."""
        try:
            cursor = self.conn.cursor()
            
            # Get total log entries
            cursor.execute("SELECT COUNT(*) FROM brain_audit_log")
            total_entries = cursor.fetchone()[0]
            
            # Get entries in last 24 hours
            cursor.execute("""
                SELECT COUNT(*) FROM brain_audit_log
                WHERE created_at >= datetime('now', '-1 day')
            """)
            recent_entries = cursor.fetchone()[0]
            
            # Get failed entries in last 24 hours
            cursor.execute("""
                SELECT COUNT(*) FROM brain_audit_log
                WHERE status = 'FAILED' AND created_at >= datetime('now', '-1 day')
            """)
            failed_entries = cursor.fetchone()[0]
            
            # Determine status
            if recent_entries == 0:
                status = HealthStatus.DEGRADED
                message = "No audit log entries in last 24 hours"
            elif failed_entries > recent_entries * 0.1:
                status = HealthStatus.DEGRADED
                message = f"High failure rate: {failed_entries}/{recent_entries} failed"
            else:
                status = HealthStatus.HEALTHY
                message = "Audit log is healthy"
            
            return HealthCheckResult(
                name="audit_log_status",
                status=status,
                message=message,
                severity=CheckSeverity.INFO if status == HealthStatus.HEALTHY else CheckSeverity.WARNING,
                details={
                    "total_entries": total_entries,
                    "recent_entries": recent_entries,
                    "failed_entries": failed_entries,
                    "failure_rate": round(failed_entries / recent_entries * 100, 2) if recent_entries > 0 else 0
                }
            )
        except sqlite3.OperationalError:
            return HealthCheckResult(
                name="audit_log_status",
                status=HealthStatus.UNHEALTHY,
                message="Audit log table not found",
                severity=CheckSeverity.ERROR
            )
    
    def _check_error_rate(self) -> HealthCheckResult:
        """Check system error rate."""
        try:
            cursor = self.conn.cursor()
            
            # Get error rate over different time periods
            timeframes = [
                ("1 hour", "-1 hour"),
                ("24 hours", "-1 day"),
                ("7 days", "-7 days")
            ]
            
            error_rates = {}
            for name, time_delta in timeframes:
                cursor.execute("""
                    SELECT 
                        COUNT(*) as total,
                        SUM(CASE WHEN status = 'FAILED' THEN 1 ELSE 0 END) as failed
                    FROM brain_audit_log
                    WHERE created_at >= datetime('now', ?)
                """, (time_delta,))
                
                row = cursor.fetchone()
                total = row[0] if row[0] else 0
                failed = row[1] if row[1] else 0
                rate = (failed / total * 100) if total > 0 else 0
                error_rates[name] = {
                    "total": total,
                    "failed": failed,
                    "rate": round(rate, 2)
                }
            
            # Determine status based on 24h error rate
            rate_24h = error_rates.get("24 hours", {}).get("rate", 0)
            
            if rate_24h > 10:
                status = HealthStatus.UNHEALTHY
                severity = CheckSeverity.ERROR
                message = f"High error rate: {rate_24h}% in last 24 hours"
            elif rate_24h > 5:
                status = HealthStatus.DEGRADED
                severity = CheckSeverity.WARNING
                message = f"Elevated error rate: {rate_24h}% in last 24 hours"
            else:
                status = HealthStatus.HEALTHY
                severity = CheckSeverity.INFO
                message = f"Normal error rate: {rate_24h}% in last 24 hours"
            
            return HealthCheckResult(
                name="error_rate",
                status=status,
                message=message,
                severity=severity,
                details={"error_rates": error_rates}
            )
        except sqlite3.OperationalError:
            return HealthCheckResult(
                name="error_rate",
                status=HealthStatus.DEGRADED,
                message="Cannot calculate error rate - audit log unavailable",
                severity=CheckSeverity.WARNING
            )
    
    def _check_command_performance(self) -> HealthCheckResult:
        """Check command execution performance."""
        try:
            cursor = self.conn.cursor()
            
            # Get average duration by command type in last 24 hours
            cursor.execute("""
                SELECT 
                    command_type,
                    COUNT(*) as count,
                    AVG(duration_ms) as avg_duration,
                    MAX(duration_ms) as max_duration
                FROM brain_audit_log
                WHERE created_at >= datetime('now', '-1 day')
                  AND duration_ms IS NOT NULL
                GROUP BY command_type
                ORDER BY avg_duration DESC
                LIMIT 10
            """)
            
            slow_commands = []
            for row in cursor.fetchall():
                if row[2] and row[2] > 1000:  # Slower than 1 second
                    slow_commands.append({
                        "command_type": row[0],
                        "count": row[1],
                        "avg_duration_ms": round(row[2], 2),
                        "max_duration_ms": row[3]
                    })
            
            if slow_commands:
                status = HealthStatus.DEGRADED
                message = f"{len(slow_commands)} command types averaging >1s"
            else:
                status = HealthStatus.HEALTHY
                message = "Command performance is good"
            
            return HealthCheckResult(
                name="command_performance",
                status=status,
                message=message,
                severity=CheckSeverity.WARNING if slow_commands else CheckSeverity.INFO,
                details={"slow_commands": slow_commands}
            )
        except sqlite3.OperationalError:
            return HealthCheckResult(
                name="command_performance",
                status=HealthStatus.DEGRADED,
                message="Cannot check performance - audit log unavailable",
                severity=CheckSeverity.WARNING
            )
    
    def _check_table_integrity(self) -> HealthCheckResult:
        """Check database table integrity."""
        try:
            cursor = self.conn.cursor()
            
            # Run PRAGMA integrity_check
            cursor.execute("PRAGMA integrity_check")
            result = cursor.fetchone()[0]
            
            if result == "ok":
                status = HealthStatus.HEALTHY
                message = "Database integrity check passed"
                severity = CheckSeverity.INFO
            else:
                status = HealthStatus.UNHEALTHY
                message = f"Database integrity issues: {result}"
                severity = CheckSeverity.ERROR
            
            # Get table info
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name NOT LIKE 'sqlite_%'
            """)
            tables = [row[0] for row in cursor.fetchall()]
            
            return HealthCheckResult(
                name="table_integrity",
                status=status,
                message=message,
                severity=severity,
                details={
                    "integrity_check": result,
                    "table_count": len(tables),
                    "tables": tables[:10]  # First 10 tables
                }
            )
        except Exception as e:
            return HealthCheckResult(
                name="table_integrity",
                status=HealthStatus.UNHEALTHY,
                message=f"Integrity check failed: {str(e)}",
                severity=CheckSeverity.ERROR
            )
    
    def get_health_summary(self) -> Dict:
        """Get a quick health summary."""
        health = self.run_all_checks()
        
        return {
            "status": health.status.value,
            "score": round(health.score * 100, 1),
            "healthy_count": len(health.healthy_checks),
            "unhealthy_count": len(health.unhealthy_checks),
            "checked_at": health.checked_at.isoformat()
        }
    
    def print_health_report(self):
        """Print a formatted health report."""
        health = self.run_all_checks()
        
        print("=" * 60)
        print("              SYSTEM HEALTH REPORT")
        print("=" * 60)
        print(f"Overall Status: {health.status.value}")
        print(f"Health Score: {health.score * 100:.1f}%")
        print(f"Checked At: {health.checked_at.isoformat()}")
        print()
        
        for check in health.checks:
            status_icon = {
                HealthStatus.HEALTHY: "✅",
                HealthStatus.DEGRADED: "⚠️",
                HealthStatus.UNHEALTHY: "❌",
                HealthStatus.CRITICAL: "🔴"
            }.get(check.status, "?")
            
            print(f"{status_icon} {check.name}")
            print(f"   {check.message}")
            if check.details:
                for key, value in check.details.items():
                    if isinstance(value, dict):
                        continue  # Skip nested dicts in summary
                    print(f"   - {key}: {value}")
            print()
        
        print("=" * 60)


__all__ = [
    "HealthStatus",
    "CheckSeverity",
    "HealthCheckResult",
    "SystemHealth",
    "HealthChecker",
]