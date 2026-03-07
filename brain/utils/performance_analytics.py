"""
Performance Analytics - Advanced Performance Monitoring System

Provides comprehensive performance analytics and insights for the tracking system.
Uses advanced analytics to deliver actionable performance recommendations and optimization insights.

Features:
- Real-time performance monitoring
- Advanced performance insights
- Optimization recommendation engine
- Comprehensive dashboards
- Performance trend analysis
- Bottleneck identification

Usage:
    from brain.utils.performance_analytics import PerformanceAnalytics
    
    # Initialize performance analytics
    analytics = PerformanceAnalytics()
    
    # Monitor performance
    analytics.record_performance_metric("page_load", "dashboard", 1.2)
    analytics.record_cache_hit("user_data", True)
    
    # Get insights
    insights = analytics.get_performance_insights()
    recommendations = analytics.get_optimization_recommendations()
    
    # Generate reports
    report = analytics.generate_performance_report()
"""

import time
import logging
import threading
from typing import Dict, List, Optional, Any, Tuple, Union
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import json
import pickle
from pathlib import Path
import statistics
from enum import Enum

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


class MetricType(Enum):
    """Types of performance metrics."""
    PAGE_LOAD = "page_load"
    API_RESPONSE = "api_response"
    CACHE_HIT = "cache_hit"
    DATABASE_QUERY = "database_query"
    MEMORY_USAGE = "memory_usage"
    CPU_USAGE = "cpu_usage"
    ERROR_RATE = "error_rate"
    USER_INTERACTION = "user_interaction"


class SeverityLevel(Enum):
    """Severity levels for performance issues."""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    BLOCKER = "blocker"


@dataclass
class PerformanceMetric:
    """Represents a performance metric."""
    metric_type: MetricType
    name: str
    value: float
    timestamp: float
    tags: Dict[str, str] = field(default_factory=dict)
    duration: Optional[float] = None
    success: Optional[bool] = None


@dataclass
class PerformanceInsight:
    """Represents a performance insight."""
    title: str
    description: str
    severity: SeverityLevel
    metric: str
    value: float
    threshold: float
    recommendation: str
    impact_score: float  # 0.0 to 1.0
    timestamp: float


@dataclass
class OptimizationRecommendation:
    """Represents an optimization recommendation."""
    title: str
    description: str
    category: str  # 'caching', 'database', 'frontend', 'backend'
    effort: str  # 'low', 'medium', 'high'
    impact: str  # 'low', 'medium', 'high'
    priority_score: float  # 0.0 to 1.0
    implementation_steps: List[str]
    expected_improvement: Dict[str, float]
    timestamp: float


