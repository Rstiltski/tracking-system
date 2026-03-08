"""
Helper functions for the Data Export page.

Contains export management utilities.
"""

from pathlib import Path
from typing import Tuple, Optional, Any

from .constants import DEFAULT_DB_NAME, DEFAULT_EXPORT_DIR, DEFAULT_USER_ID


def get_export_paths() -> Tuple[Path, Path]:
    """
    Get the database and export directory paths.
    
    Returns:
        Tuple of (db_path, export_dir)
    """
    db_path = Path(__file__).parent.parent.parent / DEFAULT_DB_NAME
    export_dir = Path(__file__).parent.parent.parent / DEFAULT_EXPORT_DIR
    return db_path, export_dir


def get_exporter():
    """
    Get or create the data exporter instance.
    
    Returns:
        DataExporter instance or None if brain module not available
    """
    try:
        from brain.data_export import DataExporter
        
        db_path, export_dir = get_export_paths()
        return DataExporter(db_path=str(db_path), export_dir=str(export_dir))
    except ImportError:
        return None


def get_export_modules():
    """
    Get available export modules.
    
    Returns:
        Dictionary of export modules or empty dict if brain module not available
    """
    try:
        from brain.data_export import EXPORT_MODULES
        return EXPORT_MODULES
    except ImportError:
        return {}


def get_all_module_names() -> list:
    """
    Get list of all module names.
    
    Returns:
        List of module names
    """
    try:
        from brain.data_export import EXPORT_MODULES
        return list(EXPORT_MODULES.keys())
    except ImportError:
        return []


def execute_export(
    exporter,
    export_format: str,
    selected_modules: list,
    include_archived: bool,
    compression: bool
) -> Optional[Any]:
    """
    Execute an export request.
    
    Args:
        exporter: DataExporter instance
        export_format: Format to export (json, csv, sqlite)
        selected_modules: List of modules to export
        include_archived: Whether to include archived data
        compression: Whether to compress output
        
    Returns:
        Export result or None on error
    """
    try:
        request = exporter.create_request(
            user_id=DEFAULT_USER_ID,
            format=export_format,
            modules=selected_modules,
            include_archived=include_archived,
            compression=compression
        )
        
        result = exporter.execute(request.id)
        return result
    except Exception:
        return None