"""
Brain utilities module.

Provides utility functions for brain operations.
📚 REQUIRED READING BEFORE MODIFICATION:
- DEVELOPER_GUIDE.md
- LLM_AGENT_QUICKSTART.md
"""

def get_fact_window_seconds(default: int = 300) -> int:
    """
    Get the fact window duration in seconds.

    Args:
        default: Default value if not configured

    Returns:
        Fact window duration in seconds
    """
    try:
        from config import get_config
        config = get_config()
        return getattr(config, 'FACT_WINDOW_SECONDS', default)
    except Exception:
        return default
