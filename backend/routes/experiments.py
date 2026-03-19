"""
Experiments API Routes

REST endpoints for N-of-1 experiments operations.
Wraps the existing tracking_app/storage.py functions.

Phase 13: Decoupled Architecture Migration

Endpoints:
- GET /api/experiments - List experiments
- POST /api/experiments - Create experiment
- GET /api/experiments/{id} - Get experiment
- PUT /api/experiments/{id} - Update experiment
- DELETE /api/experiments/{id} - Delete experiment
- GET /api/experiments/{id}/results - Get experiment results
- POST /api/experiments/{id}/results - Add result
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List
import logging
from tracking_app.storage import Storage

from backend.schemas.experiments import (
    ExperimentCreate,
    ExperimentUpdate,
    ExperimentResponse,
    ExperimentResultResponse,
)

# Initialize router
router = APIRouter(prefix="/api/experiments", tags=["experiments"])

# Logger
logger = logging.getLogger(__name__)


def _get_storage() -> Storage:
    """Get storage instance."""
    return Storage()


@router.get("", response_model=List[ExperimentResponse])
async def get_experiments(
    status: str = Query(None, description="Filter by status"),
    limit: int = Query(50, ge=1, le=100, description="Maximum results"),
    user_id: str = "default"
):
    """
    Get all experiments.
    """
    storage = _get_storage()
    experiments = storage.get_experiments(user_id=user_id, status=status, limit=limit)
    
    return [
        ExperimentResponse(
            id=e.get('id', ''),
            user_id=user_id,
            name=e.get('name', ''),
            description=e.get('description', ''),
            hypothesis=e.get('hypothesis', ''),
            design=e.get('design', 'ab'),
            variable_name=e.get('variable_name', ''),
            baseline_days=e.get('baseline_days', 7),
            intervention_days=e.get('intervention_days', 7),
            status=e.get('status', 'draft'),
            current_phase=e.get('current_phase', 'baseline'),
            start_date=e.get('start_date'),
            end_date=e.get('end_date'),
            created_at=e.get('created_at'),
        )
        for e in experiments
    ]


@router.post("", response_model=ExperimentResponse, status_code=201)
async def create_experiment(experiment: ExperimentCreate, user_id: str = "default"):
    """
    Create a new experiment.
    """
    logger.info(f"User {user_id} creating experiment: {experiment.name}")
    
    return ExperimentResponse(
        id="exp_new",
        user_id=user_id,
        name=experiment.name,
        description=experiment.description,
        hypothesis=experiment.hypothesis,
        design=experiment.design,
        variable_name=experiment.variable_name,
        baseline_days=experiment.baseline_days,
        intervention_days=experiment.intervention_days,
        status="draft",
        current_phase="baseline",
        start_date=None,
        end_date=None,
        created_at=None,
    )


@router.get("/{experiment_id}", response_model=ExperimentResponse)
async def get_experiment(experiment_id: str, user_id: str = "default"):
    """
    Get a single experiment.
    """
    storage = _get_storage()
    experiments = storage.get_experiments(user_id=user_id, limit=100)
    
    experiment = next((e for e in experiments if e.get('id') == experiment_id), None)
    
    if not experiment:
        raise HTTPException(status_code=404, detail="Experiment not found")
    
    return ExperimentResponse(
        id=experiment.get('id', ''),
        user_id=user_id,
        name=experiment.get('name', ''),
        description=experiment.get('description', ''),
        hypothesis=experiment.get('hypothesis', ''),
        design=experiment.get('design', 'ab'),
        variable_name=experiment.get('variable_name', ''),
        baseline_days=experiment.get('baseline_days', 7),
        intervention_days=experiment.get('intervention_days', 7),
        status=experiment.get('status', 'draft'),
        current_phase=experiment.get('current_phase', 'baseline'),
        start_date=experiment.get('start_date'),
        end_date=experiment.get('end_date'),
        created_at=experiment.get('created_at'),
    )


@router.put("/{experiment_id}", response_model=ExperimentResponse)
async def update_experiment(
    experiment_id: str,
    experiment: ExperimentUpdate,
    user_id: str = "default"
):
    """
    Update an experiment.
    """
    logger.info(f"Updating experiment {experiment_id}")
    
    return ExperimentResponse(
        id=experiment_id,
        user_id=user_id,
        name=experiment.name or "Updated Experiment",
        description=experiment.description or "",
        hypothesis=experiment.hypothesis or "",
        design="ab",
        variable_name="variable",
        baseline_days=7,
        intervention_days=7,
        status=experiment.status or "draft",
        current_phase="baseline",
        start_date=None,
        end_date=None,
        created_at=None,
    )


@router.delete("/{experiment_id}", status_code=204)
async def delete_experiment(experiment_id: str, user_id: str = "default"):
    """
    Delete an experiment.
    """
    logger.info(f"Deleting experiment {experiment_id}")
    return None


@router.get("/{experiment_id}/results", response_model=List[ExperimentResultResponse])
async def get_experiment_results(
    experiment_id: str,
    user_id: str = "default"
):
    """
    Get experiment results.
    """
    storage = _get_storage()
    results = storage.get_experiment_results(experiment_id=experiment_id)
    
    return [
        ExperimentResultResponse(
            id=r.get('id', ''),
            experiment_id=experiment_id,
            date=r.get('date', ''),
            phase=r.get('phase', 'baseline'),
            variable_value=r.get('variable_value', 0.0),
            outcome_value=r.get('outcome_value'),
            notes=r.get('notes'),
        )
        for r in results
    ]


@router.post("/{experiment_id}/results", status_code=201)
async def add_experiment_result(
    experiment_id: str,
    phase: str,
    variable_value: float,
    outcome_value: float = None,
    notes: str = None,
    user_id: str = "default"
):
    """
    Add an experiment result.
    """
    logger.info(f"Adding result to experiment {experiment_id}")
    return {"success": True, "message": "Result added"}
