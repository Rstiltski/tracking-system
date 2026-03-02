"""
Helper functions for the Data Import page.

Contains import management utilities.
"""

import os
import tempfile
from typing import Optional, Tuple

from .constants import DEFAULT_USER_ID, AVAILABLE_MODULES


def get_importer():
    """
    Get or create the data importer instance.
    
    Returns:
        DataImporter instance or None if brain module not available
    """
    try:
        from brain.data_import import DataImporter
        from tracking_app.database import get_db
        
        db = get_db()
        return DataImporter(db_connection=db)
    except ImportError:
        return None


def get_available_modules() -> list:
    """
    Get list of available import modules.
    
    Returns:
        List of module names
    """
    return AVAILABLE_MODULES.copy()


def save_uploaded_file(uploaded_file) -> Tuple[Optional[str], Optional[str]]:
    """
    Save an uploaded file to a temporary location.
    
    Args:
        uploaded_file: Streamlit uploaded file object
        
    Returns:
        Tuple of (temp_path, error_message)
    """
    try:
        file_extension = uploaded_file.name.split('.')[-1]
        with tempfile.NamedTemporaryFile(
            delete=False, 
            suffix=f".{file_extension}"
        ) as tmp:
            tmp.write(uploaded_file.getvalue())
            return tmp.name, None
    except Exception as e:
        return None, str(e)


def cleanup_temp_file(file_path: str) -> None:
    """
    Clean up a temporary file.
    
    Args:
        file_path: Path to the temporary file
    """
    try:
        if os.path.exists(file_path):
            os.unlink(file_path)
    except Exception:
        pass


def get_file_info(uploaded_file) -> dict:
    """
    Get information about an uploaded file.
    
    Args:
        uploaded_file: Streamlit uploaded file object
        
    Returns:
        Dictionary with file information
    """
    file_type = uploaded_file.name.split('.')[-1].upper()
    file_size_kb = uploaded_file.size / 1024
    
    return {
        "name": uploaded_file.name,
        "type": file_type,
        "size_kb": file_size_kb
    }


def preview_import(importer, file_path: str, modules: list):
    """
    Preview an import operation.
    
    Args:
        importer: DataImporter instance
        file_path: Path to the import file
        modules: List of modules to import
        
    Returns:
        Preview result or None on error
    """
    try:
        return importer.preview(file_path, modules)
    except Exception:
        return None


def execute_import(
    importer,
    file_path: str,
    strategy,
    modules: list,
    dry_run: bool
):
    """
    Execute an import operation.
    
    Args:
        importer: DataImporter instance
        file_path: Path to the import file
        strategy: Conflict resolution strategy
        modules: List of modules to import
        dry_run: Whether this is a dry run
        
    Returns:
        Import result or None on error
    """
    try:
        return importer.import_file(
            file_path=file_path,
            user_id=DEFAULT_USER_ID,
            strategy=strategy,
            modules=modules,
            dry_run=dry_run
        )
    except Exception:
        return None


def send_import_notification(importer, records_imported: int) -> None:
    """
    Send a notification about the import result.
    
    Args:
        importer: DataImporter instance
        records_imported: Number of records imported
    """
    try:
        from brain.notifications.engine import NotificationEngine
        
        engine = NotificationEngine(db=importer.db)
        engine.create_notification(
            type="system",
            title="Import Complete",
            message=f"Successfully imported {records_imported} records",
            priority="medium"
        )
    except Exception:
        pass  # Notifications might not be available