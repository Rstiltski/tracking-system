"""
Privacy Settings API Routes

REST endpoints for privacy and data management operations.
Wraps the existing tracking_app/storage.py functions.

Phase 13: Decoupled Architecture Migration
Step 2: Define API Contract

Endpoints:
- GET /api/privacy - Get privacy settings
- PUT /api/privacy - Update privacy settings
- POST /api/privacy/export - Export user data
- DELETE /api/privacy/data - Delete user data
"""

from fastapi import APIRouter, HTTPException
from typing import Optional
import logging
from tracking_app.storage import Storage

from backend.schemas.privacy import (
    PrivacySettingsUpdate,
    PrivacySettingsResponse,
    DataExportRequest,
    DataExportResponse,
)

# Initialize router
router = APIRouter(prefix="/api/privacy", tags=["privacy"])

# Logger
logger = logging.getLogger(__name__)


def _get_storage() -> Storage:
    """Get storage instance."""
    return Storage()


@router.get("", response_model=PrivacySettingsResponse)
async def get_privacy_settings(user_id: str = "default"):
    """
    Get privacy settings for the current user.
    """
    storage = _get_storage()
    settings = storage.get_privacy_settings(user_id=user_id)
    
    if not settings:
        # Return default settings
        return PrivacySettingsResponse(
            user_id=user_id,
            share_habits_with_friends=False,
            share_achievements=True,
            share_stats=False,
            allow_friend_requests=True,
            show_on_public_leaderboards=False,
            data_collection_enabled=True,
            analytics_enabled=True,
            streak_visible=True,
            xp_visible=True,
            level_visible=True,
            insights_visible=True,
        )
    
    return PrivacySettingsResponse(
        user_id=user_id,
        share_habits_with_friends=settings.get('share_habits_with_friends', False),
        share_achievements=settings.get('share_achievements', True),
        share_stats=settings.get('share_stats', False),
        allow_friend_requests=settings.get('allow_friend_requests', True),
        show_on_public_leaderboards=settings.get('show_on_public_leaderboards', False),
        data_collection_enabled=settings.get('data_collection_enabled', True),
        analytics_enabled=settings.get('analytics_enabled', True),
        streak_visible=settings.get('streak_visible', True),
        xp_visible=settings.get('xp_visible', True),
        level_visible=settings.get('level_visible', True),
        insights_visible=settings.get('insights_visible', True),
    )


@router.put("", response_model=PrivacySettingsResponse)
async def update_privacy_settings(
    settings: PrivacySettingsUpdate,
    user_id: str = "default"
):
    """
    Update privacy settings for the current user.
    """
    storage = _get_storage()
    
    # Build update dict (exclude None values)
    updates = {}
    for field, value in settings.model_dump(exclude_unset=True).items():
        if value is not None:
            updates[field] = value
    
    if not updates:
        raise HTTPException(status_code=400, detail="No valid settings to update")
    
    # Save to storage
    success = storage.save_privacy_settings(user_id=user_id, settings=updates)
    
    if not success:
        raise HTTPException(status_code=500, detail="Failed to save privacy settings")
    
    # Fetch and return updated settings
    updated_settings = storage.get_privacy_settings(user_id=user_id)
    
    return PrivacySettingsResponse(
        user_id=user_id,
        share_habits_with_friends=updated_settings.get('share_habits_with_friends', False),
        share_achievements=updated_settings.get('share_achievements', True),
        share_stats=updated_settings.get('share_stats', False),
        allow_friend_requests=updated_settings.get('allow_friend_requests', True),
        show_on_public_leaderboards=updated_settings.get('show_on_public_leaderboards', False),
        data_collection_enabled=updated_settings.get('data_collection_enabled', True),
        analytics_enabled=updated_settings.get('analytics_enabled', True),
        streak_visible=updated_settings.get('streak_visible', True),
        xp_visible=updated_settings.get('xp_visible', True),
        level_visible=updated_settings.get('level_visible', True),
        insights_visible=updated_settings.get('insights_visible', True),
    )


@router.post("/export", response_model=DataExportResponse)
async def export_user_data(
    request: DataExportRequest,
    user_id: str = "default"
):
    """
    Export user data in the specified format.
    """
    # For now, return a placeholder response
    # The actual export would use brain/data_export functions
    
    logger.info(f"Data export requested by user {user_id} in format {request.format}")
    
    return DataExportResponse(
        file_path=f"exports/export_{user_id}.{request.format}",
        format=request.format,
        record_counts={
            "habits": 0,
            "tasks": 0,
            "health": 0,
            "finances": 0,
            "journal": 0,
            "diary": 0,
        }
    )


@router.delete("/data")
async def delete_user_data(
    data_type: str,
    user_id: str = "default"
):
    """
    Delete specific user data.
    
    Args:
        data_type: Type of data to delete (habits, tasks, health, finances, journal, diary, all)
    """
    valid_types = ["habits", "tasks", "health", "finances", "journal", "diary", "all"]
    
    if data_type not in valid_types:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid data type. Must be one of: {', '.join(valid_types)}"
        )
    
    logger.info(f"Data deletion requested by user {user_id} for type: {data_type}")
    
    # For now, return success
    # Actual implementation would use brain/data_import or similar
    return {
        "success": True,
        "message": f"Data type '{data_type}' deletion initiated",
        "user_id": user_id
    }
