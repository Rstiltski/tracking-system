"""
Burnout Prediction Module

Predicts and helps prevent user burnout by monitoring behavioral indicators
and providing timely interventions.

Based on research in behavioral science and habit formation.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
import math


@dataclass
class BurnoutIndicators:
    """
    Indicators used for burnout prediction.
    
    These metrics are monitored to detect early warning signs of burnout
    before the user abandons their habits.
    """
    completion_rate_trend: float = 0.0  # -1 to 1 (declining to improving)
    sleep_deviation: float = 0.0  # Hours below/above baseline
    stress_level: int = 5  # 1-10 scale
    days_since_checkin: int = 0  # Days without app interaction
    streak_breaks: int = 0  # Number of recent streak breaks
    mood_trend: float = 0.0  # -1 to 1 (declining to improving)
    task_overload: float = 0.0  # Tasks due / capacity ratio
    habit_load: int = 0  # Number of active habits
    missed_days: int = 0  # Consecutive missed days
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'completion_rate_trend': self.completion_rate_trend,
            'sleep_deviation': self.sleep_deviation,
            'stress_level': self.stress_level,
            'days_since_checkin': self.days_since_checkin,
            'streak_breaks': self.streak_breaks,
            'mood_trend': self.mood_trend,
            'task_overload': self.task_overload,
            'habit_load': self.habit_load,
            'missed_days': self.missed_days
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BurnoutIndicators':
        """Create from dictionary."""
        return cls(
            completion_rate_trend=data.get('completion_rate_trend', 0.0),
            sleep_deviation=data.get('sleep_deviation', 0.0),
            stress_level=data.get('stress_level', 5),
            days_since_checkin=data.get('days_since_checkin', 0),
            streak_breaks=data.get('streak_breaks', 0),
            mood_trend=data.get('mood_trend', 0.0),
            task_overload=data.get('task_overload', 0.0),
            habit_load=data.get('habit_load', 0),
            missed_days=data.get('missed_days', 0)
        )


@dataclass
class BurnoutRisk:
    """
    Burnout risk assessment result.
    
    Provides a comprehensive view of burnout risk with actionable
    interventions to help the user recover.
    """
    risk_score: float  # 0-100%
    risk_level: str  # 'low', 'moderate', 'high', 'critical'
    contributing_factors: Dict[str, float]  # Factor -> normalized impact
    interventions: List[str]  # Recommended actions
    recovery_mode_recommended: bool  # Whether to suggest recovery mode
    monitoring_frequency: str  # How often to reassess
    calculated_at: datetime = field(default_factory=datetime.now)
    
    @property
    def risk_emoji(self) -> str:
        """Get emoji for risk level."""
        emojis = {
            'low': '🟢',
            'moderate': '🟡',
            'high': '🟠',
            'critical': '🔴'
        }
        return emojis.get(self.risk_level, '⚪')
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'risk_score': self.risk_score,
            'risk_level': self.risk_level,
            'risk_emoji': self.risk_emoji,
            'contributing_factors': self.contributing_factors,
            'interventions': self.interventions,
            'recovery_mode_recommended': self.recovery_mode_recommended,
            'monitoring_frequency': self.monitoring_frequency,
            'calculated_at': self.calculated_at.isoformat()
        }


class BurnoutPredictor:
    """
    Predict and prevent user burnout.
    
    Monitors behavioral indicators and calculates burnout risk,
    providing timely interventions to help users maintain their habits.
    
    Example:
        predictor = BurnoutPredictor()
        
        # Assess burnout risk
        indicators = BurnoutIndicators(
            completion_rate_trend=-0.3,
            sleep_deviation=-1.5,
            stress_level=7,
            days_since_checkin=2
        )
        
        risk = predictor.assess_risk(indicators)
        print(f"Risk: {risk.risk_level} ({risk.risk_score}%)")
        for intervention in risk.interventions:
            print(f"  - {intervention}")
    """
    
    # Weights for each indicator in burnout calculation
    INDICATOR_WEIGHTS = {
        'completion_rate_trend': 0.25,
        'sleep_deviation': 0.20,
        'stress_level': 0.15,
        'days_since_checkin': 0.15,
        'streak_breaks': 0.10,
        'mood_trend': 0.10,
        'task_overload': 0.05
    }
    
    # Thresholds for risk levels
    RISK_THRESHOLDS = {
        'critical': 75,
        'high': 50,
        'moderate': 25,
        'low': 0
    }
    
    def __init__(self, custom_weights: Optional[Dict[str, float]] = None):
        """
        Initialize burnout predictor.
        
        Args:
            custom_weights: Optional custom weights for indicators
        """
        self.weights = custom_weights or self.INDICATOR_WEIGHTS.copy()
    
    def assess_risk(self, indicators: BurnoutIndicators) -> BurnoutRisk:
        """
        Calculate burnout risk score from indicators.
        
        Args:
            indicators: Current burnout indicators
            
        Returns:
            BurnoutRisk with score, level, and interventions
        """
        # Calculate normalized factor scores
        factors = self._calculate_factors(indicators)
        
        # Calculate weighted risk score
        risk_score = sum(
            factors[factor] * weight 
            for factor, weight in self.weights.items()
            if factor in factors
        ) * 100
        
        # Clamp to valid range
        risk_score = max(0, min(100, risk_score))
        
        # Determine risk level
        risk_level = self._determine_risk_level(risk_score)
        
        # Generate interventions
        interventions = self._generate_interventions(factors, risk_level, indicators)
        
        # Determine if recovery mode is needed
        recovery_mode = risk_score >= 50
        
        # Determine monitoring frequency
        monitoring = self._determine_monitoring_frequency(risk_level)
        
        return BurnoutRisk(
            risk_score=round(risk_score, 1),
            risk_level=risk_level,
            contributing_factors=factors,
            interventions=interventions,
            recovery_mode_recommended=recovery_mode,
            monitoring_frequency=monitoring
        )
    
    def _calculate_factors(self, indicators: BurnoutIndicators) -> Dict[str, float]:
        """Calculate normalized factor scores (0-1 range)."""
        factors = {}
        
        # Completion rate trend (negative = declining = higher risk)
        # Range: -1 to 1, normalize to 0-1 where 1 = high risk
        factors['completion_rate_trend'] = self._normalize_trend(
            indicators.completion_rate_trend, inverse=True
        )
        
        # Sleep deviation (more deviation = higher risk)
        # Normalize: 0 hours deviation = 0, 3+ hours = 1
        factors['sleep_deviation'] = min(1.0, abs(indicators.sleep_deviation) / 3.0)
        
        # Stress level (higher = higher risk)
        # Already 1-10, normalize to 0-1
        factors['stress_level'] = (indicators.stress_level - 1) / 9.0
        
        # Days since check-in (more days = higher risk)
        # Normalize: 0 days = 0, 7+ days = 1
        factors['days_since_checkin'] = min(1.0, indicators.days_since_checkin / 7.0)
        
        # Streak breaks (more breaks = higher risk)
        # Normalize: 0 breaks = 0, 5+ breaks = 1
        factors['streak_breaks'] = min(1.0, indicators.streak_breaks / 5.0)
        
        # Mood trend (negative = declining = higher risk)
        factors['mood_trend'] = self._normalize_trend(
            indicators.mood_trend, inverse=True
        )
        
        # Task overload (higher ratio = higher risk)
        # Normalize: 0 = 0, 2+ = 1
        factors['task_overload'] = min(1.0, indicators.task_overload / 2.0)
        
        return factors
    
    def _normalize_trend(self, trend: float, inverse: bool = False) -> float:
        """Normalize trend value from -1..1 to 0..1 risk scale."""
        # trend: -1 (declining) to 1 (improving)
        # For risk: declining = high risk (1), improving = low risk (0)
        normalized = (trend + 1) / 2  # Convert to 0-1
        if inverse:
            normalized = 1 - normalized
        return normalized
    
    def _determine_risk_level(self, risk_score: float) -> str:
        """Determine risk level from score."""
        if risk_score >= self.RISK_THRESHOLDS['critical']:
            return 'critical'
        elif risk_score >= self.RISK_THRESHOLDS['high']:
            return 'high'
        elif risk_score >= self.RISK_THRESHOLDS['moderate']:
            return 'moderate'
        return 'low'
    
    def _generate_interventions(
        self, 
        factors: Dict[str, float], 
        risk_level: str,
        indicators: BurnoutIndicators
    ) -> List[str]:
        """Generate intervention suggestions based on risk factors."""
        interventions = []
        
        # Add header intervention based on risk level
        if risk_level == 'critical':
            interventions.append(
                "🚨 CRITICAL: You're at high risk of burnout. "
                "Consider taking a break or entering Recovery Mode."
            )
        elif risk_level == 'high':
            interventions.append(
                "⚠️ Warning: Burnout risk is elevated. "
                "Consider reducing your habit load temporarily."
            )
        
        # Factor-specific interventions
        if factors['completion_rate_trend'] > 0.6:
            interventions.append(
                "📉 Your habit completion is declining. "
                "Focus on just 1-2 key habits this week."
            )
        
        if factors['sleep_deviation'] > 0.5:
            if indicators.sleep_deviation < 0:
                interventions.append(
                    f"😴 You're sleeping {abs(indicators.sleep_deviation):.1f} hours less than usual. "
                    "Prioritize rest this week."
                )
            else:
                interventions.append(
                    f"😴 Your sleep pattern has shifted. "
                    "Try to maintain a consistent sleep schedule."
                )
        
        if factors['stress_level'] > 0.6:
            interventions.append(
                "🧘 Stress levels are elevated. "
                "Try a 5-minute breathing exercise or short walk."
            )
        
        if factors['days_since_checkin'] > 0.5:
            interventions.append(
                f"📱 You haven't checked in for {indicators.days_since_checkin} days. "
                "Take a moment to review your progress."
            )
        
        if factors['streak_breaks'] > 0.5:
            interventions.append(
                "❄️ Multiple streaks have broken recently. "
                "Consider using Streak Freezes or reducing habit difficulty."
            )
        
        if factors['mood_trend'] > 0.6:
            interventions.append(
                "😔 Your mood has been declining. "
                "Consider adding a mood-boosting activity or talking to someone."
            )
        
        if factors['task_overload'] > 0.7:
            interventions.append(
                "📋 You have a lot on your plate. "
                "Consider postponing non-essential tasks or habits."
            )
        
        if indicators.habit_load > 7:
            interventions.append(
                f"🎯 You're tracking {indicators.habit_load} habits. "
                "Consider pausing some lower-priority habits temporarily."
            )
        
        if indicators.missed_days >= 3:
            interventions.append(
                f"⏰ You've missed {indicators.missed_days} consecutive days. "
                "Start small - even one habit today counts!"
            )
        
        # Add positive reinforcement if risk is low
        if risk_level == 'low':
            interventions.append(
                "✅ You're doing great! Keep up the consistent progress."
            )
        
        return interventions
    
    def _determine_monitoring_frequency(self, risk_level: str) -> str:
        """Determine how often to reassess burnout risk."""
        frequencies = {
            'critical': 'daily',
            'high': 'every 2 days',
            'moderate': 'weekly',
            'low': 'bi-weekly'
        }
        return frequencies.get(risk_level, 'weekly')
    
    def get_recovery_plan(self, risk: BurnoutRisk) -> Dict[str, Any]:
        """
        Generate a recovery plan for high-risk users.
        
        Args:
            risk: Current burnout risk assessment
            
        Returns:
            Recovery plan with reduced expectations
        """
        if risk.risk_level not in ['high', 'critical']:
            return {
                'recommended': False,
                'message': 'Recovery mode not needed at current risk level.'
            }
        
        plan = {
            'recommended': True,
            'duration_days': 7 if risk.risk_level == 'high' else 14,
            'max_habits': 3,
            'habit_reduction': 0.5,  # Reduce to 50% of current
            'xp_multiplier': 1.5,  # Bonus XP for maintaining during recovery
            'streak_protection': True,  # Free streak freezes
            'daily_checkin_reminder': True,
            'steps': [
                "1. Select 1-3 most important habits to maintain",
                "2. Pause or reduce all other habits",
                "3. Focus on sleep and stress management",
                "4. Check in daily, even if just to mark a rest day",
                "5. Celebrate small wins - consistency matters more than intensity"
            ]
        }
        
        return plan


class BurnoutMonitor:
    """
    Continuous burnout monitoring system.
    
    Tracks burnout indicators over time and alerts when risk increases.
    """
    
    def __init__(self, history_days: int = 30):
        """
        Initialize burnout monitor.
        
        Args:
            history_days: Number of days to keep history
        """
        self.history_days = history_days
        self.predictor = BurnoutPredictor()
        self.risk_history: List[BurnoutRisk] = []
    
    def check_and_alert(
        self, 
        indicators: BurnoutIndicators
    ) -> tuple[BurnoutRisk, bool]:
        """
        Assess risk and determine if alert is needed.
        
        Args:
            indicators: Current burnout indicators
            
        Returns:
            Tuple of (risk assessment, should_alert)
        """
        risk = self.predictor.assess_risk(indicators)
        
        # Store in history
        self.risk_history.append(risk)
        
        # Trim history
        cutoff = datetime.now() - timedelta(days=self.history_days)
        self.risk_history = [
            r for r in self.risk_history 
            if r.calculated_at > cutoff
        ]
        
        # Determine if alert needed
        should_alert = self._should_alert(risk)
        
        return risk, should_alert
    
    def _should_alert(self, current_risk: BurnoutRisk) -> bool:
        """Determine if an alert should be triggered."""
        # Always alert for critical
        if current_risk.risk_level == 'critical':
            return True
        
        # Alert for high if not recently alerted
        if current_risk.risk_level == 'high':
            # Check if we've already alerted recently
            recent_high = any(
                r.risk_level in ['high', 'critical'] 
                for r in self.risk_history[-3:]  # Last 3 checks
            )
            return not recent_high
        
        # Alert for moderate if risk is increasing
        if current_risk.risk_level == 'moderate' and len(self.risk_history) >= 2:
            previous = self.risk_history[-2]
            if previous.risk_level == 'low':
                return True  # Risk increased from low to moderate
        
        return False
    
    def get_trend(self) -> str:
        """Get burnout risk trend over recent history."""
        if len(self.risk_history) < 2:
            return "insufficient_data"
        
        recent = self.risk_history[-7:]  # Last 7 assessments
        if len(recent) < 2:
            return "insufficient_data"
        
        scores = [r.risk_score for r in recent]
        
        # Simple trend: compare first half to second half
        mid = len(scores) // 2
        first_half_avg = sum(scores[:mid]) / mid
        second_half_avg = sum(scores[mid:]) / (len(scores) - mid)
        
        diff = second_half_avg - first_half_avg
        
        if diff > 10:
            return "increasing"
        elif diff < -10:
            return "decreasing"
        return "stable"
    
    def get_summary(self) -> Dict[str, Any]:
        """Get summary of burnout monitoring."""
        if not self.risk_history:
            return {
                'status': 'no_data',
                'message': 'No burnout assessments recorded yet.'
            }
        
        latest = self.risk_history[-1]
        trend = self.get_trend()
        
        return {
            'current_risk': latest.risk_score,
            'risk_level': latest.risk_level,
            'trend': trend,
            'assessments_count': len(self.risk_history),
            'last_assessment': latest.calculated_at.isoformat(),
            'highest_risk': max(r.risk_score for r in self.risk_history),
            'average_risk': sum(r.risk_score for r in self.risk_history) / len(self.risk_history)
        }