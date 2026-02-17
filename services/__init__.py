"""
Services Package

This package provides various service implementations for the tracking system.
"""

from services.ai_provider import AIProvider, ai_provider
from services.github_cortex_client import GitHubCortexClient, build_emotional_pr_body
from services.debug_console import DebugConsole, debug_console
from services.notifications import Notifications, notifications
from services.email import send_email

__all__ = [
    'AIProvider',
    'ai_provider',
    'GitHubCortexClient',
    'build_emotional_pr_body',
    'DebugConsole',
    'debug_console',
    'Notifications',
    'notifications',
    'send_email',
]
