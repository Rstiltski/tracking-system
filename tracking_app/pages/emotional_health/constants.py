"""
Constants for the Emotional Health page.

Contains neurotransmitter definitions and display settings.
"""

# Page configuration
PAGE_TITLE = "Emotional Health - Veryfyn"
PAGE_ICON = "🌈"
LAYOUT = "wide"
INITIAL_SIDEBAR_STATE = "expanded"

# Neurotransmitter display names and descriptions
NEUROTRANSMITTER_INFO = {
    'dopamine': {
        'name': 'Dopamine',
        'emoji': '🔴',
        'role': 'Joy • Reward • Pleasure',
        'high': 'Achievement, excitement',
        'low': 'Lack of motivation',
        'help': 'Controls feelings of pleasure, motivation, and reward'
    },
    'norepinephrine': {
        'name': 'Norepinephrine',
        'emoji': '🔵',
        'role': 'Stress • Energy • Focus',
        'high': 'Alertness, anxiety',
        'low': 'Fatigue, low focus',
        'help': 'Controls alertness, focus, and stress response'
    },
    'serotonin': {
        'name': 'Serotonin',
        'emoji': '🟢',
        'role': 'Satisfaction • Stability',
        'high': 'Contentment, calm',
        'low': 'Sadness, irritability',
        'help': 'Controls mood stability, satisfaction, and contentment'
    },
    'oxytocin': {
        'name': 'Oxytocin',
        'emoji': '💕',
        'role': 'Bonding',
        'help': 'Controls feelings of trust, bonding, and empathy'
    },
    'endorphins': {
        'name': 'Endorphins',
        'emoji': '✨',
        'role': 'Euphoria',
        'help': 'Controls feelings of euphoria and pain relief'
    },
    'gaba': {
        'name': 'GABA',
        'emoji': '🧘',
        'role': 'Calm',
        'help': 'Controls feelings of calm and relaxation'
    }
}

# Default neurotransmitter values
DEFAULT_NEUROTRANSMITTER_VALUE = 0.5
NEUROTRANSMITTER_STEP = 0.05
NEUROTRANSMITTER_MIN = 0.0
NEUROTRANSMITTER_MAX = 1.0

# Display settings
COLOR_CIRCLE_SIZE = 60
COLOR_CIRCLE_SIZE_PREVIEW = 80
COLOR_CIRCLE_SIZE_CARD = 40

# History settings
HISTORY_DAYS = 14
HISTORY_DISPLAY_LIMIT = 10

# Trend display
TREND_DISPLAY_COUNT = 7