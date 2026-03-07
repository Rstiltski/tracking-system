"""
Performance Baselines - Establish Performance Benchmarks

Provides functionality to establish performance baselines and measure
improvements throughout the optimization process.

Usage:
    from tracking_app.utils.performance_baselines import establish_baselines
    
    # Establish baselines
    baselines = establish_baselines()
    
    # Compare against baselines
    compare_against_baselines(current_metrics)
"""

import time
import json
import logging
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime, timedelta
from brain.utils.performance_monitor import get_performance_monitor
from tracking_app.utils.timing_decorators import timed_operation
from tracking_app.storage import get_storage
from tracking_app.database import get_db

logger = logging.getLogger(__name__)


class PerformanceBaseline:
    """Represents a performance baseline for a specific operation."""
    
    def __init__(
        self,
        operation_name: str,
        baseline_duration_ms: float,
        baseline_memory_mb: float,
        baseline_cpu_percent: float,
        timestamp: datetime,
        sample_size: int = 10
    ):
        self.operation_name = operation_name
        self.baseline_duration_ms = baseline_duration_ms
        self.baseline_memory_mb = baseline_memory_mb
        self.baseline_cpu_percent = baseline_cpu_percent
        self.timestamp = timestamp
        self.sample_size = sample_size
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'operation_name': self.operation_name,
            'baseline_duration_ms': self.baseline_duration_ms,
            'baseline_memory_mb': self.baseline_memory_mb,
            'baseline_cpu_percent': self.baseline_cpu_percent,
            'timestamp': self.timestamp.isoformat(),
            'sample_size': self.sample_size
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PerformanceBaseline":
        """Create from dictionary."""
        return cls(
            operation_name=data['operation_name'],
            baseline_duration_ms=data['baseline_duration_ms'],
            baseline_memory_mb=data['baseline_memory_mb'],
            baseline_cpu_percent=data['baseline_cpu_percent'],
            timestamp=datetime.fromisoformat(data['timestamp']),
            sample_size=data['sample_size']
        )


