"""
Brain Analysis Module

This module provides analytical capabilities for the tracking system:
- Correlation analysis between habits, health, and context
- Predictive Context Sensitivity (PCS) scoring
- Burnout prediction and intervention

Key Components:
- CorrelationEngine: Statistical correlation analysis
- PCSEngine: Predict habit fragility from context
- BurnoutPredictor: Assess and prevent user burnout

Usage:
    from brain.analysis import CorrelationEngine, PCSEngine, BurnoutPredictor
    
    # Correlation analysis
    engine = CorrelationEngine()
    result = engine.pearson(sleep_data, completion_data)
    
    # PCS scoring
    pcs = PCSEngine()
    score = pcs.calculate_pcs(completions, context_history)
    
    # Burnout prediction
    predictor = BurnoutPredictor()
    risk = predictor.assess_risk(indicators)
"""

from brain.analysis.correlation import (
    CorrelationEngine, 
    CorrelationResult,
    Insight,
    InsightGenerator
)
from brain.analysis.prediction import (
    PCSEngine, 
    PCSScore, 
    ContextVariables
)
from brain.analysis.burnout import (
    BurnoutPredictor, 
    BurnoutIndicators, 
    BurnoutRisk,
    BurnoutMonitor
)
from brain.analysis.time_views import (
    TimeViewsProcessor,
    CalendarProcessor,
    DayData,
    WeekData,
    MonthData,
)

__all__ = [
    # Correlation
    'CorrelationEngine',
    'CorrelationResult',
    'Insight',
    'InsightGenerator',
    
    # Prediction
    'PCSEngine',
    'PCSScore',
    'ContextVariables',
    
    # Burnout
    'BurnoutPredictor',
    'BurnoutIndicators',
    'BurnoutRisk',
    'BurnoutMonitor',
    
    # Time Views
    'TimeViewsProcessor',
    'CalendarProcessor',
    'DayData',
    'WeekData',
    'MonthData',
]

__version__ = '1.0.0'