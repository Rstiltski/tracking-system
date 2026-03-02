"""
Constants for the Friends page.

Contains page configuration and display settings.
"""

# Page configuration
PAGE_TITLE = "Friends - Veryfyn"
PAGE_ICON = "👥"
LAYOUT = "wide"
INITIAL_SIDEBAR_STATE = "expanded"

# Default user ID for demo
DEFAULT_USER_ID = "user-123"

# Privacy visibility options
VISIBILITY_OPTIONS = ["private", "friends", "public"]

# Activity feed settings
FEED_LIMIT = 20

# Activity types
ACTIVITY_TYPE_COMPLETION = "completion"
ACTIVITY_TYPE_STREAK = "streak"
ACTIVITY_TYPE_ACHIEVEMENT = "achievement"

# Default privacy settings
DEFAULT_PRIVACY_SETTINGS = {
    'share_achievements': True,
    'share_streaks': True,
    'share_completions': False,
    'allow_cheers': True,
    'visible_to': 'friends'
}