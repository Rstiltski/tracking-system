"""
Predictive Loader - AI-Driven Preloading System

Provides intelligent predictive loading capabilities for the tracking system.
Uses machine learning to analyze user behavior patterns and preload likely-to-be-accessed content.

Features:
- User behavior analysis and pattern recognition
- ML-based prediction algorithms
- Background preloading with resource management
- Integration with existing caching and lazy loading systems

Usage:
    from brain.utils.predictive_loader import PredictiveLoader
    
    # Initialize predictive loader
    loader = PredictiveLoader()
    
    # Track user navigation
    loader.track_navigation("Dashboard", "Habits")
    
    # Get predicted next page
    predicted_page = loader.predict_next_page("Habits")
    
    # Preload predicted content
    loader.preload_page(predicted_page)
"""

import time
import logging
import threading
from typing import Dict, List, Optional, Tuple, Any, Callable
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import json
import pickle
from pathlib import Path

import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

logger = logging.getLogger(__name__)


@dataclass
class NavigationEvent:
    """Represents a user navigation event."""
    from_page: str
    to_page: str
    timestamp: float
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    context: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PredictionResult:
    """Result of a prediction operation."""
    predicted_page: str
    confidence: float
    alternatives: List[Tuple[str, float]]
    timestamp: float


class UserBehaviorAnalyzer:
    """
    Analyzes user behavior patterns for predictive loading.
    
    Features:
    - Navigation pattern analysis
    - Time-based behavior analysis
    - Session-based pattern recognition
    - Machine learning model training
    """
    
    def __init__(self, model_path: Optional[str] = None):
        """
        Initialize user behavior analyzer.
        
        Args:
            model_path: Optional path to save/load ML models
        """
        self.model_path = model_path
        self.navigation_history: List[NavigationEvent] = []
        self.page_transitions: Dict[str, Dict[str, int]] = defaultdict(lambda: defaultdict(int))
        self.time_patterns: Dict[str, List[int]] = defaultdict(list)
        self.session_patterns: Dict[str, List[str]] = {}
        
        # ML components
        self.model: Optional[RandomForestClassifier] = None
        self.label_encoder: Optional[LabelEncoder] = None
        self.page_encoder: Optional[LabelEncoder] = None
        
        # Training data
        self.features: List[List[float]] = []
        self.labels: List[str] = []
        
        # Configuration
        self.max_history_size = 10000
        self.min_training_samples = 100
        self.retrain_interval = 3600  # 1 hour
        self.last_training_time = 0
        
        logger.info("User behavior analyzer initialized")
    
    def track_navigation(self, from_page: str, to_page: str, user_id: Optional[str] = None, 
                        session_id: Optional[str] = None, context: Dict[str, Any] = None) -> None:
        """
        Track a navigation event.
        
        Args:
            from_page: Source page
            to_page: Target page
            user_id: User identifier
            session_id: Session identifier
            context: Additional context data
        """
        event = NavigationEvent(
            from_page=from_page,
            to_page=to_page,
            timestamp=time.time(),
            user_id=user_id,
            session_id=session_id,
            context=context or {}
        )
        
        # Add to history
        self.navigation_history.append(event)
        
        # Maintain history size
        if len(self.navigation_history) > self.max_history_size:
            self.navigation_history.pop(0)
        
        # Update transition patterns
        self.page_transitions[from_page][to_page] += 1
        
        # Update time patterns
        hour = datetime.fromtimestamp(event.timestamp).hour
        self.time_patterns[to_page].append(hour)
        
        # Update session patterns
        if session_id:
            if session_id not in self.session_patterns:
                self.session_patterns[session_id] = []
            self.session_patterns[session_id].append(to_page)
        
        # Add to training data
        self._add_training_sample(event)
        
        # Auto-train model if needed
        self._auto_train_model()
        
        logger.debug(f"Tracked navigation: {from_page} → {to_page}")
    
    def _add_training_sample(self, event: NavigationEvent) -> None:
        """
        Add a training sample to the dataset.
        
        Args:
            event: Navigation event to extract features from
        """
        # Extract features
        features = self._extract_features(event)
        self.features.append(features)
        self.labels.append(event.to_page)
    
    def _extract_features(self, event: NavigationEvent) -> List[float]:
        """
        Extract features from a navigation event for ML training.
        
        Args:
            event: Navigation event
            
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
            1 if dt.weekday() < 5 else 0,  # Weekday
        ])
        
        # Transition features
        transitions_from = sum(self.page_transitions[event.from_page].values())
        transitions_to = sum(1 for e in self.navigation_history if e.to_page == event.to_page)
        
        features.extend([
            transitions_from,  # How many times from this page
            transitions_to,  # How many times to this page
            len([e for e in self.navigation_history[-100:] if e.from_page == event.from_page]),  # Recent from
            len([e for e in self.navigation_history[-100:] if e.to_page == event.to_page]),  # Recent to
        ])
        
        # Context features
        context_features = [
            len(event.context.get('actions', [])),  # Number of actions
            event.context.get('time_spent', 0),  # Time spent on previous page
            1 if event.context.get('is_frequent_user', False) else 0,  # User type
        ]
        features.extend(context_features)
        
        return features
    
    def _auto_train_model(self) -> None:
        """Auto-train the ML model if conditions are met."""
        current_time = time.time()
        
        if (current_time - self.last_training_time > self.retrain_interval and
            len(self.features) >= self.min_training_samples):
            
            self.train_model()
            self.last_training_time = current_time
    
    def train_model(self) -> bool:
        """
        Train the machine learning model.
        
        Returns:
            True if training successful, False otherwise
        """
        if len(self.features) < self.min_training_samples:
            logger.warning(f"Insufficient training data: {len(self.features)} < {self.min_training_samples}")
            return False
        
        try:
            # Encode labels
            self.page_encoder = LabelEncoder()
            encoded_labels = self.page_encoder.fit_transform(self.labels)
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                self.features, encoded_labels, test_size=0.2, random_state=42
            )
            
            # Train model
            self.model = RandomForestClassifier(n_estimators=100, random_state=42)
            self.model.fit(X_train, y_train)
            
            # Evaluate model
            y_pred = self.model.predict(X_test)
            accuracy = accuracy_score(y_test, y_pred)
            
            logger.info(f"Model trained with accuracy: {accuracy:.3f}")
            
            # Save model if path provided
            if self.model_path:
                self.save_model()
            
            return True
            
        except Exception as e:
            logger.error(f"Model training failed: {e}")
            return False
    
    def save_model(self) -> None:
        """Save the trained model to disk."""
        if not self.model_path or not self.model:
            return
        
        try:
            model_data = {
                'model': self.model,
                'page_encoder': self.page_encoder,
                'features': self.features[-1000:],  # Keep recent features
                'labels': self.labels[-1000:],  # Keep recent labels
            }
            
            with open(self.model_path, 'wb') as f:
                pickle.dump(model_data, f)
            
            logger.info(f"Model saved to {self.model_path}")
            
        except Exception as e:
            logger.error(f"Failed to save model: {e}")
    
    def load_model(self) -> bool:
        """
        Load a trained model from disk.
        
        Returns:
            True if loading successful, False otherwise
        """
        if not self.model_path or not Path(self.model_path).exists():
            return False
        
        try:
            with open(self.model_path, 'rb') as f:
                model_data = pickle.load(f)
            
            self.model = model_data['model']
            self.page_encoder = model_data['page_encoder']
            self.features = model_data['features']
            self.labels = model_data['labels']
            
            logger.info(f"Model loaded from {self.model_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            return False
    
    def get_transition_probability(self, from_page: str, to_page: str) -> float:
        """
        Get the probability of transitioning from one page to another.
        
        Args:
            from_page: Source page
            to_page: Target page
            
        Returns:
            Probability (0.0 to 1.0)
        """
        total_transitions = sum(self.page_transitions[from_page].values())
        if total_transitions == 0:
            return 0.0
        
        return self.page_transitions[from_page][to_page] / total_transitions
    
    def get_most_likely_transitions(self, from_page: str, limit: int = 5) -> List[Tuple[str, float]]:
        """
        Get the most likely transitions from a page.
        
        Args:
            from_page: Source page
            limit: Maximum number of transitions to return
            
        Returns:
            List of (page, probability) tuples
        """
        transitions = self.page_transitions[from_page]
        if not transitions:
            return []
        
        total = sum(transitions.values())
        probabilities = [
            (page, count / total)
            for page, count in sorted(transitions.items(), key=lambda x: x[1], reverse=True)
        ]
        
        return probabilities[:limit]


class PredictiveLoader:
    """
    Main predictive loading system.
    
    Features:
    - ML-based page prediction
    - Background preloading with resource management
    - Integration with caching system
    - Performance monitoring and optimization
    """
    
    def __init__(self, cache_manager=None, model_path: Optional[str] = None):
        """
        Initialize predictive loader.
        
        Args:
            cache_manager: Cache manager instance for integration
            model_path: Path to ML model file
        """
        self.analyzer = UserBehaviorAnalyzer(model_path)
        self.cache_manager = cache_manager
        
        # Configuration
        self.prediction_threshold = 0.7  # Minimum confidence for preloading
        self.max_concurrent_preloads = 3
        self.preload_timeout = 30  # seconds
        self.preload_delay = 1.0  # seconds after navigation
        
        # State management
        self.active_preloads: Dict[str, threading.Thread] = {}
        self.preload_queue: deque = deque()
        self.preload_history: List[Dict[str, Any]] = []
        
        # Performance tracking
        self.preload_success_rate = 0.0
        self.preload_metrics = {
            'total_preloads': 0,
            'successful_preloads': 0,
            'failed_preloads': 0,
            'cache_hits': 0,
            'cache_misses': 0,
        }
        
        logger.info("Predictive loader initialized")
    
    def track_navigation(self, from_page: str, to_page: str, user_id: Optional[str] = None,
                        session_id: Optional[str] = None, context: Dict[str, Any] = None) -> None:
        """
        Track user navigation and trigger predictive loading.
        
        Args:
            from_page: Source page
            to_page: Target page
            user_id: User identifier
            session_id: Session identifier
            context: Additional context data
        """
        # Track in analyzer
        self.analyzer.track_navigation(from_page, to_page, user_id, session_id, context)
        
        # Trigger predictive loading after delay
        threading.Timer(
            self.preload_delay,
            self._schedule_predictive_preload,
            args=(to_page, user_id, session_id)
        ).start()
    
    def _schedule_predictive_preload(self, current_page: str, user_id: Optional[str], 
                                   session_id: Optional[str]) -> None:
        """
        Schedule predictive preloading based on current page.
        
        Args:
            current_page: Current page user is on
            user_id: User identifier
            session_id: Session identifier
        """
        # Get predictions
        predictions = self.predict_next_pages(current_page, limit=3)
        
        # Schedule preloading for high-confidence predictions
        for page, confidence in predictions:
            if confidence >= self.prediction_threshold:
                self.preload_page(page, user_id, session_id, confidence)
    
    def predict_next_pages(self, current_page: str, limit: int = 5) -> List[Tuple[str, float]]:
        """
        Predict the next likely pages the user will navigate to.
        
        Args:
            current_page: Current page
            limit: Maximum number of predictions to return
            
        Returns:
            List of (page, confidence) tuples
        """
        # Get ML-based predictions
        ml_predictions = self._get_ml_predictions(current_page, limit)
        
        # Get pattern-based predictions
        pattern_predictions = self.analyzer.get_most_likely_transitions(current_page, limit)
        
        # Combine predictions
        combined_predictions = self._combine_predictions(
            ml_predictions, pattern_predictions
        )
        
        # Sort by confidence
        combined_predictions.sort(key=lambda x: x[1], reverse=True)
        
        return combined_predictions[:limit]
    
    def _get_ml_predictions(self, current_page: str, limit: int) -> List[Tuple[str, float]]:
        """Get ML-based predictions."""
        if not self.analyzer.model or not self.analyzer.page_encoder:
            return []
        
        try:
            # Create features for current page
            current_time = time.time()
            event = NavigationEvent(
                from_page=current_page,
                to_page="",  # Not used for prediction
                timestamp=current_time
            )
            features = self.analyzer._extract_features(event)
            
            # Get prediction probabilities
            probabilities = self.analyzer.model.predict_proba([features])[0]
            classes = self.analyzer.model.classes_
            
            # Get top predictions
            predictions = []
            for class_idx, prob in enumerate(probabilities):
                page = self.analyzer.page_encoder.inverse_transform([classes[class_idx]])[0]
                predictions.append((page, prob))
            
            predictions.sort(key=lambda x: x[1], reverse=True)
            return predictions[:limit]
            
        except Exception as e:
            logger.error(f"ML prediction failed: {e}")
            return []
    
    def _combine_predictions(self, ml_predictions: List[Tuple[str, float]],
                           pattern_predictions: List[Tuple[str, float]]) -> List[Tuple[str, float]]:
        """Combine ML and pattern-based predictions."""
        # Weighted combination
        ml_weight = 0.7
        pattern_weight = 0.3
        
        all_pages = set()
        for page, _ in ml_predictions:
            all_pages.add(page)
        for page, _ in pattern_predictions:
            all_pages.add(page)
        
        combined = []
        for page in all_pages:
            ml_score = next((score for p, score in ml_predictions if p == page), 0.0)
            pattern_score = next((score for p, score in pattern_predictions if p == page), 0.0)
            
            combined_score = (ml_score * ml_weight) + (pattern_score * pattern_weight)
            combined.append((page, combined_score))
        
        return combined
    
    def preload_page(self, page_name: str, user_id: Optional[str] = None,
                     session_id: Optional[str] = None, confidence: float = 0.0) -> bool:
        """
        Preload a page in the background.
        
        Args:
            page_name: Name of page to preload
            user_id: User identifier
            session_id: Session identifier
            confidence: Prediction confidence
            
        Returns:
            True if preloading successful, False otherwise
        """
        # Check if already preloading
        if page_name in self.active_preloads:
            return True
        
        # Check concurrent preload limit
        if len(self.active_preloads) >= self.max_concurrent_preloads:
            self.preload_queue.append(page_name)
            return False
        
        # Start preloading in background
        thread = threading.Thread(
            target=self._preload_page_background,
            args=(page_name, user_id, session_id, confidence)
        )
        thread.daemon = True
        thread.start()
        
        self.active_preloads[page_name] = thread
        
        logger.info(f"Started preloading page: {page_name} (confidence: {confidence:.3f})")
        return True
    
    def _preload_page_background(self, page_name: str, user_id: Optional[str],
                               session_id: Optional[str], confidence: float) -> None:
        """
        Background thread for preloading a page.
        
        Args:
            page_name: Name of page to preload
            user_id: User identifier
            session_id: Session identifier
            confidence: Prediction confidence
        """
        start_time = time.time()
        
        try:
            # Simulate page loading (in real implementation, this would load actual page data)
            page_data = self._load_page_data(page_name, user_id)
            
            # Cache the preloaded data
            if self.cache_manager:
                cache_key = f"predicted_page_{page_name}_{user_id or 'anonymous'}"
                self.cache_manager.set(cache_key, page_data, ttl=600)  # 10 minutes
            
            # Record success
            self._record_preload_success(page_name, confidence, time.time() - start_time)
            
            logger.info(f"Successfully preloaded page: {page_name}")
            
        except Exception as e:
            # Record failure
            self._record_preload_failure(page_name, confidence, str(e))
            
            logger.error(f"Failed to preload page {page_name}: {e}")
        
        finally:
            # Clean up
            if page_name in self.active_preloads:
                del self.active_preloads[page_name]
            
            # Process queue
            self._process_preload_queue()
    
    def _load_page_data(self, page_name: str, user_id: Optional[str]) -> Dict[str, Any]:
        """
        Load page data for preloading.
        
        Args:
            page_name: Name of page to load
            user_id: User identifier
            
        Returns:
            Page data dictionary
        """
        # This would integrate with actual page loading logic
        # For now, simulate with mock data
        import random
        
        return {
            'page_name': page_name,
            'user_id': user_id,
            'timestamp': time.time(),
            'data_size': random.randint(1000, 5000),
            'load_time': random.uniform(0.1, 0.5)
        }
    
    def _record_preload_success(self, page_name: str, confidence: float, load_time: float) -> None:
        """Record successful preload."""
        self.preload_metrics['total_preloads'] += 1
        self.preload_metrics['successful_preloads'] += 1
        
        self.preload_history.append({
            'page': page_name,
            'confidence': confidence,
            'load_time': load_time,
            'success': True,
            'timestamp': time.time()
        })
        
        # Update success rate
        total = self.preload_metrics['total_preloads']
        successful = self.preload_metrics['successful_preloads']
        self.preload_success_rate = successful / total if total > 0 else 0.0
    
    def _record_preload_failure(self, page_name: str, confidence: float, error: str) -> None:
        """Record failed preload."""
        self.preload_metrics['total_preloads'] += 1
        self.preload_metrics['failed_preloads'] += 1
        
        self.preload_history.append({
            'page': page_name,
            'confidence': confidence,
            'error': error,
            'success': False,
            'timestamp': time.time()
        })
    
    def _process_preload_queue(self) -> None:
        """Process queued preloads."""
        while (self.preload_queue and 
               len(self.active_preloads) < self.max_concurrent_preloads):
            
            page_name = self.preload_queue.popleft()
            self.preload_page(page_name)
    
    def get_preload_metrics(self) -> Dict[str, Any]:
        """Get preload performance metrics."""
        return {
            'success_rate': self.preload_success_rate,
            'metrics': self.preload_metrics.copy(),
            'active_preloads': len(self.active_preloads),
            'queued_preloads': len(self.preload_queue),
            'total_predictions': len(self.analyzer.navigation_history)
        }
    
    def optimize_preload_settings(self) -> Dict[str, float]:
        """
        Optimize preload settings based on performance metrics.
        
        Returns:
            Optimized settings
        """
        metrics = self.get_preload_metrics()
        success_rate = metrics['success_rate']
        
        optimized_settings = {}
        
        # Adjust prediction threshold based on success rate
        if success_rate < 0.6:
            optimized_settings['prediction_threshold'] = min(0.9, self.prediction_threshold + 0.1)
        elif success_rate > 0.8:
            optimized_settings['prediction_threshold'] = max(0.5, self.prediction_threshold - 0.1)
        else:
            optimized_settings['prediction_threshold'] = self.prediction_threshold
        
        # Adjust concurrent preloads based on success rate
        if success_rate < 0.5:
            optimized_settings['max_concurrent_preloads'] = max(1, self.max_concurrent_preloads - 1)
        elif success_rate > 0.9:
            optimized_settings['max_concurrent_preloads'] = min(5, self.max_concurrent_preloads + 1)
        else:
            optimized_settings['max_concurrent_preloads'] = self.max_concurrent_preloads
        
        logger.info(f"Optimized settings: {optimized_settings}")
        return optimized_settings


# Global predictive loader instance
_predictive_loader: Optional[PredictiveLoader] = None


def get_predictive_loader() -> PredictiveLoader:
    """Get the global predictive loader instance."""
    global _predictive_loader
    if _predictive_loader is None:
        _predictive_loader = PredictiveLoader()
    return _predictive_loader


# Export
__all__ = [
    'PredictiveLoader',
    'UserBehaviorAnalyzer',
    'NavigationEvent',
    'PredictionResult',
    'get_predictive_loader'
]