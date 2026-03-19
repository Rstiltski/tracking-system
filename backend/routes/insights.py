"""
Insights API Routes

REST endpoints for insight operations.
Wraps the existing tracking_app/storage.py insight functions.

Phase 14: Page Consolidation & Feature Completion

Endpoints:
- GET /api/insights - Get insights
- GET /api/insights/{insight_id} - Get single insight
- POST /api/insights - Save an insight
- POST /api/insights/{insight_id}/read - Mark insight as read
- DELETE /api/insights/{insight_id} - Delete insight
- GET /api/insights/burnout/all - Get all burnout risks
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional
from pydantic import BaseModel
import logging
from tracking_app.storage import Storage

# Initialize router
router = APIRouter(prefix="/api/insights", tags=["insights"])

# Logger
logger = logging.getLogger(__name__)


def get_storage() -> Storage:
    """Dependency to get storage instance."""
    return Storage()


# ==================== Schemas ====================

class InsightCreate(BaseModel):
    """Request schema for creating an insight."""
    insight_type: str
    title: str
    description: str = ""
    data: Optional[dict] = None


class InsightResponse(BaseModel):
    """Response schema for insight."""
    id: str
    user_id: str
    insight_type: str
    title: str
    description: Optional[str] = None
    data: Optional[dict] = None
    created_at: str
    is_read: bool = False


class BurnoutRiskResponse(BaseModel):
    """Response schema for burnout risk."""
    habit_id: str
    risk_score: float
    risk_level: str
    contributing_factors: Optional[dict] = None
    assessment_date: Optional[str] = None


# ==================== Routes ====================

@router.get("", response_model=List[InsightResponse])
async def get_insights(
    insight_type: Optional[str] = Query(None, description="Filter by insight type"),
    limit: int = Query(50, ge=1, le=200, description="Max records to return"),
    storage: Storage = Depends(get_storage)
):
    """
    Get insights, optionally filtered by type.
    
    Args:
        insight_type: Filter by type (correlation, burnout, prediction, etc.)
        limit: Maximum number of records
        storage: Storage dependency
        
    Returns:
        List of insight responses
    """
    try:
        insights = storage.get_insights(insight_type=insight_type, limit=limit)
        
        results = []
        for insight in insights:
            is_read = bool(insight.get('is_read', 0))
            results.append(InsightResponse(
                id=insight.get('id', ''),
                user_id=insight.get('user_id', 'default'),
                insight_type=insight.get('insight_type', ''),
                title=insight.get('title', ''),
                description=insight.get('description'),
                data=insight.get('data'),
                created_at=insight.get('created_at', ''),
                is_read=is_read
            ))
        
        return results
    except Exception as e:
        logger.error(f"Error fetching insights: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{insight_id}", response_model=InsightResponse)
async def get_insight(
    insight_id: str,
    storage: Storage = Depends(get_storage)
):
    """
    Get a single insight by ID.
    
    Args:
        insight_id: The ID of the insight
        storage: Storage dependency
        
    Returns:
        Insight response
    """
    try:
        insight = storage.get_insight(insight_id)
        
        if not insight:
            raise HTTPException(
                status_code=404,
                detail=f"Insight '{insight_id}' not found"
            )
        
        is_read = bool(insight.get('is_read', 0))
        return InsightResponse(
            id=insight.get('id', ''),
            user_id=insight.get('user_id', 'default'),
            insight_type=insight.get('insight_type', ''),
            title=insight.get('title', ''),
            description=insight.get('description'),
            data=insight.get('data'),
            created_at=insight.get('created_at', ''),
            is_read=is_read
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching insight: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("", response_model=InsightResponse)
async def create_insight(
    insight_data: InsightCreate,
    storage: Storage = Depends(get_storage)
):
    """
    Save an insight.
    
    Args:
        insight_data: Insight data
        storage: Storage dependency
        
    Returns:
        Created insight
    """
    try:
        insight = storage.save_insight(
            insight_type=insight_data.insight_type,
            title=insight_data.title,
            description=insight_data.description,
            data=insight_data.data
        )
        
        is_read = bool(insight.get('is_read', 0))
        return InsightResponse(
            id=insight.get('id', ''),
            user_id=insight.get('user_id', 'default'),
            insight_type=insight.get('insight_type', ''),
            title=insight.get('title', ''),
            description=insight.get('description'),
            data=insight.get('data'),
            created_at=insight.get('created_at', ''),
            is_read=is_read
        )
    except Exception as e:
        logger.error(f"Error creating insight: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{insight_id}/read")
async def mark_insight_read(
    insight_id: str,
    storage: Storage = Depends(get_storage)
):
    """
    Mark an insight as read.
    
    Args:
        insight_id: The ID of the insight
        storage: Storage dependency
        
    Returns:
        Success message
    """
    try:
        success = storage.mark_insight_read(insight_id)
        
        if not success:
            raise HTTPException(
                status_code=404,
                detail=f"Insight '{insight_id}' not found"
            )
        
        return {"success": True, "message": "Insight marked as read"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error marking insight as read: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{insight_id}")
async def delete_insight(
    insight_id: str,
    storage: Storage = Depends(get_storage)
):
    """
    Delete an insight.
    
    Args:
        insight_id: The ID of the insight
        storage: Storage dependency
        
    Returns:
        Success message
    """
    try:
        success = storage.delete_insight(insight_id)
        
        if not success:
            raise HTTPException(
                status_code=404,
                detail=f"Insight '{insight_id}' not found"
            )
        
        return {"success": True, "message": "Insight deleted"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting insight: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/burnout/all", response_model=List[BurnoutRiskResponse])
async def get_all_burnout_risks(
    min_risk_level: str = Query("moderate", description="Minimum risk level to return"),
    storage: Storage = Depends(get_storage)
):
    """
    Get all habits with burnout risk.
    
    Args:
        min_risk_level: Minimum risk level (low, moderate, high, critical)
        storage: Storage dependency
        
    Returns:
        List of burnout risk responses
    """
    try:
        at_risk = storage.get_all_at_risk_habits(min_risk_level=min_risk_level)
        
        results = []
        for item in at_risk:
            results.append(BurnoutRiskResponse(
                habit_id=item.get('habit_id', ''),
                risk_score=item.get('risk_score', 0.0),
                risk_level=item.get('risk_level', 'low'),
                contributing_factors=item.get('contributing_factors'),
                assessment_date=item.get('assessment_date')
            ))
        
        return results
    except Exception as e:
        logger.error(f"Error fetching burnout risks: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/burnout/{habit_id}", response_model=Optional[BurnoutRiskResponse])
async def get_burnout_risk(
    habit_id: str,
    storage: Storage = Depends(get_storage)
):
    """
    Get burnout risk for a specific habit.
    
    Args:
        habit_id: The ID of the habit
        storage: Storage dependency
        
    Returns:
        Burnout risk response
    """
    try:
        risk = storage.get_burnout_risk(habit_id)
        
        if not risk:
            return None
        
        return BurnoutRiskResponse(
            habit_id=habit_id,
            risk_score=risk.risk_score,
            risk_level=risk.risk_level.value if hasattr(risk.risk_level, 'value') else str(risk.risk_level),
            contributing_factors=risk.contributing_factors,
            assessment_date=risk.assessment_date.isoformat() if risk.assessment_date else None
        )
    except Exception as e:
        logger.error(f"Error fetching burnout risk: {e}")
        raise HTTPException(status_code=500, detail=str(e))
