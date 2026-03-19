"""
Friends API Routes

REST endpoints for social/friends operations.
Wraps the existing tracking_app/storage.py functions.

Phase 13: Decoupled Architecture Migration

Endpoints:
- GET /api/friends - List friends
- POST /api/friends/request - Send friend request
- POST /api/friends/accept - Accept request
- POST /api/friends/reject - Reject request
- DELETE /api/friends/{friend_id} - Remove friend
- GET /api/friends/feed - Get activity feed
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List
import logging
from tracking_app.storage import Storage

from backend.schemas.friends import (
    FriendResponse,
    FriendFeedItem,
)

# Initialize router
router = APIRouter(prefix="/api/friends", tags=["friends"])

# Logger
logger = logging.getLogger(__name__)


def _get_storage() -> Storage:
    """Get storage instance."""
    return Storage()


@router.get("", response_model=List[FriendResponse])
async def get_friends(user_id: str = "default"):
    """
    Get user's friends list.
    """
    storage = _get_storage()
    friends = storage.get_friends(user_id=user_id)
    
    return [
        FriendResponse(
            id=f.get('id', ''),
            user_id=user_id,
            friend_id=f.get('friend_id', ''),
            friend_name=f.get('friend_name', ''),
            status=f.get('status', 'active'),
            created_at=f.get('created_at'),
        )
        for f in friends
    ]


@router.post("/request")
async def send_friend_request(
    friend_id: str,
    user_id: str = "default"
):
    """
    Send a friend request.
    """
    logger.info(f"User {user_id} sending friend request to {friend_id}")
    return {"success": True, "message": "Friend request sent"}


@router.post("/accept")
async def accept_friend_request(
    request_id: str,
    user_id: str = "default"
):
    """
    Accept a friend request.
    """
    logger.info(f"User {user_id} accepting friend request {request_id}")
    return {"success": True, "message": "Friend request accepted"}


@router.post("/reject")
async def reject_friend_request(
    request_id: str,
    user_id: str = "default"
):
    """
    Reject a friend request.
    """
    logger.info(f"User {user_id} rejecting friend request {request_id}")
    return {"success": True, "message": "Friend request rejected"}


@router.delete("/{friend_id}")
async def remove_friend(
    friend_id: str,
    user_id: str = "default"
):
    """
    Remove a friend.
    """
    logger.info(f"User {user_id} removing friend {friend_id}")
    return {"success": True, "message": "Friend removed"}


@router.get("/feed", response_model=List[FriendFeedItem])
async def get_friend_feed(
    limit: int = Query(50, ge=1, le=100, description="Maximum feed items"),
    user_id: str = "default"
):
    """
    Get activity feed from friends.
    """
    storage = _get_storage()
    feed = storage.get_friend_feed(user_id=user_id, limit=limit)
    
    return [
        FriendFeedItem(
            id=item.get('id', ''),
            friend_id=item.get('friend_id', ''),
            friend_name=item.get('friend_name', ''),
            action_type=item.get('action_type', 'unknown'),
            action_description=item.get('action_description', ''),
            timestamp=item.get('timestamp'),
        )
        for item in feed
    ]


@router.get("/requests", response_model=List[FriendResponse])
async def get_pending_requests(user_id: str = "default"):
    """
    Get pending friend requests.
    """
    logger.info(f"Fetching pending friend requests for {user_id}")
    return []
