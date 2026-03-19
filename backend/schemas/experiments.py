"""
Experiments API Schemas

Pydantic models for N-of-1 experiments validation and serialization.

Phase 13: Decoupled Architecture - Backend Schemas
"""

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import date


class ExperimentBase(BaseModel):
    """Base schema for experiments."""
    name: str = Field(description="Experiment name")
    description: str = Field(default="", description="Experiment description")
    hypothesis: str = Field(default="", description="Hypothesis being tested")
    design: str = Field(default="ab", description="Experiment design: ab, aba, randomized")
    variable_name: str = Field(description="Variable being tested")
    baseline_days: int = Field(default=7, description="Baseline period days")
    intervention_days: int = Field(default=7, description="Intervention period days")


class ExperimentCreate(ExperimentBase):
    """Schema for creating an experiment."""
    pass


class ExperimentUpdate(BaseModel):
    """Schema for updating an experiment."""
    name: Optional[str] = None
    description: Optional[str] = None
    hypothesis: Optional[str] = None
    status: Optional[str] = None


class ExperimentResponse(ExperimentBase):
    """Schema for experiment response."""
    id: str = Field(description="Unique identifier")
    user_id: str = Field(description="User ID")
    status: str = Field(description="Experiment status")
    current_phase: str = Field(default="baseline", description="Current experiment phase")
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    created_at: Optional[str] = None

    class Config:
        from_attributes = True


class ExperimentResultResponse(BaseModel):
    """Schema for experiment results."""
    id: str
    experiment_id: str
    date: str
    phase: str
    variable_value: float
    outcome_value: Optional[float] = None
    notes: Optional[str] = None
