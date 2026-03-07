"""
Performance Monitor - System-wide Performance Tracking

Provides comprehensive performance monitoring for the tracking system.
Tracks timing, memory usage, and identifies performance bottlenecks.

Usage:
    monitor = PerformanceMonitor()
    
    # Record an operation
    monitor.record_operation("get_habits", 150.5)
    
    # Get slow operations
    slow_ops = monitor.get_slow_operations(threshold_ms=100)
    
    # Generate performance report
    report = monitor.generate_report()
"""

import time
import psutil
import threading
from typing import Dict, List, Optional, Tuple, Any
from collections import defaultdict, deque
from dataclasses import dataclass
from datetime import datetime, timedelta
import json
import logging

logger = logging.getLogger(__name__)


@dataclass
class OperationMetric:
    """Represents a single operation metric."""
    name: str
    duration_ms: float
    timestamp: datetime
    memory_before_mb: float
    memory_after_mb: float
    cpu_percent: float
    thread_id: int


class PerformanceMonitor:
    """
    System-wide performance monitoring.
    
    Tracks operation timing, memory usage, and CPU utilization.
    Identifies performance bottlenecks and generates reports.
    """
    
    def __init__(self, max_history: int = 10000):
        """
        Initialize performance monitor.
        
        Args:
            max_history: Maximum number of operations to keep in history
        """
        self.max_history = max_history
        self.metrics: deque = deque(maxlen=max_history)
        self.operation_stats: Dict[str, List[float]] = defaultdict(list)
        self.slow_operations: List[OperationMetric] = []
        self.lock = threading.Lock()
        
        # Performance thresholds
        self.slow_threshold_ms = 100.0
        self.memory_threshold_mb = 50.0
        
        # System monitoring
        self.process = psutil.Process()
        self.monitoring = False
        self.monitor_thread = None
        
    def record_operation(self, operation_name: str, duration_ms: float) -> None:
        """
        Record an operation metric.
        
        Args:
            operation_name: Name of the operation
            duration_ms: Duration in milliseconds
        """
        try:
            # Get current system stats
            memory_info = self.process.memory_info()
            memory_mb = memory_info.rss / 1024 / 1024  # Convert to MB
            cpu_percent = self.process.cpu_percent()
            thread_id = threading.get_ident()
            
            metric = OperationMetric(
                name=operation_name,
                duration_ms=duration_ms,
                timestamp=datetime.now(),
                memory_before_mb=memory_mb,
                memory_after_mb=memory_mb,
                cpu_percent=cpu_percent,
                thread_id=thread_id
            )
            
            with self.lock:
                self.metrics.append(metric)
                self.operation_stats[operation_name].append(duration_ms)
                
                # Track slow operations
                if duration_ms > self.slow_threshold_ms:
                    self.slow_operations.append(metric)
                    if len(self.slow_operations) > 100:  # Keep only last 100 slow ops
                        self.slow_operations.pop(0)
                        
        except Exception as e:
            logger.warning(f"Failed to record performance metric: {e}")
    
    def get_operation_stats(self, operation_name: str) -> Dict[str, float]:
        """
        Get statistics for a specific operation.
        
        Args:
            operation_name: Name of the operation
            
        Returns:
            Dictionary with min, max, avg, and p95 timings
        """
        with self.lock:
            durations = self.operation_stats.get(operation_name, [])
            
        if not durations:
            return {
                'count': 0,
                'min': 0.0,
                'max': 0.0,
                'avg': 0.0,
                'p95': 0.0,
                'p99': 0.0
            }
        
        durations_sorted = sorted(durations)
        count = len(durations_sorted)
        
        return {
            'count': count,
            'min': durations_sorted[0],
            'max': durations_sorted[-1],
            'avg': sum(durations_sorted) / count,
            'p95': durations_sorted[int(0.95 * count)] if count > 0 else 0.0,
            'p99': durations_sorted[int(0.99 * count)] if count > 0 else 0.0
        }
    
    def get_slow_operations(self, threshold_ms: Optional[float] = None) -> List[Dict[str, Any]]:
        """
        Get slow operations.
        
        Args:
            threshold_ms: Optional threshold (uses default if not provided)
            
        Returns:
            List of slow operations sorted by duration
        """
        threshold = threshold_ms or self.slow_threshold_ms
        
        with self.lock:
            slow_ops = [
                {
                    'name': op.name,
                    'duration_ms': op.duration_ms,
                    'timestamp': op.timestamp.isoformat(),
                    'memory_mb': op.memory_after_mb,
                    'cpu_percent': op.cpu_percent
                }
                for op in self.slow_operations
                if op.duration_ms >= threshold
            ]
        
        return sorted(slow_ops, key=lambda x: x['duration_ms'], reverse=True)
    
    def get_top_operations(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get top operations by average duration.
        
        Args:
            limit: Number of operations to return
            
        Returns:
            List of operations sorted by average duration
        """
        with self.lock:
            operations = []
            for name, durations in self.operation_stats.items():
                if durations:
                    avg_duration = sum(durations) / len(durations)
                    operations.append({
                        'name': name,
                        'avg_duration': avg_duration,
                        'count': len(durations),
                        'total_duration': sum(durations)
                    })
        
        return sorted(operations, key=lambda x: x['avg_duration'], reverse=True)[:limit]
    
    def get_recent_operations(self, minutes: int = 30) -> List[Dict[str, Any]]:
        """
        Get operations from the last N minutes.
        
        Args:
            minutes: Number of minutes to look back
            
        Returns:
            List of recent operations
        """
        cutoff_time = datetime.now() - timedelta(minutes=minutes)
        
        with self.lock:
            recent_ops = [
                {
                    'name': op.name,
                    'duration_ms': op.duration_ms,
                    'timestamp': op.timestamp.isoformat(),
                    'memory_mb': op.memory_after_mb
                }
                for op in self.metrics
                if op.timestamp >= cutoff_time
            ]
        
        return sorted(recent_ops, key=lambda x: x['timestamp'], reverse=True)
    
    def get_memory_usage(self) -> Dict[str, float]:
        """
        Get current memory usage statistics.
        
        Returns:
            Dictionary with memory statistics
        """
        try:
            memory_info = self.process.memory_info()
            return {
                'rss_mb': memory_info.rss / 1024 / 1024,
                'vms_mb': memory_info.vms / 1024 / 1024,
                'percent': self.process.memory_percent(),
                'available_mb': psutil.virtual_memory().available / 1024 / 1024
            }
        except Exception as e:
            logger.warning(f"Failed to get memory usage: {e}")
            return {'rss_mb': 0, 'vms_mb': 0, 'percent': 0, 'available_mb': 0}
    
    def get_cpu_usage(self) -> Dict[str, float]:
        """
        Get current CPU usage statistics.
        
        Returns:
            Dictionary with CPU statistics
        """
        try:
            return {
                'process_percent': self.process.cpu_percent(),
                'system_percent': psutil.cpu_percent(),
                'num_threads': self.process.num_threads(),
                'num_ctx_switches': self.process.num_ctx_switches().total
            }
        except Exception as e:
            logger.warning(f"Failed to get CPU usage: {e}")
            return {'process_percent': 0, 'system_percent': 0, 'num_threads': 0, 'num_ctx_switches': 0}
    
    def generate_report(self) -> Dict[str, Any]:
        """
        Generate comprehensive performance report.
        
        Returns:
            Dictionary with performance metrics and recommendations
        """
        with self.lock:
            total_operations = len(self.metrics)
            
        # Get system stats
        memory_stats = self.get_memory_usage()
        cpu_stats = self.get_cpu_usage()
        
        # Get operation statistics
        top_operations = self.get_top_operations(10)
        slow_operations = self.get_slow_operations()
        recent_operations = self.get_recent_operations(60)
        
        # Calculate overall statistics
        all_durations = []
        for durations in self.operation_stats.values():
            all_durations.extend(durations)
        
        avg_duration = sum(all_durations) / len(all_durations) if all_durations else 0
        max_duration = max(all_durations) if all_durations else 0
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            top_operations, slow_operations, memory_stats, cpu_stats
        )
        
        return {
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'total_operations': total_operations,
                'avg_duration_ms': avg_duration,
                'max_duration_ms': max_duration,
                'slow_operations_count': len(slow_operations),
                'unique_operations': len(self.operation_stats)
            },
            'system_stats': {
                'memory': memory_stats,
                'cpu': cpu_stats
            },
            'operation_stats': {
                'top_operations': top_operations,
                'slow_operations': slow_operations,
                'recent_operations': recent_operations[:20]  # Last 20 operations
            },
            'recommendations': recommendations
        }
    
    def _generate_recommendations(
        self,
        top_operations: List[Dict[str, Any]],
        slow_operations: List[Dict[str, Any]],
        memory_stats: Dict[str, float],
        cpu_stats: Dict[str, float]
    ) -> List[Dict[str, str]]:
        """Generate performance recommendations."""
        recommendations = []
        
        # Memory recommendations
        if memory_stats['percent'] > 80:
            recommendations.append({
                'type': 'memory',
                'priority': 'high',
                'message': f"High memory usage detected ({memory_stats['percent']:.1f}%). Consider implementing caching or reducing data in memory."
            })
        
        # CPU recommendations
        if cpu_stats['process_percent'] > 50:
            recommendations.append({
                'type': 'cpu',
                'priority': 'high',
                'message': f"High CPU usage detected ({cpu_stats['process_percent']:.1f}%). Consider optimizing algorithms or adding caching."
            })
        
        # Operation-specific recommendations
        for op in top_operations[:3]:  # Top 3 slowest operations
            if op['avg_duration'] > 500:
                recommendations.append({
                    'type': 'operation',
                    'priority': 'medium',
                    'message': f"Operation '{op['name']}' is slow (avg: {op['avg_duration']:.1f}ms). Consider optimization or caching."
                })
        
        # Slow operation recommendations
        for op in slow_operations[:3]:  # Top 3 slowest instances
            if op['duration_ms'] > 1000:
                recommendations.append({
                    'type': 'operation',
                    'priority': 'high',
                    'message': f"Operation '{op['name']}' took {op['duration_ms']:.1f}ms. Immediate optimization needed."
                })
        
        # General recommendations
        if len(self.operation_stats) > 50:
            recommendations.append({
                'type': 'general',
                'priority': 'low',
                'message': "Consider consolidating similar operations to reduce overhead."
            })
        
        return recommendations
    
    def export_metrics(self, filepath: str) -> None:
        """
        Export metrics to JSON file.
        
        Args:
            filepath: Path to export file
        """
        with self.lock:
            metrics_data = [
                {
                    'name': op.name,
                    'duration_ms': op.duration_ms,
                    'timestamp': op.timestamp.isoformat(),
                    'memory_before_mb': op.memory_before_mb,
                    'memory_after_mb': op.memory_after_mb,
                    'cpu_percent': op.cpu_percent,
                    'thread_id': op.thread_id
                }
                for op in self.metrics
            ]
        
        export_data = {
            'export_timestamp': datetime.now().isoformat(),
            'metrics': metrics_data,
            'operation_stats': dict(self.operation_stats),
            'slow_operations': [
                {
                    'name': op.name,
                    'duration_ms': op.duration_ms,
                    'timestamp': op.timestamp.isoformat()
                }
                for op in self.slow_operations
            ]
        }
        
        try:
            with open(filepath, 'w') as f:
                json.dump(export_data, f, indent=2)
            logger.info(f"Performance metrics exported to {filepath}")
        except Exception as e:
            logger.error(f"Failed to export metrics: {e}")
    
    def clear_metrics(self) -> None:
        """Clear all recorded metrics."""
        with self.lock:
            self.metrics.clear()
            self.operation_stats.clear()
            self.slow_operations.clear()
        logger.info("Performance metrics cleared")


# Global performance monitor instance
_performance_monitor: Optional[PerformanceMonitor] = None


def get_performance_monitor() -> PerformanceMonitor:
    """Get the global performance monitor instance."""
    global _performance_monitor
    if _performance_monitor is None:
        _performance_monitor = PerformanceMonitor()
    return _performance_monitor


# Export
__all__ = [
    'PerformanceMonitor',
    'get_performance_monitor',
    'OperationMetric'
]