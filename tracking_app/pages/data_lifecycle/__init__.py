"""
Data Lifecycle page module.

Provides data lifecycle management components.
"""

from .constants import *
from .helpers import get_lifecycle_manager, format_duration
from .session_state import init_session_state
from .components import (
    render_retention_policies,
    render_gdpr_compliance,
    render_data_reset,
)