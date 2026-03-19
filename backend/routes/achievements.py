"""
Achievements API Routes

REST endpoints for achievement operations.
Wraps the existing tracking_app/storage.py functions.

Phase 14: Page Consolidation & Feature Completion

Endpoints:
- GET /api/achievements - List all achievements
- GET /api/achievements/unlocked - Get user's unlocked achievements
- POST /api/achievements/{achievement_id}/unlock - Unlock an achievement
- GET /api/achievements/progress - Get user's achievement progress
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from pydantic import BaseModel
import logging
from tracking_app.storage import Storage

# Initialize router
router = APIRouter(prefix="/api/achievements", tags=["achievements"])

# Logger
logger = logging.getLogger(__name__)


def get_storage() -> Storage:
    """Dependency to get storage instance."""
    return Storage()


# ==================== Schemas ====================

class AchievementResponse(BaseModel):
    """Achievement response schema."""
    id: str
    name: str
    description: Optional[str] = None
    category: Optional[str] = None
    tier: Optional[str] = None
    unlocked_at: Optional[str] = None
    progress: Optional[int] = None
    target: Optional[int] = None


class AchievementUnlockResponse(BaseModel):
    """Response for unlocking an achievement."""
    success: bool
    achievement: Optional[AchievementResponse] = None
    message: str


class AchievementProgressResponse(BaseModel):
    """Response for achievement progress."""
    total_achievements: int
    unlocked_count: int
    locked_count: int
    achievements: List[AchievementResponse]


# ==================== Routes ====================

@router.get("", response_model=List[AchievementResponse])
async def get_achievements(
    unlocked_only: bool = False,
    storage: Storage = Depends(get_storage)
):
    """
    Get all achievements, optionally filtering to unlocked only.
    
    Args:
        unlocked_only: If True, only return unlocked achievements
        storage: Storage dependency
        
    Returns:
        List of achievement responses
    """
    try:
        achievements = storage.get_achievements(unlocked_only=unlocked_only)
        
        results = []
        for ach in achievements:
            results.append(AchievementResponse(
                id=ach.get('id', ''),
                name=ach.get('name', ''),
                description=ach.get('description'),
                category=ach.get('category'),
                tier=ach.get('tier'),
                unlocked_at=ach.get('unlocked_at'),
                progress=ach.get('progress'),
                target=ach.get('target')
            ))
        
        return results
    except Exception as e:
        logger.error(f"Error fetching achievements: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/unlocked", response_model=List[AchievementResponse])
async def get_unlocked_achievements(
    storage: Storage = Depends(get_storage)
):
    """
    Get user's unlocked achievements.
    
    Args:
        storage: Storage dependency
        
    Returns:
        List of unlocked achievement responses
    """
    try:
        achievements = storage.get_achievements(unlocked_only=True)
        
        results = []
        for ach in achievements:
            results.append(AchievementResponse(
                id=ach.get('id', ''),
                name=ach.get('name', ''),
                description=ach.get('description'),
                category=ach.get('category'),
                tier=ach.get('tier'),
                unlocked_at=ach.get('unlocked_at'),
                progress=ach.get('progress'),
                target=ach.get('target')
            ))
        
        return results
    except Exception as e:
        logger.error(f"Error fetching unlocked achievements: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{achievement_id}/unlock", response_model=AchievementUnlockResponse)
async def unlock_achievement(
    achievement_id: str,
    storage: Storage = Depends(get_storage)
):
    """
    Unlock an achievement by ID.
    
    Args:
        achievement_id: The ID of the achievement to unlock
        storage: Storage dependency
        
    Returns:
        Unlock response with success status
    """
    try:
        achievement = storage.unlock_achievement(achievement_id)
        
        if not achievement:
            return AchievementUnlockResponse(
                success=False,
                message=f"Achievement '{achievement_id}' not found"
            )
        
        return AchievementUnlockResponse(
            success=True,
            achievement=AchievementResponse(
                id=achievement.get('id', ''),
                name=achievement.get('name', ''),
                description=achievement.get('description'),
                category=achievement.get('category'),
                tier=achievement.get('tier'),
                unlocked_at=achievement.get('unlocked_at'),
                progress=achievement.get('progress'),
                target=achievement.get('target')
            ),
            message="Achievement unlocked successfully!"
        )
    except Exception as e:
        logger.error(f"Error unlocking achievement: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/progress", response_model=AchievementProgressResponse)
async def get_achievement_progress(
    storage: Storage = Depends(get_storage)
):
    """
    Get user's achievement progress summary.
    
    Args:
        storage: Storage dependency
        
    Returns:
        Progress response with counts and achievements
    """
    try:
        all_achievements = storage.get_achievements(unlocked_only=False)
        unlocked_achievements = storage.get_achievements(unlocked_only=True)
        
        results = []
        for ach in all_achievements:
            results.append(AchievementResponse(
                id=ach.get('id', ''),
                name=ach.get('name', ''),
                description=ach.get('description'),
                category=ach.get('category'),
                tier=ach.get('tier'),
                unlocked_at=ach.get('unlocked_at'),
                progress=ach.get('progress'),
                target=ach.get('target')
            ))
        
        return AchievementProgressResponse(
            total_achievements=len(all_achievements),
            unlocked_count=len(unlocked_achievements),
            locked_count=len(all_achievements) - len(unlocked_achievements),
            achievements=results
        )
    except Exception as e:
        logger.error(f"Error fetching achievement progress: {e}")
        raise HTTPException(status_code=500, detail=str(e))
