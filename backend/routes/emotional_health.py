"""
Emotional Health API Routes

REST endpoints for emotional state operations.
Wraps the existing tracking_app/storage.py emotional state functions.

Phase 14: Page Consolidation & Feature Completion

Endpoints:
- GET /api/emotional-health - Get emotional states
- GET /api/emotional-health/latest - Get latest emotional state
- POST /api/emotional-health - Create emotional state
- DELETE /api/emotional-health/{state_id} - Delete emotional state
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional
from pydantic import BaseModel
from datetime import date
import logging
from tracking_app.storage import Storage

# Initialize router
router = APIRouter(prefix="/api/emotional-health", tags=["emotional-health"])

# Logger
logger = logging.getLogger(__name__)


def get_storage() -> Storage:
    """Dependency to get storage instance."""
    return Storage()


# ==================== Schemas ====================

class EmotionalStateCreate(BaseModel):
    """Request schema for creating emotional state."""
    dopamine: float
    norepinephrine: float
    serotonin: float
    oxytocin: float = 0.0
    endorphins: float = 0.0
    gaba: float = 0.0
    notes: str = ""
    triggers: Optional[List[str]] = None


class EmotionalStateResponse(BaseModel):
    """Response schema for emotional state."""
    id: str
    timestamp: str
    dopamine: float
    norepinephrine: float
    serotonin: float
    oxytocin: float
    endorphins: float
    gaba: float
    notes: Optional[str] = None
    triggers: Optional[List[str]] = None
    hex_color: Optional[str] = None
    emotion_label: Optional[str] = None
    emotion_category: Optional[str] = None


# ==================== Routes ====================

@router.get("", response_model=List[EmotionalStateResponse])
async def get_emotional_states(
    start_date: Optional[date] = Query(None, description="Start date for filtering"),
    end_date: Optional[date] = Query(None, description="End date for filtering"),
    limit: int = Query(100, ge=1, le=500, description="Max records to return"),
    storage: Storage = Depends(get_storage)
):
    """
    Get emotional states within a date range.
    
    Args:
        start_date: Filter states from this date
        end_date: Filter states until this date
        limit: Maximum number of records
        storage: Storage dependency
        
    Returns:
        List of emotional state responses
    """
    try:
        states = storage.get_emotional_states(
            start_date=start_date,
            end_date=end_date,
            limit=limit
        )
        
        results = []
        for state in states:
            triggers = state.get('triggers')
            if isinstance(triggers, str):
                import json
                try:
                    triggers = json.loads(triggers)
                except:
                    triggers = None
            
            results.append(EmotionalStateResponse(
                id=state.get('id', ''),
                timestamp=state.get('timestamp', ''),
                dopamine=state.get('dopamine', 0.0),
                norepinephrine=state.get('norepinephrine', 0.0),
                serotonin=state.get('serotonin', 0.0),
                oxytocin=state.get('oxytocin', 0.0),
                endorphins=state.get('endorphins', 0.0),
                gaba=state.get('gaba', 0.0),
                notes=state.get('notes'),
                triggers=triggers,
                hex_color=state.get('hex_color'),
                emotion_label=state.get('emotion_label'),
                emotion_category=state.get('emotion_category')
            ))
        
        return results
    except Exception as e:
        logger.error(f"Error fetching emotional states: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/latest", response_model=Optional[EmotionalStateResponse])
async def get_latest_emotional_state(
    storage: Storage = Depends(get_storage)
):
    """
    Get the most recent emotional state.
    
    Args:
        storage: Storage dependency
        
    Returns:
        Latest emotional state or None
    """
    try:
        state = storage.get_latest_emotional_state()
        
        if not state:
            return None
        
        triggers = state.get('triggers')
        if isinstance(triggers, str):
            import json
            try:
                triggers = json.loads(triggers)
            except:
                triggers = None
        
        return EmotionalStateResponse(
            id=state.get('id', ''),
            timestamp=state.get('timestamp', ''),
            dopamine=state.get('dopamine', 0.0),
            norepinephrine=state.get('norepinephrine', 0.0),
            serotonin=state.get('serotonin', 0.0),
            oxytocin=state.get('oxytocin', 0.0),
            endorphins=state.get('endorphins', 0.0),
            gaba=state.get('gaba', 0.0),
            notes=state.get('notes'),
            triggers=triggers,
            hex_color=state.get('hex_color'),
            emotion_label=state.get('emotion_label'),
            emotion_category=state.get('emotion_category')
        )
    except Exception as e:
        logger.error(f"Error fetching latest emotional state: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("", response_model=EmotionalStateResponse)
async def create_emotional_state(
    state_data: EmotionalStateCreate,
    storage: Storage = Depends(get_storage)
):
    """
    Create a new emotional state entry.
    
    Args:
        state_data: Emotional state data
        storage: Storage dependency
        
    Returns:
        Created emotional state
    """
    try:
        state = storage.create_emotional_state(
            dopamine=state_data.dopamine,
            norepinephrine=state_data.norepinephrine,
            serotonin=state_data.serotonin,
            oxytocin=state_data.oxytocin,
            endorphins=state_data.endorphins,
            gaba=state_data.gaba,
            notes=state_data.notes,
            triggers=state_data.triggers
        )
        
        triggers = state.get('triggers')
        if isinstance(triggers, str):
            import json
            try:
                triggers = json.loads(triggers)
            except:
                triggers = None
        
        return EmotionalStateResponse(
            id=state.get('id', ''),
            timestamp=state.get('timestamp', ''),
            dopamine=state.get('dopamine', 0.0),
            norepinephrine=state.get('norepinephrine', 0.0),
            serotonin=state.get('serotonin', 0.0),
            oxytocin=state.get('oxytocin', 0.0),
            endorphins=state.get('endorphins', 0.0),
            gaba=state.get('gaba', 0.0),
            notes=state.get('notes'),
            triggers=triggers,
            hex_color=state.get('hex_color'),
            emotion_label=state.get('emotion_label'),
            emotion_category=state.get('emotion_category')
        )
    except Exception as e:
        logger.error(f"Error creating emotional state: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{state_id}")
async def delete_emotional_state(
    state_id: str,
    storage: Storage = Depends(get_storage)
):
    """
    Delete an emotional state.
    
    Args:
        state_id: ID of the emotional state to delete
        storage: Storage dependency
        
    Returns:
        Success message
    """
    try:
        success = storage.delete_emotional_state(state_id)
        
        if not success:
            raise HTTPException(
                status_code=404,
                detail=f"Emotional state '{state_id}' not found"
            )
        
        return {"success": True, "message": "Emotional state deleted"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting emotional state: {e}")
        raise HTTPException(status_code=500, detail=str(e))
