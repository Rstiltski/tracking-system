"""
Constants for the Challenges page.

Contains challenge-related configuration values.
"""

from typing import List

# Default user ID for demo
DEFAULT_USER_ID = "user-123"

# Challenge duration options (in days)
DURATION_OPTIONS: List[int] = [7, 14, 30, 60, 90]

# Default max participants (0 = unlimited)
DEFAULT_MAX_PARTICIPANTS = 0

# Leaderboard display limit
LEADERBOARD_DISPLAY_LIMIT = 10

# Check-in feed limit
CHECKIN_FEED_LIMIT = 10

# Medal emojis for leaderboard
MEDAL_EMOJIS = {
    1: "🥇",
    2: "🥈",
    3: "🥉",
}