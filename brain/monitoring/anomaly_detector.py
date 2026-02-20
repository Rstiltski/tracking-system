"""
Anomaly Detector - Detects anomalies in system behavior

This module provides anomaly detection for:
- Error rate spikes
- Performance degradation
- Unusual command patterns
- Rule violations

📚 REQUIRED READING BEFORE MODIFICATION:
- brain/design/06_audit_schema.md
"""

import sqlite3
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional
from pathlib import Path


class AnomalyType(Enum):
    """Types of anomalies."""
    ERROR_SPIKE = "ERROR_SPIKE"
    PERFORMANCE_DEGRADATION = "PERFORMANCE_DEGRADATION"
    UNUSUAL_PATTERN = "UNUSUAL_PATTERN"
    RULE_VIOLATION = "RULE_VIOLATION"
    VOLUME_ANOMALY = "VOLUME_ANOMALY"
    STATE_ANOMALY = "STATE_ANOMALY"


class AnomalySeverity(Enum):
    """Severity levels for anomalies."""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


@dataclass
class Anomaly:
    """Detected anomaly."""
    anomaly_id: str
    anomaly_type: AnomalyType
    severity: AnomalySeverity
    detected_at: datetime
    description: str
    metric_name: str
    actual_value: Any
    expected_value: Any
    deviation: float
    related_commands: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        return {
            "anomaly_id": self.anomaly_id,
            "anomaly_type": self.anomaly_type.value,
            "severity": self.severity.value,
            "detected_at": self.detected_at.isoformat(),
            "description": self.description,
            "metric_name": self.metric_name,
            "actual_value": self.actual_value,
            "expected_value": self.expected_value,
            "deviation": self.deviation,
            "related_commands": self.related_commands,
            "recommendations": self.recommendations
        }


@dataclass
class AnomalyReport:
    """Report of all detected anomalies."""
    anomalies: List[Anomaly]
    scanned_at: datetime = field(default_factory=datetime.now)
    time_range_hours: int = 24
    
    def to_dict(self) -> Dict:
        return {
            "anomalies": [a.to_dict() for a in self.anomalies],
            "scanned_at": self.scanned_at.isoformat(),
            "time_range_hours": self.time_range_hours,
            "total_anomalies": len(self.anomalies),
            "by_severity": {
                s.value: len([a for a in self.anomalies if a.severity == s])
                for s in AnomalySeverity
            }
        }
    
    @property
    def critical_anomalies(self) -> List[Anomaly]:
        return [a for a in self.anomalies if a.severity == AnomalySeverity.CRITICAL]
    
    @property
    def high_anomalies(self) -> List[Anomaly]:
        return [a for a in self.anomalies if a.severity == AnomalySeverity.HIGH]