class PerformanceAnalytics:
    """
    Main performance analytics system.
    
    Features:
    - Real-time performance monitoring
    - Advanced performance insights
    - Optimization recommendation engine
    - Comprehensive dashboards
    - Performance trend analysis
    - Bottleneck identification
    """
    
    def __init__(self, model_path: Optional[str] = None):
        """
        Initialize performance analytics.
        
        Args:
            model_path: Optional path to save/load ML models
        """
        self.model_path = model_path
        
        # Data storage
        self.metrics: List[PerformanceMetric] = []
        self.insights: List[PerformanceInsight] = []
        self.recommendations: List[OptimizationRecommendation] = []
        
        # Performance thresholds
        self.thresholds: Dict[str, Dict[str, float]] = {
            "page_load": {"warning": 2.0, "critical": 5.0, "blocker": 10.0},
            "api_response": {"warning": 1.0, "critical": 3.0, "blocker": 5.0},
            "cache_hit_rate": {"warning": 0.7, "critical": 0.5, "blocker": 0.3},
            "error_rate": {"warning": 0.05, "critical": 0.1, "blocker": 0.2},
            "memory_usage": {"warning": 0.8, "critical": 0.9, "blocker": 0.95},
            "cpu_usage": {"warning": 0.7, "critical": 0.85, "blocker": 0.95}
        }
        
        # Analytics configuration
        self.analysis_window = 3600  # 1 hour
        self.min_samples_for_analysis = 10
        self.trend_window = 86400  # 24 hours
        
        # Background analysis
        self.analysis_thread: Optional[threading.Thread] = None
        self.is_running = False
        self.analysis_interval = 300  # 5 minutes
        
        # Performance baselines
        self.baselines: Dict[str, Dict[str, float]] = {}
        
        # Anomaly detection
        self.anomaly_detector = AnomalyDetector()
        
        # Configuration
        self.max_metrics = 10000
        self.max_insights = 1000
        self.max_recommendations = 100
        
        logger.info("Performance analytics initialized")
    
    def record_metric(self, metric_type: Union[MetricType, str], name: str, 
                     value: float, tags: Dict[str, str] = None, 
                     duration: Optional[float] = None, 
                     success: Optional[bool] = None) -> None:
        """
        Record a performance metric.
        
        Args:
            metric_type: Type of metric
            name: Metric name
            value: Metric value
            tags: Additional tags
            duration: Optional duration
            success: Optional success status
        """
        if isinstance(metric_type, str):
            try:
                metric_type = MetricType(metric_type)
            except ValueError:
                logger.warning(f"Unknown metric type: {metric_type}")
                return
        
        metric = PerformanceMetric(
            metric_type=metric_type,
            name=name,
            value=value,
            timestamp=time.time(),
            tags=tags or {},
            duration=duration,
            success=success
        )
        
        self.metrics.append(metric)
        
        # Maintain metrics history size
        if len(self.metrics) > self.max_metrics:
            self.metrics.pop(0)
        
        # Trigger real-time analysis
        self._analyze_real_time_metric(metric)
        
        logger.debug(f"Recorded metric: {metric_type.value} - {name} = {value}")
    
    def _analyze_real_time_metric(self, metric: PerformanceMetric) -> None:
        """
        Analyze a metric in real-time for immediate insights.
        
        Args:
            metric: Performance metric to analyze
        """
        # Check against thresholds
        if metric.metric_type.value in self.thresholds:
            thresholds = self.thresholds[metric.metric_type.value]
            
            # Determine severity
            severity = None
            if metric.metric_type.value == "cache_hit_rate":
                # Inverted logic for cache hit rate
                if metric.value < thresholds["blocker"]:
                    severity = SeverityLevel.BLOCKER
                elif metric.value < thresholds["critical"]:
                    severity = SeverityLevel.CRITICAL
                elif metric.value < thresholds["warning"]:
                    severity = SeverityLevel.WARNING
            else:
                # Normal logic for other metrics
                if metric.value >= thresholds["blocker"]:
                    severity = SeverityLevel.BLOCKER
                elif metric.value >= thresholds["critical"]:
                    severity = SeverityLevel.CRITICAL
                elif metric.value >= thresholds["warning"]:
                    severity = SeverityLevel.WARNING
            
            # Create insight if threshold exceeded
            if severity:
                insight = PerformanceInsight(
                    title=f"Performance Issue: {metric.name}",
                    description=f"{metric.name} exceeded {severity.value} threshold",
                    severity=severity,
                    metric=metric.name,
                    value=metric.value,
                    threshold=thresholds.get(severity.value, 0),
                    recommendation=self._get_recommendation_for_metric(metric),
                    impact_score=self._calculate_impact_score(metric, severity),
                    timestamp=metric.timestamp
                )
                
                self.insights.append(insight)
                
                # Maintain insights history size
                if len(self.insights) > self.max_insights:
                    self.insights.pop(0)
    
    def _get_recommendation_for_metric(self, metric: PerformanceMetric) -> str:
        """
        Get recommendation for a specific metric.
        
        Args:
            metric: Performance metric
            
        Returns:
            Recommendation string
        """
        recommendations = {
            "page_load": "Consider implementing lazy loading, optimizing images, and using CDN",
            "api_response": "Review database queries, implement caching, and optimize endpoints",
            "cache_hit_rate": "Review cache strategy, increase cache size, or adjust TTL",
            "error_rate": "Investigate error sources and implement proper error handling",
            "memory_usage": "Review memory leaks, optimize data structures, and implement garbage collection",
            "cpu_usage": "Optimize algorithms, implement caching, and review computational complexity"
        }
        
        return recommendations.get(metric.name, "Review system configuration and optimization opportunities")
    
    def _calculate_impact_score(self, metric: PerformanceMetric, severity: SeverityLevel) -> float:
        """
        Calculate impact score for a performance issue.
        
        Args:
            metric: Performance metric
            severity: Severity level
            
        Returns:
            Impact score (0.0 to 1.0)
        """
        # Base scores by severity
        severity_scores = {
            SeverityLevel.INFO: 0.1,
            SeverityLevel.WARNING: 0.4,
            SeverityLevel.CRITICAL: 0.7,
            SeverityLevel.BLOCKER: 1.0
        }
        
        base_score = severity_scores.get(severity, 0.0)
        
        # Adjust based on frequency (recent metrics of same type)
        recent_metrics = [
            m for m in self.metrics[-100:] 
            if m.metric_type == metric.metric_type and m.name == metric.name
        ]
        
        frequency_bonus = min(len(recent_metrics) / 10.0, 0.3)
        
        return min(base_score + frequency_bonus, 1.0)
    
    def get_performance_insights(self, limit: int = 50) -> List[PerformanceInsight]:
        """
        Get performance insights.
        
        Args:
            limit: Maximum number of insights to return
            
        Returns:
            List of performance insights
        """
        # Sort by timestamp (newest first)
        sorted_insights = sorted(self.insights, key=lambda x: x.timestamp, reverse=True)
        return sorted_insights[:limit]
    
    def get_optimization_recommendations(self, limit: int = 20) -> List[OptimizationRecommendation]:
        """
        Get optimization recommendations.
        
        Args:
            limit: Maximum number of recommendations to return
            
        Returns:
            List of optimization recommendations
        """
        # Generate recommendations based on current state
        if not self.recommendations:
            self._generate_recommendations()
        
        # Sort by priority score (highest first)
        sorted_recommendations = sorted(
            self.recommendations, 
            key=lambda x: x.priority_score, 
            reverse=True
        )
        
        return sorted_recommendations[:limit]
    
    def _generate_recommendations(self) -> None:
        """Generate optimization recommendations based on current metrics."""
        # Analyze cache performance
        cache_metrics = [m for m in self.metrics if m.metric_type == MetricType.CACHE_HIT]
        if cache_metrics:
            avg_hit_rate = statistics.mean([m.value for m in cache_metrics])
            if avg_hit_rate < 0.8:
                recommendation = OptimizationRecommendation(
                    title="Improve Cache Hit Rate",
                    description="Cache hit rate is below optimal threshold",
                    category="caching",
                    effort="medium",
                    impact="high",
                    priority_score=0.8,
                    implementation_steps=[
                        "Review cache key strategy",
                        "Increase cache size if memory allows",
                        "Optimize cache TTL settings",
                        "Implement cache warming strategies"
                    ],
                    expected_improvement={"cache_hit_rate": 0.2, "response_time": 0.3},
                    timestamp=time.time()
                )
                self.recommendations.append(recommendation)
        
        # Analyze page load times
        page_load_metrics = [m for m in self.metrics if m.metric_type == MetricType.PAGE_LOAD]
        if page_load_metrics:
            avg_load_time = statistics.mean([m.value for m in page_load_metrics])
            if avg_load_time > 2.0:
                recommendation = OptimizationRecommendation(
                    title="Optimize Page Load Times",
                    description="Page load times exceed performance targets",
                    category="frontend",
                    effort="high",
                    impact="high",
                    priority_score=0.9,
                    implementation_steps=[
                        "Implement lazy loading for images and components",
                        "Optimize image sizes and formats",
                        "Enable compression and minification",
                        "Review JavaScript bundle size",
                        "Consider implementing CDN"
                    ],
                    expected_improvement={"page_load_time": 1.0, "user_experience": 0.4},
                    timestamp=time.time()
                )
                self.recommendations.append(recommendation)
        
        # Analyze API response times
        api_metrics = [m for m in self.metrics if m.metric_type == MetricType.API_RESPONSE]
        if api_metrics:
            avg_response_time = statistics.mean([m.value for m in api_metrics])
            if avg_response_time > 1.0:
                recommendation = OptimizationRecommendation(
                    title="Optimize API Response Times",
                    description="API response times are slower than expected",
                    category="backend",
                    effort="medium",
                    impact="medium",
                    priority_score=0.6,
                    implementation_steps=[
                        "Review database query performance",
                        "Implement query caching",
                        "Optimize serialization/deserialization",
                        "Consider implementing pagination",
                        "Review middleware performance"
                    ],
                    expected_improvement={"api_response_time": 0.5, "throughput": 0.2},
                    timestamp=time.time()
                )
                self.recommendations.append(recommendation)
        
        # Maintain recommendations history size
        if len(self.recommendations) > self.max_recommendations:
            self.recommendations = self.recommendations[-self.max_recommendations:]
    
    def generate_performance_report(self, time_range: str = "24h") -> Dict[str, Any]:
        """
        Generate a comprehensive performance report.
        
        Args:
            time_range: Time range for the report ("1h", "24h", "7d", "30d")
            
        Returns:
            Performance report dictionary
        """
        # Determine time range
        end_time = time.time()
        time_ranges = {
            "1h": 3600,
            "24h": 86400,
            "7d": 604800,
            "30d": 2592000
        }
        
        start_time = end_time - time_ranges.get(time_range, 86400)
        
        # Filter metrics by time range
        filtered_metrics = [
            m for m in self.metrics 
            if start_time <= m.timestamp <= end_time
        ]
        
        # Calculate statistics
        report = {
            "time_range": time_range,
            "start_time": start_time,
            "end_time": end_time,
            "total_metrics": len(filtered_metrics),
            "metrics_summary": self._calculate_metrics_summary(filtered_metrics),
            "performance_trends": self._calculate_trends(filtered_metrics),
            "bottlenecks": self._identify_bottlenecks(filtered_metrics),
            "recommendations": self.get_optimization_recommendations(10),
            "insights": self.get_performance_insights(20),
            "generated_at": time.time()
        }
        
        return report
    
    def _calculate_metrics_summary(self, metrics: List[PerformanceMetric]) -> Dict[str, Any]:
        """Calculate summary statistics for metrics."""
        if not metrics:
            return {}
        
        # Group metrics by type
        by_type = defaultdict(list)
        for metric in metrics:
            by_type[metric.metric_type.value].append(metric.value)
        
        summary = {}
        for metric_type, values in by_type.items():
            summary[metric_type] = {
                "count": len(values),
                "mean": statistics.mean(values),
                "median": statistics.median(values),
                "min": min(values),
                "max": max(values),
                "std_dev": statistics.stdev(values) if len(values) > 1 else 0.0
            }
        
        return summary
    
    def _calculate_trends(self, metrics: List[PerformanceMetric]) -> Dict[str, Any]:
        """Calculate performance trends."""
        if len(metrics) < 10:
            return {}
        
        # Group by hour for trend analysis
        hourly_data = defaultdict(list)
        for metric in metrics:
            hour = int(metric.timestamp // 3600) * 3600
            hourly_data[hour].append(metric.value)
        
        trends = {}
        for metric_type in set(m.metric_type.value for m in metrics):
            type_metrics = [m for m in metrics if m.metric_type.value == metric_type]
            if len(type_metrics) < 5:
                continue
            
            # Calculate trend using linear regression
            x = list(range(len(type_metrics)))
            y = [m.value for m in type_metrics]
            
            if len(x) > 1:
                correlation = np.corrcoef(x, y)[0, 1]
                trends[metric_type] = {
                    "trend_direction": "improving" if correlation < -0.1 else "degrading" if correlation > 0.1 else "stable",
                    "trend_strength": abs(correlation),
                    "current_value": y[-1] if y else 0,
                    "baseline_value": statistics.mean(y[:len(y)//2]) if len(y) > 1 else 0
                }
        
        return trends
    
    def _identify_bottlenecks(self, metrics: List[PerformanceMetric]) -> List[Dict[str, Any]]:
        """Identify performance bottlenecks."""
        bottlenecks = []
        
        # Analyze different metric types
        for metric_type in set(m.metric_type.value for m in metrics):
            type_metrics = [m for m in metrics if m.metric_type.value == metric_type]
            
            if len(type_metrics) < 5:
                continue
            
            values = [m.value for m in type_metrics]
            mean_val = statistics.mean(values)
            std_dev = statistics.stdev(values) if len(values) > 1 else 0
            
            # Identify outliers (potential bottlenecks)
            threshold = mean_val + (2 * std_dev)
            outliers = [m for m in type_metrics if m.value > threshold]
            
            if outliers:
                bottleneck = {
                    "metric_type": metric_type,
                    "description": f"High {metric_type} values detected",
                    "severity": "high" if len(outliers) > len(type_metrics) * 0.1 else "medium",
                    "count": len(outliers),
                    "avg_value": statistics.mean([m.value for m in outliers]),
                    "recommendation": self._get_recommendation_for_metric(outliers[0])
                }
                bottlenecks.append(bottleneck)
        
        return bottlenecks
    
    def start_background_analysis(self) -> None:
        """Start background performance analysis."""
        if self.is_running:
            return
        
        self.is_running = True
        self.analysis_thread = threading.Thread(
            target=self._analysis_loop,
            daemon=True
        )
        self.analysis_thread.start()
        
        logger.info("Background performance analysis started")
    
    def stop_background_analysis(self) -> None:
        """Stop background performance analysis."""
        self.is_running = False
        
        if self.analysis_thread:
            self.analysis_thread.join(timeout=5)
        
        logger.info("Background performance analysis stopped")
    
    def _analysis_loop(self) -> None:
        """Background analysis loop."""
        while self.is_running:
            try:
                # Run periodic analysis
                self._run_periodic_analysis()
                
                # Sleep until next analysis
                time.sleep(self.analysis_interval)
                
            except Exception as e:
                logger.error(f"Background analysis error: {e}")
                time.sleep(60)  # Wait 1 minute before retrying
    
    def _run_periodic_analysis(self) -> None:
        """Run periodic performance analysis."""
        # Update baselines
        self._update_baselines()
        
        # Generate new recommendations
        self._generate_recommendations()
        
        # Detect anomalies
        self._detect_anomalies()
        
        logger.debug("Periodic analysis completed")
    
    def _update_baselines(self) -> None:
        """Update performance baselines."""
        # Calculate baselines for different time periods
        recent_metrics = self.metrics[-1000:]  # Last 1000 metrics
        
        for metric_type in set(m.metric_type.value for m in recent_metrics):
            type_metrics = [m for m in recent_metrics if m.metric_type.value == metric_type]
            
            if len(type_metrics) >= self.min_samples_for_analysis:
                values = [m.value for m in type_metrics]
                
                self.baselines[metric_type] = {
                    "mean": statistics.mean(values),
                    "median": statistics.median(values),
                    "p95": np.percentile(values, 95),
                    "p99": np.percentile(values, 99),
                    "std_dev": statistics.stdev(values) if len(values) > 1 else 0
                }
    
    def _detect_anomalies(self) -> None:
        """Detect performance anomalies."""
        recent_metrics = self.metrics[-100:]  # Last 100 metrics
        
        for metric in recent_metrics:
            if metric.metric_type.value in self.baselines:
                baseline = self.baselines[metric.metric_type.value]
                
                # Use anomaly detector
                is_anomaly = self.anomaly_detector.is_anomaly(
                    metric.value, 
                    baseline["mean"], 
                    baseline["std_dev"]
                )
                
                if is_anomaly:
                    insight = PerformanceInsight(
                        title=f"Performance Anomaly: {metric.name}",
                        description=f"Detected anomaly in {metric.name} performance",
                        severity=SeverityLevel.WARNING,
                        metric=metric.name,
                        value=metric.value,
                        threshold=baseline["mean"] + (3 * baseline["std_dev"]),
                        recommendation="Investigate recent changes that may have affected performance",
                        impact_score=0.5,
                        timestamp=metric.timestamp
                    )
                    
                    self.insights.append(insight)
    
    def get_dashboard_data(self) -> Dict[str, Any]:
        """Get data for performance dashboard."""
        return {
            "current_metrics": self._get_current_metrics(),
            "recent_insights": self.get_performance_insights(10),
            "top_recommendations": self.get_optimization_recommendations(5),
            "performance_summary": self._get_performance_summary(),
            "system_health": self._calculate_system_health()
        }
    
    def _get_current_metrics(self) -> Dict[str, float]:
        """Get current performance metrics."""
        recent_metrics = self.metrics[-50:]  # Last 50 metrics
        
        current = {}
        for metric_type in set(m.metric_type.value for m in recent_metrics):
            type_metrics = [m for m in recent_metrics if m.metric_type.value == metric_type]
            if type_metrics:
                current[metric_type] = type_metrics[-1].value
        
        return current
    
    def _get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary."""
        if not self.metrics:
            return {}
        
        # Calculate overall performance score
        total_metrics = len(self.metrics)
        
        # Count metrics by severity
        critical_count = len([i for i in self.insights if i.severity == SeverityLevel.CRITICAL])
        warning_count = len([i for i in self.insights if i.severity == SeverityLevel.WARNING])
        
        # Calculate performance score (0-100)
        score = 100 - (critical_count * 10) - (warning_count * 2)
        score = max(0, min(100, score))
        
        return {
            "total_metrics": total_metrics,
            "critical_issues": critical_count,
            "warning_issues": warning_count,
            "performance_score": score,
            "recommendations_count": len(self.recommendations)
        }
    
    def _calculate_system_health(self) -> Dict[str, Any]:
        """Calculate overall system health."""
        if not self.metrics:
            return {"status": "unknown", "score": 0}
        
        # Calculate health score based on various factors
        health_factors = []
        
        # Cache health
        cache_metrics = [m for m in self.metrics if m.metric_type == MetricType.CACHE_HIT]
        if cache_metrics:
            avg_cache_hit = statistics.mean([m.value for m in cache_metrics])
            cache_health = min(avg_cache_hit * 100, 100)
            health_factors.append(cache_health)
        
        # Response time health
        response_metrics = [m for m in self.metrics if m.metric_type in [MetricType.PAGE_LOAD, MetricType.API_RESPONSE]]
        if response_metrics:
            avg_response = statistics.mean([m.value for m in response_metrics])
            response_health = max(0, 100 - (avg_response * 10))
            health_factors.append(response_health)
        
        # Error rate health
        error_metrics = [m for m in self.metrics if m.metric_type == MetricType.ERROR_RATE]
        if error_metrics:
            avg_error_rate = statistics.mean([m.value for m in error_metrics])
            error_health = max(0, 100 - (avg_error_rate * 500))
            health_factors.append(error_health)
        
        # Calculate overall health
        if health_factors:
            overall_health = statistics.mean(health_factors)
            status = "excellent" if overall_health >= 90 else "good" if overall_health >= 75 else "fair" if overall_health >= 50 else "poor"
        else:
            overall_health = 0
            status = "unknown"
        
        return {
            "status": status,
            "score": overall_health,
            "factors": health_factors
        }
    
    def save_state(self, filepath: Optional[str] = None) -> None:
        """Save analytics state to file."""
        if not filepath and self.model_path:
            filepath = self.model_path
        
        if not filepath:
            return
        
        try:
            state = {
                "metrics": self.metrics,
                "insights": self.insights,
                "recommendations": self.recommendations,
                "baselines": self.baselines,
                "thresholds": self.thresholds
            }
            
            with open(filepath, 'wb') as f:
                pickle.dump(state, f)
            
            logger.info(f"Analytics state saved to {filepath}")
            
        except Exception as e:
            logger.error(f"Failed to save analytics state: {e}")
    
    def load_state(self, filepath: Optional[str] = None) -> bool:
        """Load analytics state from file."""
        if not filepath and self.model_path:
            filepath = self.model_path
        
        if not filepath or not Path(filepath).exists():
            return False
        
        try:
            with open(filepath, 'rb') as f:
                state = pickle.load(f)
            
            self.metrics = state.get("metrics", [])
            self.insights = state.get("insights", [])
            self.recommendations = state.get("recommendations", [])
            self.baselines = state.get("baselines", {})
            self.thresholds = state.get("thresholds", self.thresholds)
            
            logger.info(f"Analytics state loaded from {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load analytics state: {e}")
            return False


class AnomalyDetector:
    """Simple anomaly detector for performance metrics."""
    
    def __init__(self, threshold_multiplier: float = 3.0):
        """
        Initialize anomaly detector.
        
        Args:
            threshold_multiplier: Multiplier for standard deviation threshold
        """
        self.threshold_multiplier = threshold_multiplier
    
    def is_anomaly(self, value: float, mean: float, std_dev: float) -> bool:
        """
        Check if a value is an anomaly.
        
        Args:
            value: Value to check
            mean: Mean of the distribution
            std_dev: Standard deviation of the distribution
            
        Returns:
            True if anomaly, False otherwise
        """
        if std_dev == 0:
            return False
        
        z_score = abs((value - mean) / std_dev)
        return z_score > self.threshold_multiplier


# Global performance analytics instance
_performance_analytics: Optional[PerformanceAnalytics] = None


def get_performance_analytics() -> Optional[PerformanceAnalytics]:
    """Get the global performance analytics instance."""
    return _performance_analytics


def initialize_performance_analytics(model_path: Optional[str] = None) -> PerformanceAnalytics:
    """Initialize and return a performance analytics instance."""
    global _performance_analytics
    _performance_analytics = PerformanceAnalytics(model_path)
    return _performance_analytics


# Export
__all__ = [
    'PerformanceAnalytics',
    'PerformanceMetric',
    'PerformanceInsight',
    'OptimizationRecommendation',
    'MetricType',
    'SeverityLevel',
    'get_performance_analytics',
    'initialize_performance_analytics'
]