class BaselineManager:
    """Manages performance baselines."""
    
    def __init__(self, baseline_file: str = "performance_baselines.json"):
        self.baseline_file = baseline_file
        self.baselines: Dict[str, PerformanceBaseline] = {}
        self.load_baselines()
    
    def establish_baseline(
        self,
        operation_name: str,
        operation_func: Callable,
        sample_size: int = 10,
        warmup_runs: int = 3
    ) -> PerformanceBaseline:
        """
        Establish a performance baseline for an operation.
        
        Args:
            operation_name: Name of the operation
            operation_func: Function to measure
            sample_size: Number of samples to take
            warmup_runs: Number of warmup runs to discard
            
        Returns:
            PerformanceBaseline object
        """
        logger.info(f"Establishing baseline for {operation_name}")
        
        # Warmup runs
        for i in range(warmup_runs):
            try:
                operation_func()
            except Exception as e:
                logger.warning(f"Warmup run {i+1} failed: {e}")
        
        # Measure samples
        durations = []
        memory_values = []
        cpu_values = []
        
        monitor = get_performance_monitor()
        
        for i in range(sample_size):
            try:
                # Clear any existing metrics for this operation
                monitor.clear_metrics()
                
                # Measure memory before
                memory_before = self._get_memory_usage()
                
                # Execute operation with timing
                start_time = time.perf_counter()
                result = operation_func()
                end_time = time.perf_counter()
                
                # Measure memory after
                memory_after = self._get_memory_usage()
                
                # Calculate metrics
                duration_ms = (end_time - start_time) * 1000
                memory_delta = memory_after - memory_before
                cpu_usage = self._get_cpu_usage()
                
                durations.append(duration_ms)
                memory_values.append(memory_delta)
                cpu_values.append(cpu_usage)
                
                logger.debug(f"Sample {i+1}: {duration_ms:.2f}ms, {memory_delta:.2f}MB, {cpu_usage:.2f}%")
                
            except Exception as e:
                logger.error(f"Sample {i+1} failed: {e}")
                continue
        
        if not durations:
            raise ValueError(f"Failed to establish baseline for {operation_name}")
        
        # Calculate statistics
        avg_duration = sum(durations) / len(durations)
        avg_memory = sum(memory_values) / len(memory_values)
        avg_cpu = sum(cpu_values) / len(cpu_values)
        
        baseline = PerformanceBaseline(
            operation_name=operation_name,
            baseline_duration_ms=avg_duration,
            baseline_memory_mb=avg_memory,
            baseline_cpu_percent=avg_cpu,
            timestamp=datetime.now(),
            sample_size=len(durations)
        )
        
        self.baselines[operation_name] = baseline
        logger.info(f"Baseline established for {operation_name}: {avg_duration:.2f}ms, {avg_memory:.2f}MB, {avg_cpu:.2f}%")
        
        return baseline
    
    def compare_against_baseline(
        self,
        operation_name: str,
        current_duration_ms: float,
        current_memory_mb: float = 0.0,
        current_cpu_percent: float = 0.0
    ) -> Dict[str, Any]:
        """
        Compare current performance against baseline.
        
        Args:
            operation_name: Name of the operation
            current_duration_ms: Current duration in milliseconds
            current_memory_mb: Current memory usage in MB
            current_cpu_percent: Current CPU usage percentage
            
        Returns:
            Comparison results
        """
        baseline = self.baselines.get(operation_name)
        if not baseline:
            return {
                'operation_name': operation_name,
                'status': 'no_baseline',
                'message': f'No baseline found for {operation_name}'
            }
        
        # Calculate improvements/regressions
        duration_improvement = baseline.baseline_duration_ms - current_duration_ms
        duration_improvement_pct = (duration_improvement / baseline.baseline_duration_ms) * 100
        
        memory_improvement = baseline.baseline_memory_mb - current_memory_mb
        memory_improvement_pct = (memory_improvement / baseline.baseline_memory_mb) * 100 if baseline.baseline_memory_mb > 0 else 0
        
        cpu_improvement = baseline.baseline_cpu_percent - current_cpu_percent
        cpu_improvement_pct = (cpu_improvement / baseline.baseline_cpu_percent) * 100 if baseline.baseline_cpu_percent > 0 else 0
        
        # Determine status
        if duration_improvement_pct > 10:
            status = 'improved'
        elif duration_improvement_pct < -10:
            status = 'regressed'
        else:
            status = 'similar'
        
        return {
            'operation_name': operation_name,
            'status': status,
            'baseline': {
                'duration_ms': baseline.baseline_duration_ms,
                'memory_mb': baseline.baseline_memory_mb,
                'cpu_percent': baseline.baseline_cpu_percent,
                'timestamp': baseline.timestamp.isoformat(),
                'sample_size': baseline.sample_size
            },
            'current': {
                'duration_ms': current_duration_ms,
                'memory_mb': current_memory_mb,
                'cpu_percent': current_cpu_percent
            },
            'improvements': {
                'duration_ms': duration_improvement,
                'duration_pct': duration_improvement_pct,
                'memory_mb': memory_improvement,
                'memory_pct': memory_improvement_pct,
                'cpu_percent': cpu_improvement,
                'cpu_pct': cpu_improvement_pct
            }
        }
    
    def save_baselines(self) -> None:
        """Save baselines to file."""
        try:
            data = {
                'baselines': {name: baseline.to_dict() for name, baseline in self.baselines.items()},
                'saved_at': datetime.now().isoformat()
            }
            
            with open(self.baseline_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            logger.info(f"Baselines saved to {self.baseline_file}")
        except Exception as e:
            logger.error(f"Failed to save baselines: {e}")
    
    def load_baselines(self) -> None:
        """Load baselines from file."""
        try:
            with open(self.baseline_file, 'r') as f:
                data = json.load(f)
            
            self.baselines = {
                name: PerformanceBaseline.from_dict(baseline_data)
                for name, baseline_data in data.get('baselines', {}).items()
            }
            
            logger.info(f"Baselines loaded from {self.baseline_file}")
        except FileNotFoundError:
            logger.info("No existing baselines found")
        except Exception as e:
            logger.error(f"Failed to load baselines: {e}")
    
    def get_baseline(self, operation_name: str) -> Optional[PerformanceBaseline]:
        """Get baseline for an operation."""
        return self.baselines.get(operation_name)
    
    def list_baselines(self) -> List[str]:
        """List all established baselines."""
        return list(self.baselines.keys())
    
    def clear_baselines(self) -> None:
        """Clear all baselines."""
        self.baselines.clear()
        logger.info("All baselines cleared")
    
    def _get_memory_usage(self) -> float:
        """Get current memory usage in MB."""
        try:
            import psutil
            process = psutil.Process()
            memory_info = process.memory_info()
            return memory_info.rss / 1024 / 1024
        except ImportError:
            return 0.0
        except Exception:
            return 0.0
    
    def _get_cpu_usage(self) -> float:
        """Get current CPU usage percentage."""
        try:
            import psutil
            return psutil.Process().cpu_percent()
        except ImportError:
            return 0.0
        except Exception:
            return 0.0


def establish_common_baselines() -> Dict[str, PerformanceBaseline]:
    """
    Establish baselines for common operations.
    
    Returns:
        Dictionary of established baselines
    """
    manager = BaselineManager()
    
    # Get storage instance
    storage = get_storage()
    
    # Define operations to baseline
    operations = [
        ('get_habits', lambda: storage.get_habits()),
        ('get_tasks', lambda: storage.get_tasks()),
        ('get_goals', lambda: storage.get_goals()),
        ('get_health_entries', lambda: storage.get_health_entries()),
        ('get_transactions', lambda: storage.get_transactions()),
        ('get_habit_entries', lambda: storage.get_habit_entries('test_habit_id')),
        ('create_habit', lambda: storage.create_habit("Test Habit", "Test Description")),
        ('create_task', lambda: storage.create_task("Test Task", "Test Description")),
        ('create_transaction', lambda: storage.create_transaction("Test", 10.0, "income")),
        ('create_health_entry', lambda: storage.create_health_entry(date.today(), 70.0, 8.0, "good")),
    ]
    
    established_baselines = {}
    
    for operation_name, operation_func in operations:
        try:
            baseline = manager.establish_baseline(
                operation_name=operation_name,
                operation_func=operation_func,
                sample_size=5,  # Smaller sample for faster baseline establishment
                warmup_runs=2
            )
            established_baselines[operation_name] = baseline
        except Exception as e:
            logger.error(f"Failed to establish baseline for {operation_name}: {e}")
    
    # Save baselines
    manager.save_baselines()
    
    return established_baselines


def compare_performance_against_baselines() -> Dict[str, Any]:
    """
    Compare current performance against established baselines.
    
    Returns:
        Comparison results
    """
    manager = BaselineManager()
    
    # Get current performance metrics
    monitor = get_performance_monitor()
    report = monitor.generate_report()
    
    comparisons = {}
    
    for operation_name in manager.list_baselines():
        # Get current stats for this operation
        current_stats = monitor.get_operation_stats(operation_name)
        
        if current_stats['count'] > 0:
            current_duration = current_stats['avg']
            current_memory = 0.0  # Would need enhancement to track memory
            current_cpu = 0.0     # Would need enhancement to track CPU
            
            comparison = manager.compare_against_baseline(
                operation_name=operation_name,
                current_duration_ms=current_duration,
                current_memory_mb=current_memory,
                current_cpu_percent=current_cpu
            )
            
            comparisons[operation_name] = comparison
    
    return {
        'timestamp': datetime.now().isoformat(),
        'comparisons': comparisons,
        'summary': {
            'total_operations': len(comparisons),
            'improved': len([c for c in comparisons.values() if c.get('status') == 'improved']),
            'regressed': len([c for c in comparisons.values() if c.get('status') == 'regressed']),
            'similar': len([c for c in comparisons.values() if c.get('status') == 'similar'])
        }
    }


def generate_baseline_report() -> str:
    """
    Generate a comprehensive baseline report.
    
    Returns:
        Report as string
    """
    manager = BaselineManager()
    
    report_lines = [
        "# Performance Baseline Report",
        f"Generated: {datetime.now().isoformat()}",
        "",
        "## Established Baselines",
        ""
    ]
    
    if not manager.baselines:
        report_lines.append("No baselines established yet.")
    else:
        for operation_name, baseline in manager.baselines.items():
            report_lines.extend([
                f"### {operation_name}",
                f"- **Baseline Duration:** {baseline.baseline_duration_ms:.2f}ms",
                f"- **Baseline Memory:** {baseline.baseline_memory_mb:.2f}MB",
                f"- **Baseline CPU:** {baseline.baseline_cpu_percent:.2f}%",
                f"- **Sample Size:** {baseline.sample_size}",
                f"- **Established:** {baseline.timestamp.strftime('%Y-%m-%d %H:%M:%S')}",
                ""
            ])
    
    # Add comparison against current performance
    try:
        comparison = compare_performance_against_baselines()
        report_lines.extend([
            "## Current Performance vs Baselines",
            "",
            f"**Total Operations:** {comparison['summary']['total_operations']}",
            f"**Improved:** {comparison['summary']['improved']}",
            f"**Regressed:** {comparison['summary']['regressed']}",
            f"**Similar:** {comparison['summary']['similar']}",
            ""
        ])
        
        for operation_name, comp in comparison['comparisons'].items():
            status_emoji = {
                'improved': '🟢',
                'regressed': '🔴',
                'similar': '🟡'
            }.get(comp['status'], '⚪')
            
            report_lines.extend([
                f"### {status_emoji} {operation_name}",
                f"- **Status:** {comp['status']}",
                f"- **Duration Improvement:** {comp['improvements']['duration_pct']:.2f}%",
                f"- **Memory Improvement:** {comp['improvements']['memory_pct']:.2f}%",
                f"- **CPU Improvement:** {comp['improvements']['cpu_pct']:.2f}%",
                ""
            ])
    
    except Exception as e:
        report_lines.append(f"## Error generating comparison: {e}")
    
    return "\n".join(report_lines)


# Convenience functions
def establish_baselines() -> Dict[str, PerformanceBaseline]:
    """Establish baselines for common operations."""
    return establish_common_baselines()


def compare_baselines() -> Dict[str, Any]:
    """Compare current performance against baselines."""
    return compare_performance_against_baselines()


def save_baseline_report(filepath: str = "baseline_report.md") -> None:
    """Save baseline report to file."""
    report = generate_baseline_report()
    try:
        with open(filepath, 'w') as f:
            f.write(report)
        logger.info(f"Baseline report saved to {filepath}")
    except Exception as e:
        logger.error(f"Failed to save baseline report: {e}")


# Export
__all__ = [
    'PerformanceBaseline',
    'BaselineManager',
    'establish_baselines',
    'compare_baselines',
    'generate_baseline_report',
    'save_baseline_report'
]