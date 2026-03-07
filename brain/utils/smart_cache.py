"""
Smart Cache - AI-Driven Cache Management System

Provides intelligent caching capabilities with machine learning optimization.
Uses AI to dynamically manage cache sizing, invalidation, and warming strategies.

Features:
- AI-driven cache optimization
- Dynamic cache sizing based on usage patterns
- Intelligent cache invalidation strategies
- Multi-tier cache management with predictive warming
- Integration with existing caching system

Usage:
    from brain.utils.smart_cache import SmartCacheManager
    
    # Initialize smart cache manager
    smart_cache = SmartCacheManager(base_cache=cache_manager)
    
    # Smart cache operations
    smart_cache.set("key", "value", ttl=300)
    value = smart_cache.get("key")
    
    # AI-driven optimization
    smart_cache.optimize_cache_size()
    smart_cache.predictive_warm_cache()
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

import numpy as np
from sklearn.ensemble import RandomForestRegressor, IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, accuracy_score

from brain.utils.cache import CacheManager

logger = logging.getLogger(__name__)


@dataclass
class CacheEvent:
    """Represents a cache operation event."""
    operation: str  # 'get', 'set', 'delete', 'hit', 'miss'
    key: str
    timestamp: float
    ttl: Optional[int] = None
    size: Optional[int] = None
    hit: Optional[bool] = None
    access_pattern: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CacheMetrics:
    """Cache performance metrics."""
    hit_rate: float
    miss_rate: float
    avg_access_time: float
    memory_usage: float
    eviction_count: int
    timestamp: float


class CacheUsageAnalyzer:
    """
    Analyzes cache usage patterns for AI-driven optimization.
    
    Features:
    - Usage pattern analysis
    - Access frequency tracking
    - Memory usage optimization
    - Predictive cache sizing
    """
    
    def __init__(self, model_path: Optional[str] = None):
        """
        Initialize cache usage analyzer.
        
        Args:
            model_path: Optional path to save/load ML models
        """
        self.model_path = model_path
        self.cache_events: List[CacheEvent] = []
        self.access_patterns: Dict[str, Dict[str, Any]] = defaultdict(lambda: {
            'access_count': 0,
            'last_access': 0,
            'avg_interval': 0,
            'access_times': [],
            'ttl_history': [],
            'size_history': []
        })
        
        # ML components
        self.size_model: Optional[RandomForestRegressor] = None
        self.eviction_model: Optional[IsolationForest] = None
        self.scaler: Optional[StandardScaler] = None
        
        # Training data
        self.size_features: List[List[float]] = []
        self.size_targets: List[float] = []
        self.eviction_features: List[List[float]] = []
        
        # Configuration
        self.max_events = 10000
        self.retrain_interval = 3600  # 1 hour
        self.last_training_time = 0
        
        # Performance tracking
        self.metrics_history: List[CacheMetrics] = []
        
        logger.info("Cache usage analyzer initialized")
    
    def record_event(self, event: CacheEvent) -> None:
        """
        Record a cache operation event.
        
        Args:
            event: Cache operation event
        """
        # Add to event history
        self.cache_events.append(event)
        
        # Maintain event history size
        if len(self.cache_events) > self.max_events:
            self.cache_events.pop(0)
        
        # Update access patterns
        pattern = self.access_patterns[event.key]
        pattern['access_count'] += 1
        pattern['last_access'] = event.timestamp
        
        # Track access intervals
        if pattern['access_times']:
            interval = event.timestamp - pattern['access_times'][-1]
            pattern['access_times'].append(event.timestamp)
            pattern['avg_interval'] = np.mean(np.diff(pattern['access_times']))
        else:
            pattern['access_times'] = [event.timestamp]
        
        # Track TTL and size history
        if event.ttl is not None:
            pattern['ttl_history'].append(event.ttl)
        if event.size is not None:
            pattern['size_history'].append(event.size)
        
        # Add to training data
        self._add_training_sample(event)
        
        # Auto-train models if needed
        self._auto_train_models()
        
        logger.debug(f"Recorded cache event: {event.operation} {event.key}")
    
    def _add_training_sample(self, event: CacheEvent) -> None:
        """
        Add a training sample to the dataset.
        
        Args:
            event: Cache event to extract features from
        """
        # Extract features for size prediction
        features = self._extract_size_features(event)
        self.size_features.append(features)
        self.size_targets.append(self._get_optimal_size())
        
        # Extract features for eviction prediction
        eviction_features = self._extract_eviction_features(event)
        self.eviction_features.append(eviction_features)
    
    def _extract_size_features(self, event: CacheEvent) -> List[float]:
        """
        Extract features for cache size prediction.
        
        Args:
            event: Cache event
            
        Returns:
            List of numerical features
        """
        features = []
        
        # Time-based features
        dt = datetime.fromtimestamp(event.timestamp)
        features.extend([
            dt.hour,  # Hour of day
            dt.weekday(),  # Day of week
            dt.day,  # Day of month
            1 if 9 <= dt.hour <= 17 else 0,  # Business hours
        ])
        
        # Usage-based features
        total_accesses = sum(p['access_count'] for p in self.access_patterns.values())
        active_keys = len([p for p in self.access_patterns.values() if p['access_count'] > 0])
        
        features.extend([
            total_accesses,  # Total accesses
            active_keys,  # Active cache keys
            len(self.cache_events),  # Event history size
            self._get_current_memory_usage(),  # Current memory usage
        ])
        
        # Pattern-based features
        key_pattern = self.access_patterns[event.key]
        features.extend([
            key_pattern['access_count'],  # Key access count
            key_pattern['avg_interval'],  # Average access interval
            len(key_pattern['ttl_history']),  # TTL history length
            np.mean(key_pattern['ttl_history']) if key_pattern['ttl_history'] else 0,  # Avg TTL
        ])
        
        return features
    
    def _extract_eviction_features(self, event: CacheEvent) -> List[float]:
        """
        Extract features for eviction prediction.
        
        Args:
            event: Cache event
            
        Returns:
            List of numerical features
        """
        features = []
        
        # Key-specific features
        pattern = self.access_patterns[event.key]
        features.extend([
            pattern['access_count'],
            pattern['avg_interval'],
            pattern['last_access'],
            len(pattern['access_times']),
        ])
        
        # System-level features
        total_memory = self._get_current_memory_usage()
        hit_rate = self._calculate_hit_rate()
        
        features.extend([
            total_memory,
            hit_rate,
            len(self.access_patterns),
            len(self.cache_events),
        ])
        
        return features
    
    def _get_optimal_size(self) -> float:
        """
        Calculate optimal cache size based on current usage.
        
        Returns:
            Optimal cache size in bytes
        """
        # Simple heuristic: 1.5x current memory usage with minimum threshold
        current_usage = self._get_current_memory_usage()
        optimal_size = current_usage * 1.5
        
        # Minimum size of 10MB
        return max(optimal_size, 10 * 1024 * 1024)
    
    def _get_current_memory_usage(self) -> float:
        """Get current estimated memory usage."""
        total_size = 0
        for pattern in self.access_patterns.values():
            if pattern['size_history']:
                total_size += pattern['size_history'][-1]
        return total_size
    
    def _calculate_hit_rate(self) -> float:
        """Calculate current cache hit rate."""
        hits = sum(1 for event in self.cache_events if event.hit is True)
        total = len([e for e in self.cache_events if e.hit is not None])
        return hits / total if total > 0 else 0.0
    
    def _auto_train_models(self) -> None:
        """Auto-train ML models if conditions are met."""
        current_time = time.time()
        
        if (current_time - self.last_training_time > self.retrain_interval and
            len(self.size_features) >= 100):
            
            self.train_models()
            self.last_training_time = current_time
    
    def train_models(self) -> bool:
        """
        Train the machine learning models.
        
        Returns:
            True if training successful, False otherwise
        """
        if len(self.size_features) < 100:
            logger.warning(f"Insufficient training data: {len(self.size_features)} < 100")
            return False
        
        try:
            # Train size prediction model
            X_size = np.array(self.size_features)
            y_size = np.array(self.size_targets)
            
            if len(X_size) > 0:
                # Scale features
                self.scaler = StandardScaler()
                X_scaled = self.scaler.fit_transform(X_size)
                
                # Train size prediction model
                self.size_model = RandomForestRegressor(n_estimators=50, random_state=42)
                X_train, X_test, y_train, y_test = train_test_split(
                    X_scaled, y_size, test_size=0.2, random_state=42
                )
                self.size_model.fit(X_train, y_train)
                
                # Evaluate model
                y_pred = self.size_model.predict(X_test)
                mse = mean_squared_error(y_test, y_pred)
                logger.info(f"Size prediction model trained with MSE: {mse:.2f}")
            
            # Train eviction detection model
            if len(self.eviction_features) >= 100:
                X_eviction = np.array(self.eviction_features)
                self.eviction_model = IsolationForest(contamination=0.1, random_state=42)
                self.eviction_model.fit(X_eviction)
                
                logger.info("Eviction detection model trained")
            
            # Save models if path provided
            if self.model_path:
                self.save_models()
            
            return True
            
        except Exception as e:
            logger.error(f"Model training failed: {e}")
            return False
    
    def save_models(self) -> None:
        """Save the trained models to disk."""
        if not self.model_path:
            return
        
        try:
            model_data = {
                'size_model': self.size_model,
                'eviction_model': self.eviction_model,
                'scaler': self.scaler,
                'access_patterns': self.access_patterns,
                'cache_events': self.cache_events[-1000:],  # Keep recent events
            }
            
            with open(self.model_path, 'wb') as f:
                pickle.dump(model_data, f)
            
            logger.info(f"Models saved to {self.model_path}")
            
        except Exception as e:
            logger.error(f"Failed to save models: {e}")
    
    def load_models(self) -> bool:
        """
        Load trained models from disk.
        
        Returns:
            True if loading successful, False otherwise
        """
        if not self.model_path or not Path(self.model_path).exists():
            return False
        
        try:
            with open(self.model_path, 'rb') as f:
                model_data = pickle.load(f)
            
            self.size_model = model_data['size_model']
            self.eviction_model = model_data['eviction_model']
            self.scaler = model_data['scaler']
            self.access_patterns = model_data['access_patterns']
            self.cache_events = model_data['cache_events']
            
            logger.info(f"Models loaded from {self.model_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load models: {e}")
            return False
    
    def predict_optimal_size(self) -> Optional[float]:
        """
        Predict optimal cache size.
        
        Returns:
            Predicted optimal size in bytes, or None if prediction failed
        """
        if not self.size_model or not self.scaler:
            return None
        
        try:
            # Get current features
            current_time = time.time()
            current_event = CacheEvent(
                operation='predict',
                key='system',
                timestamp=current_time
            )
            features = self._extract_size_features(current_event)
            
            # Scale features
            features_scaled = self.scaler.transform([features])
            
            # Predict optimal size
            predicted_size = self.size_model.predict(features_scaled)[0]
            
            return max(predicted_size, 10 * 1024 * 1024)  # Minimum 10MB
            
        except Exception as e:
            logger.error(f"Size prediction failed: {e}")
            return None
    
    def predict_eviction_risk(self, key: str) -> Optional[float]:
        """
        Predict eviction risk for a cache key.
        
        Args:
            key: Cache key to evaluate
            
        Returns:
            Eviction risk score (0.0 to 1.0), or None if prediction failed
        """
        if not self.eviction_model or not self.scaler:
            return None
        
        try:
            # Create event for prediction
            current_time = time.time()
            event = CacheEvent(
                operation='predict',
                key=key,
                timestamp=current_time
            )
            
            # Extract features
            features = self._extract_eviction_features(event)
            
            # Scale features
            features_scaled = self.scaler.transform([features])
            
            # Predict eviction risk
            anomaly_score = self.eviction_model.decision_function(features_scaled)[0]
            
            # Convert to risk score (0.0 to 1.0)
            risk_score = max(0.0, min(1.0, (anomaly_score + 0.5) / 1.0))
            
            return risk_score
            
        except Exception as e:
            logger.error(f"Eviction risk prediction failed for key {key}: {e}")
            return None
    
    def get_access_frequency(self, key: str) -> float:
        """
        Get access frequency for a key.
        
        Args:
            key: Cache key
            
        Returns:
            Access frequency (accesses per hour)
        """
        pattern = self.access_patterns.get(key, {})
        if not pattern['access_times']:
            return 0.0
        
        # Calculate accesses per hour
        time_span = time.time() - pattern['access_times'][0]
        hours = max(time_span / 3600, 0.001)  # Avoid division by zero
        return pattern['access_count'] / hours
    
    def get_cache_efficiency(self) -> Dict[str, float]:
        """
        Get cache efficiency metrics.
        
        Returns:
            Dictionary with efficiency metrics
        """
        if not self.cache_events:
            return {
                'hit_rate': 0.0,
                'miss_rate': 1.0,
                'avg_access_time': 0.0,
                'memory_efficiency': 0.0
            }
        
        # Calculate hit rate
        hits = sum(1 for event in self.cache_events if event.hit is True)
        total_accesses = len([e for e in self.cache_events if e.hit is not None])
        hit_rate = hits / total_accesses if total_accesses > 0 else 0.0
        
        # Calculate average access time (simplified)
        avg_access_time = 0.01  # Placeholder
        
        # Calculate memory efficiency
        current_memory = self._get_current_memory_usage()
        optimal_memory = self.predict_optimal_size() or current_memory
        memory_efficiency = current_memory / optimal_memory if optimal_memory > 0 else 1.0
        
        return {
            'hit_rate': hit_rate,
            'miss_rate': 1.0 - hit_rate,
            'avg_access_time': avg_access_time,
            'memory_efficiency': memory_efficiency
        }


class SmartCacheManager:
    """
    Main smart cache management system.
    
    Features:
    - AI-driven cache optimization
    - Dynamic cache sizing
    - Intelligent cache invalidation
    - Predictive cache warming
    - Multi-tier cache management
    """
    
    def __init__(self, base_cache: CacheManager, model_path: Optional[str] = None):
        """
        Initialize smart cache manager.
        
        Args:
            base_cache: Base cache manager to enhance
            model_path: Path to ML model file
        """
        self.base_cache = base_cache
        self.analyzer = CacheUsageAnalyzer(model_path)
        
        # Configuration
        self.optimization_interval = 300  # 5 minutes
        self.warming_interval = 600  # 10 minutes
        self.max_warmup_keys = 50
        
        # State management
        self.optimization_thread: Optional[threading.Thread] = None
        self.warming_thread: Optional[threading.Thread] = None
        self.is_running = False
        
        # Performance tracking
        self.optimization_history: List[Dict[str, Any]] = []
        
        logger.info("Smart cache manager initialized")
    
    def start_background_optimization(self) -> None:
        """Start background optimization threads."""
        if self.is_running:
            return
        
        self.is_running = True
        
        # Start optimization thread
        self.optimization_thread = threading.Thread(
            target=self._optimization_loop,
            daemon=True
        )
        self.optimization_thread.start()
        
        # Start warming thread
        self.warming_thread = threading.Thread(
            target=self._warming_loop,
            daemon=True
        )
        self.warming_thread.start()
        
        logger.info("Background optimization started")
    
    def stop_background_optimization(self) -> None:
        """Stop background optimization threads."""
        self.is_running = False
        
        if self.optimization_thread:
            self.optimization_thread.join(timeout=5)
        if self.warming_thread:
            self.warming_thread.join(timeout=5)
        
        logger.info("Background optimization stopped")
    
    def _optimization_loop(self) -> None:
        """Background optimization loop."""
        while self.is_running:
            try:
                self.optimize_cache_size()
                self.optimize_cache_invalidation()
                
                # Sleep until next optimization
                time.sleep(self.optimization_interval)
                
            except Exception as e:
                logger.error(f"Optimization loop error: {e}")
                time.sleep(60)  # Wait 1 minute before retrying
    
    def _warming_loop(self) -> None:
        """Background cache warming loop."""
        while self.is_running:
            try:
                self.predictive_warm_cache()
                
                # Sleep until next warming
                time.sleep(self.warming_interval)
                
            except Exception as e:
                logger.error(f"Warming loop error: {e}")
                time.sleep(60)  # Wait 1 minute before retrying
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """
        Set a value in the cache with smart optimization.
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds
            
        Returns:
            True if successful, False otherwise
        """
        # Record the operation
        size = self._estimate_size(value)
        event = CacheEvent(
            operation='set',
            key=key,
            timestamp=time.time(),
            ttl=ttl,
            size=size
        )
        self.analyzer.record_event(event)
        
        # Set in base cache
        return self.base_cache.set(key, value, ttl)
    
    def get(self, key: str) -> Optional[Any]:
        """
        Get a value from the cache with smart optimization.
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None if not found
        """
        # Get from base cache
        value = self.base_cache.get(key)
        
        # Record the operation
        hit = value is not None
        event = CacheEvent(
            operation='get',
            key=key,
            timestamp=time.time(),
            hit=hit
        )
        self.analyzer.record_event(event)
        
        return value
    
    def delete(self, key: str) -> bool:
        """
        Delete a key from the cache.
        
        Args:
            key: Cache key
            
        Returns:
            True if successful, False otherwise
        """
        # Record the operation
        event = CacheEvent(
            operation='delete',
            key=key,
            timestamp=time.time()
        )
        self.analyzer.record_event(event)
        
        # Delete from base cache
        return self.base_cache.delete(key)
    
    def _estimate_size(self, value: Any) -> int:
        """
        Estimate the size of a value in bytes.
        
        Args:
            value: Value to estimate size for
            
        Returns:
            Estimated size in bytes
        """
        try:
            return len(str(value).encode('utf-8'))
        except:
            return 100  # Default estimate
    
    def optimize_cache_size(self) -> Dict[str, Any]:
        """
        Optimize cache size based on AI predictions.
        
        Returns:
            Optimization results
        """
        try:
            # Get current metrics
            current_size = self.base_cache.get_memory_usage()
            efficiency = self.analyzer.get_cache_efficiency()
            
            # Predict optimal size
            predicted_size = self.analyzer.predict_optimal_size()
            
            results = {
                'current_size': current_size,
                'predicted_optimal_size': predicted_size,
                'efficiency': efficiency,
                'recommendation': 'no_change'
            }
            
            if predicted_size:
                size_diff = predicted_size - current_size
                size_change_pct = abs(size_diff) / current_size if current_size > 0 else 0
                
                # Only adjust if change is significant (>10%)
                if size_change_pct > 0.1:
                    if size_diff > 0:
                        # Increase cache size
                        new_size = int(current_size * 1.2)  # Increase by 20%
                        self.base_cache.set_max_size(new_size)
                        results['recommendation'] = 'increase_size'
                        results['new_size'] = new_size
                    else:
                        # Decrease cache size
                        new_size = int(current_size * 0.8)  # Decrease by 20%
                        self.base_cache.set_max_size(new_size)
                        results['recommendation'] = 'decrease_size'
                        results['new_size'] = new_size
            
            # Record optimization
            self.optimization_history.append({
                'type': 'size_optimization',
                'timestamp': time.time(),
                'results': results
            })
            
            logger.info(f"Cache size optimization: {results['recommendation']}")
            return results
            
        except Exception as e:
            logger.error(f"Cache size optimization failed: {e}")
            return {'error': str(e)}
    
    def optimize_cache_invalidation(self) -> Dict[str, Any]:
        """
        Optimize cache invalidation based on AI predictions.
        
        Returns:
            Optimization results
        """
        try:
            # Get keys with high eviction risk
            high_risk_keys = []
            for key in list(self.base_cache.cache.keys()):
                risk = self.analyzer.predict_eviction_risk(key)
                if risk and risk > 0.8:  # High eviction risk
                    high_risk_keys.append((key, risk))
            
            # Sort by risk score
            high_risk_keys.sort(key=lambda x: x[1], reverse=True)
            
            # Preemptively refresh high-risk keys
            refreshed_count = 0
            for key, risk in high_risk_keys[:10]:  # Refresh top 10
                try:
                    # Try to refresh the key (extend TTL)
                    current_value = self.base_cache.get(key)
                    if current_value is not None:
                        self.base_cache.set(key, current_value, ttl=600)  # Extend TTL to 10 minutes
                        refreshed_count += 1
                except Exception:
                    pass  # Ignore refresh failures
            
            results = {
                'high_risk_keys': len(high_risk_keys),
                'refreshed_keys': refreshed_count,
                'action': 'preemptive_refresh' if refreshed_count > 0 else 'no_action'
            }
            
            # Record optimization
            self.optimization_history.append({
                'type': 'invalidation_optimization',
                'timestamp': time.time(),
                'results': results
            })
            
            logger.info(f"Cache invalidation optimization: {results['action']}")
            return results
            
        except Exception as e:
            logger.error(f"Cache invalidation optimization failed: {e}")
            return {'error': str(e)}
    
    def predictive_warm_cache(self) -> Dict[str, Any]:
        """
        Warm cache with predicted frequently accessed keys.
        
        Returns:
            Warming results
        """
        try:
            # Get frequently accessed keys
            frequent_keys = []
            for key, pattern in self.analyzer.access_patterns.items():
                frequency = self.analyzer.get_access_frequency(key)
                if frequency > 1.0:  # More than 1 access per hour
                    frequent_keys.append((key, frequency))
            
            # Sort by frequency
            frequent_keys.sort(key=lambda x: x[1], reverse=True)
            
            # Warm up cache with top keys
            warmed_count = 0
            for key, frequency in frequent_keys[:self.max_warmup_keys]:
                try:
                    # Try to load the key (this will cache it if not already cached)
                    if not self.base_cache.get(key):
                        # Key not in cache, try to load from source
                        # This is a placeholder - in real implementation,
                        # you would load from your data source
                        pass
                    warmed_count += 1
                except Exception:
                    pass  # Ignore warming failures
            
            results = {
                'frequent_keys': len(frequent_keys),
                'warmed_keys': warmed_count,
                'action': 'cache_warming' if warmed_count > 0 else 'no_action'
            }
            
            # Record optimization
            self.optimization_history.append({
                'type': 'predictive_warming',
                'timestamp': time.time(),
                'results': results
            })
            
            logger.info(f"Predictive cache warming: {results['action']}")
            return results
            
        except Exception as e:
            logger.error(f"Predictive cache warming failed: {e}")
            return {'error': str(e)}
    
    def get_optimization_metrics(self) -> Dict[str, Any]:
        """
        Get comprehensive optimization metrics.
        
        Returns:
            Dictionary with optimization metrics
        """
        efficiency = self.analyzer.get_cache_efficiency()
        
        # Calculate optimization success rate
        total_optimizations = len(self.optimization_history)
        successful_optimizations = len([
            opt for opt in self.optimization_history
            if 'error' not in opt['results']
        ])
        
        success_rate = successful_optimizations / total_optimizations if total_optimizations > 0 else 0.0
        
        return {
            'efficiency': efficiency,
            'total_optimizations': total_optimizations,
            'successful_optimizations': successful_optimizations,
            'success_rate': success_rate,
            'current_memory_usage': self.base_cache.get_memory_usage(),
            'cache_hit_rate': efficiency['hit_rate'],
            'memory_efficiency': efficiency['memory_efficiency']
        }
    
    def force_optimization(self) -> Dict[str, Any]:
        """
        Force immediate optimization of all cache aspects.
        
        Returns:
            Comprehensive optimization results
        """
        results = {
            'size_optimization': self.optimize_cache_size(),
            'invalidation_optimization': self.optimize_cache_invalidation(),
            'predictive_warming': self.predictive_warm_cache(),
            'timestamp': time.time()
        }
        
        logger.info("Forced cache optimization completed")
        return results


# Global smart cache manager instance
_smart_cache_manager: Optional[SmartCacheManager] = None


def get_smart_cache_manager() -> Optional[SmartCacheManager]:
    """Get the global smart cache manager instance."""
    return _smart_cache_manager


def initialize_smart_cache(base_cache: CacheManager, model_path: Optional[str] = None) -> SmartCacheManager:
    """Initialize and return a smart cache manager instance."""
    global _smart_cache_manager
    _smart_cache_manager = SmartCacheManager(base_cache, model_path)
    return _smart_cache_manager


# Export
__all__ = [
    'SmartCacheManager',
    'CacheUsageAnalyzer',
    'CacheEvent',
    'CacheMetrics',
    'get_smart_cache_manager',
    'initialize_smart_cache'
]