class AnomalyDetector:
    """
    Detects anomalies in system behavior.
    
    Uses statistical analysis to identify:
    - Error rate spikes (>2x baseline)
    - Performance degradation (>50% slower)
    - Unusual command patterns
    - Repeated failures
    """
    
    ERROR_RATE_THRESHOLD = 2.0
    PERFORMANCE_THRESHOLD = 1.5
    VOLUME_THRESHOLD = 3.0
    
    def __init__(self, db_path: Optional[str] = None):
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
    
    def detect_all(self, hours: int = 24) -> AnomalyReport:
        """Run all anomaly detection checks."""
        anomalies = []
        
        anomalies.extend(self._detect_error_spikes(hours))
        anomalies.extend(self._detect_performance_degradation(hours))
        anomalies.extend(self._detect_volume_anomalies(hours))
        anomalies.extend(self._detect_repeated_failures(hours))
        
        severity_order = {
            AnomalySeverity.CRITICAL: 0,
            AnomalySeverity.HIGH: 1,
            AnomalySeverity.MEDIUM: 2,
            AnomalySeverity.LOW: 3
        }
        anomalies.sort(key=lambda a: severity_order[a.severity])
        
        return AnomalyReport(anomalies=anomalies, time_range_hours=hours)
    
    def _detect_error_spikes(self, hours: int) -> List[Anomaly]:
        """Detect error rate spikes."""
        anomalies = []
        
        try:
            cursor = self.conn.cursor()
            
            # Get baseline error rate
            cursor.execute("""
                SELECT 
                    COUNT(*) as total,
                    SUM(CASE WHEN status = 'FAILED' THEN 1 ELSE 0 END) as failed
                FROM brain_audit_log
                WHERE created_at BETWEEN datetime('now', ?) AND datetime('now', ?)
            """, (f'-{hours * 2} hours', f'-{hours} hours'))
            
            baseline = cursor.fetchone()
            baseline_rate = baseline[1] / baseline[0] if baseline[0] > 0 else 0
            
            # Get current period
            cursor.execute("""
                SELECT 
                    COUNT(*) as total,
                    SUM(CASE WHEN status = 'FAILED' THEN 1 ELSE 0 END) as failed
                FROM brain_audit_log
                WHERE created_at >= datetime('now', ?)
            """, (f'-{hours} hours',))
            
            current = cursor.fetchone()
            current_rate = current[1] / current[0] if current[0] > 0 else 0
            
            if baseline_rate > 0 and current_rate > baseline_rate * self.ERROR_RATE_THRESHOLD:
                deviation = ((current_rate - baseline_rate) / baseline_rate) * 100
                
                cursor.execute("""
                    SELECT command_id FROM brain_audit_log
                    WHERE status = 'FAILED' AND created_at >= datetime('now', ?)
                    LIMIT 10
                """, (f'-{hours} hours',))
                
                failed_commands = [row[0] for row in cursor.fetchall()]
                
                anomalies.append(Anomaly(
                    anomaly_id=f"ANOM-{datetime.now().strftime('%Y%m%d%H%M%S')}-ERR",
                    anomaly_type=AnomalyType.ERROR_SPIKE,
                    severity=AnomalySeverity.HIGH if current_rate > 0.1 else AnomalySeverity.MEDIUM,
                    detected_at=datetime.now(),
                    description=f"Error rate spiked from {baseline_rate:.1%} to {current_rate:.1%}",
                    metric_name="error_rate",
                    actual_value=current_rate,
                    expected_value=baseline_rate,
                    deviation=deviation,
                    related_commands=failed_commands,
                    recommendations=["Investigate recent error codes", "Check for deployment changes"]
                ))
        
        except sqlite3.OperationalError:
            pass
        
        return anomalies
    
    def _detect_performance_degradation(self, hours: int) -> List[Anomaly]:
        """Detect performance degradation."""
        anomalies = []
        
        try:
            cursor = self.conn.cursor()
            
            # Get baseline performance
            cursor.execute("""
                SELECT command_type, AVG(duration_ms) as avg_duration
                FROM brain_audit_log
                WHERE created_at BETWEEN datetime('now', ?) AND datetime('now', ?)
                  AND duration_ms IS NOT NULL
                GROUP BY command_type
            """, (f'-{hours * 2} hours', f'-{hours} hours'))
            
            baseline = {row[0]: row[1] for row in cursor.fetchall()}
            
            # Get current performance
            cursor.execute("""
                SELECT command_type, AVG(duration_ms) as avg_duration
                FROM brain_audit_log
                WHERE created_at >= datetime('now', ?)
                  AND duration_ms IS NOT NULL
                GROUP BY command_type
            """, (f'-{hours} hours',))
            
            current = {row[0]: row[1] for row in cursor.fetchall()}
            
            for cmd_type, current_duration in current.items():
                if cmd_type in baseline:
                    baseline_duration = baseline[cmd_type]
                    
                    if current_duration > baseline_duration * self.PERFORMANCE_THRESHOLD:
                        deviation = ((current_duration - baseline_duration) / baseline_duration) * 100
                        
                        anomalies.append(Anomaly(
                            anomaly_id=f"ANOM-{datetime.now().strftime('%Y%m%d%H%M%S')}-PERF",
                            anomaly_type=AnomalyType.PERFORMANCE_DEGRADATION,
                            severity=AnomalySeverity.MEDIUM,
                            detected_at=datetime.now(),
                            description=f"{cmd_type} slowed from {baseline_duration:.0f}ms to {current_duration:.0f}ms",
                            metric_name="duration_ms",
                            actual_value=current_duration,
                            expected_value=baseline_duration,
                            deviation=deviation,
                            recommendations=["Check database indexes", "Review query performance"]
                        ))
        
        except sqlite3.OperationalError:
            pass
        
        return anomalies
    
    def _detect_volume_anomalies(self, hours: int) -> List[Anomaly]:
        """Detect unusual request volume."""
        anomalies = []
        
        try:
            cursor = self.conn.cursor()
            
            # Get average hourly volume for baseline
            cursor.execute("""
                SELECT COUNT(*) / ? as hourly_avg
                FROM brain_audit_log
                WHERE created_at BETWEEN datetime('now', ?) AND datetime('now', ?)
            """, (str(hours), f'-{hours * 2} hours', f'-{hours} hours'))
            
            baseline_hourly = cursor.fetchone()[0] or 0
            
            # Get current hourly volume
            cursor.execute("""
                SELECT COUNT(*) / ? as hourly_avg
                FROM brain_audit_log
                WHERE created_at >= datetime('now', ?)
            """, (str(hours), f'-{hours} hours',))
            
            current_hourly = cursor.fetchone()[0] or 0
            
            if baseline_hourly > 0 and current_hourly > baseline_hourly * self.VOLUME_THRESHOLD:
                deviation = ((current_hourly - baseline_hourly) / baseline_hourly) * 100
                
                anomalies.append(Anomaly(
                    anomaly_id=f"ANOM-{datetime.now().strftime('%Y%m%d%H%M%S')}-VOL",
                    anomaly_type=AnomalyType.VOLUME_ANOMALY,
                    severity=AnomalySeverity.LOW,
                    detected_at=datetime.now(),
                    description=f"Request volume increased from {baseline_hourly:.0f}/hr to {current_hourly:.0f}/hr",
                    metric_name="requests_per_hour",
                    actual_value=current_hourly,
                    expected_value=baseline_hourly,
                    deviation=deviation,
                    recommendations=["Monitor for continued increase", "Check for legitimate traffic spike"]
                ))
        
        except sqlite3.OperationalError:
            pass
        
        return anomalies
    
    def _detect_repeated_failures(self, hours: int) -> List[Anomaly]:
        """Detect repeated failures of same type."""
        anomalies = []
        
        try:
            cursor = self.conn.cursor()
            
            # Find error codes that appear more than 5 times
            cursor.execute("""
                SELECT error_code, COUNT(*) as count
                FROM brain_audit_log
                WHERE status = 'FAILED' 
                  AND created_at >= datetime('now', ?)
                  AND error_code IS NOT NULL
                GROUP BY error_code
                HAVING count > 5
                ORDER BY count DESC
            """, (f'-{hours} hours',))
            
            for row in cursor.fetchall():
                error_code = row[0]
                count = row[1]
                
                cursor.execute("""
                    SELECT command_id FROM brain_audit_log
                    WHERE error_code = ? AND created_at >= datetime('now', ?)
                    LIMIT 5
                """, (error_code, f'-{hours} hours',))
                
                related = [r[0] for r in cursor.fetchall()]
                
                anomalies.append(Anomaly(
                    anomaly_id=f"ANOM-{datetime.now().strftime('%Y%m%d%H%M%S')}-REPEAT",
                    anomaly_type=AnomalyType.RULE_VIOLATION,
                    severity=AnomalySeverity.HIGH if count > 10 else AnomalySeverity.MEDIUM,
                    detected_at=datetime.now(),
                    description=f"Error {error_code} occurred {count} times",
                    metric_name="error_count",
                    actual_value=count,
                    expected_value=1,
                    deviation=(count - 1) * 100,
                    related_commands=related,
                    recommendations=[f"Investigate error code {error_code}", "Check for systematic issue"]
                ))
        
        except sqlite3.OperationalError:
            pass
        
        return anomalies
    
    def print_report(self, report: AnomalyReport):
        """Print formatted anomaly report."""
        print("=" * 60)
        print("              ANOMALY DETECTION REPORT")
        print("=" * 60)
        print(f"Scanned At: {report.scanned_at.isoformat()}")
        print(f"Time Range: {report.time_range_hours} hours")
        print(f"Total Anomalies: {len(report.anomalies)}")
        print()
        
        if not report.anomalies:
            print("No anomalies detected. System is operating normally.")
            print("=" * 60)
            return
        
        severity_icons = {
            AnomalySeverity.CRITICAL: "🔴",
            AnomalySeverity.HIGH: "🟠",
            AnomalySeverity.MEDIUM: "🟡",
            AnomalySeverity.LOW: "🟢"
        }
        
        for anomaly in report.anomalies:
            icon = severity_icons.get(anomaly.severity, "⚪")
            print(f"{icon} [{anomaly.severity.value}] {anomaly.anomaly_type.value}")
            print(f"   {anomaly.description}")
            print(f"   Deviation: {anomaly.deviation:.1f}%")
            if anomaly.recommendations:
                print(f"   Recommendations: {', '.join(anomaly.recommendations[:2])}")
            print()
        
        print("=" * 60)


__all__ = [
    "AnomalyType",
    "AnomalySeverity",
    "Anomaly",
    "AnomalyReport",
    "AnomalyDetector",
]