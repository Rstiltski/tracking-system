"""
Debug Console Service

Provides debugging utilities for the tracking system.
"""

import logging
from typing import Any, Optional

logger = logging.getLogger(__name__)


class DebugConsole:
    """
    Debug console for development and troubleshooting.
    
    Provides methods for logging debug information, printing to console,
    and inspecting objects.
    """
    
    def __init__(self, enabled: bool = True):
        """
        Initialize the debug console.
        
        Args:
            enabled: Whether debug output is enabled
        """
        self.enabled = enabled
        self._log_level = logging.DEBUG
    
    def log(self, message: str, *args: Any, **kwargs: Any) -> None:
        """
        Log a debug message.
        
        Args:
            message: Message to log
            *args: Additional positional arguments
            **kwargs: Additional keyword arguments
        """
        if self.enabled:
            logger.log(self._log_level, message, *args, **kwargs)
            print(f"[DEBUG] {message}" % args if args else f"[DEBUG] {message}")
    
    def print(self, *args: Any, **kwargs: Any) -> None:
        """
        Print debug information.
        
        Args:
            *args: Arguments to print
            **kwargs: Keyword arguments for print()
        """
        if self.enabled:
            print("[DEBUG]", *args, **kwargs)
    
    def inspect(self, obj: Any, name: Optional[str] = None) -> None:
        """
        Inspect an object and print its properties.
        
        Args:
            obj: Object to inspect
            name: Optional name for the object
        """
        if self.enabled:
            if name:
                print(f"[DEBUG] Inspecting {name}:")
            else:
                print(f"[DEBUG] Inspecting {type(obj).__name__}:")
            
            if hasattr(obj, '__dict__'):
                for key, value in obj.__dict__.items():
                    print(f"  {key}: {value}")
            else:
                print(f"  Value: {obj}")
    
    def set_enabled(self, enabled: bool) -> None:
        """Enable or disable debug output."""
        self.enabled = enabled


# Default debug_console instance
debug_console = DebugConsole(enabled=True)
