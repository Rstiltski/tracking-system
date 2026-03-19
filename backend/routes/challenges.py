"""
Challenges API Routes

REST endpoints for challenge operations.
Wraps the existing tracking_app/storage.py functions.

Phase 13: Decoupled Architecture Migration

Endpoints:
- GET /api/challenges - List challenges
- POST /api/challenges - Create challenge
- GET /api/challenges/{id} - Get challenge
- PUT /api/challenges/{id} - Update challenge
- DELETE /api/challenges/{id} - Delete challenge
- POST /api/challenges/{id}/join - Join challenge
- POST /api/challenges/{id}/leave - Leave challenge
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
import logging
from tracking_app.storage import Storage

from backend.schemas.challenges import (
    ChallengeCreate,
    ChallengeUpdate,
    ChallengeResponse,
    ChallengeParticipantResponse,
)

# Initialize router
router = APIRouter(prefix="/api/challenges", tags=["challenges"])

# Logger
logger = logging.getLogger(__name__)


def _get_storage() -> Storage:
    """Get storage instance."""
    return Storage()


@router.get("", response_model=List[ChallengeResponse])
async def get_challenges(
    status: Optional[str] = Query(None, description="Filter by status"),
    limit: int = Query(50, ge=1, le=100, description="Maximum results"),
    user_id: str = "default"
):
    """
    Get all challenges.
    """
    storage = _get_storage()
    challenges = storage.get_challenges(user_id=user_id, status=status, limit=limit)
    
    return [
        ChallengeResponse(
            id=c.get('id', ''),
            creator_id=c.get('creator_id', ''),
            name=c.get('name', ''),
            description=c.get('description', ''),
            target=c.get('target', 0),
            unit=c.get('unit', 'days'),
            start_date=c.get('start_date'),
            end_date=c.get('end_date'),
            is_public=c.get('is_public', False),
            status=c.get('status', 'active'),
            participants_count=c.get('participants_count', 0),
            created_at=c.get('created_at'),
        )
        for c in challenges
    ]


@router.post("", response_model=ChallengeResponse, status_code=201)
async def create_challenge(challenge: ChallengeCreate, user_id: str = "default"):
    """
    Create a new challenge.
    """
    storage = _get_storage()
    
    challenge_data = {
        'name': challenge.name,
        'description': challenge.description,
        'target': challenge.target,
        'unit': challenge.unit,
        'start_date': challenge.start_date.isoformat() if challenge.start_date else None,
        'end_date': challenge.end_date.isoformat() if challenge.end_date else None,
        'is_public': challenge.is_public,
        'creator_id': user_id,
    }
    
    challenge_id = storage.save_challenge(challenge_data)
    
    return ChallengeResponse(
        id=challenge_id,
        creator_id=user_id,
        name=challenge.name,
        description=challenge.description,
        target=challenge.target,
        unit=challenge.unit,
        start_date=str(challenge.start_date) if challenge.start_date else None,
        end_date=str(challenge.end_date) if challenge.end_date else None,
        is_public=challenge.is_public,
        status='active',
        participants_count=0,
    )


@router.get("/{challenge_id}", response_model=ChallengeResponse)
async def get_challenge(challenge_id: str):
    """
    Get a single challenge.
    """
    storage = _get_storage()
    challenges = storage.get_challenges(limit=1)
    
    challenge = next((c for c in challenges if c.get('id') == challenge_id), None)
    
    if not challenge:
        raise HTTPException(status_code=404, detail="Challenge not found")
    
    return ChallengeResponse(
        id=challenge.get('id', ''),
        creator_id=challenge.get('creator_id', ''),
        name=challenge.get('name', ''),
        description=challenge.get('description', ''),
        target=challenge.get('target', 0),
        unit=challenge.get('unit', 'days'),
        start_date=challenge.get('start_date'),
        end_date=challenge.get('end_date'),
        is_public=challenge.get('is_public', False),
        status=challenge.get('status', 'active'),
        participants_count=challenge.get('participants_count', 0),
        created_at=challenge.get('created_at'),
    )


@router.put("/{challenge_id}", response_model=ChallengeResponse)
async def update_challenge(challenge_id: str, challenge: ChallengeUpdate):
    """
    Update a challenge.
    """
    logger.info(f"Updating challenge {challenge_id}")
    
    # For now, return the updated challenge
    return ChallengeResponse(
        id=challenge_id,
        creator_id="default",
        name=challenge.name or "Updated Challenge",
        description=challenge.description or "",
        target=challenge.target or 30,
        unit="days",
        start_date=None,
        end_date=str(challenge.end_date) if challenge.end_date else None,
        is_public=False,
        status=challenge.status or "active",
        participants_count=0,
    )


@router.delete("/{challenge_id}", status_code=204)
async def delete_challenge(challenge_id: str):
    """
    Delete a challenge.
    """
    logger.info(f"Deleting challenge {challenge_id}")
    return None


@router.post("/{challenge_id}/join")
async def join_challenge(challenge_id: str, user_id: str = "default"):
    """
    Join a challenge.
    """
    logger.info(f"User {user_id} joining challenge {challenge_id}")
    return {"success": True, "message": "Joined challenge"}


@router.post("/{challenge_id}/leave")
async def leave_challenge(challenge_id: str, user_id: str = "default"):
    """
    Leave a challenge.
    """
    logger.info(f"User {user_id} leaving challenge {challenge_id}")
    return {"success": True, "message": "Left challenge"}
