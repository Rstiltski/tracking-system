"""
Data Export Serializers

Python implementations for serializing data to different formats.
Uses Python standard library: json, csv, sqlite3, zipfile

All implementation is in Python 3.10+
"""

import json
import csv
import sqlite3
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from abc import ABC, abstractmethod
import logging


logger = logging.getLogger(__name__)


class BaseSerializer(ABC):
    """
    Abstract base class for serializers.
    
    All serializers implement the same interface for
    consistent export behavior across formats.
    """
    
    @abstractmethod
    def serialize(
        self,
        data: Dict[str, List[Dict[str, Any]]],
        output_path: Path
    ) -> int:
        """
        Serialize data to the target format.
        
        Args:
            data: Dictionary mapping table names to row lists
            output_path: Path to write output
            
        Returns:
            Total number of records serialized
        """
        pass
    
    @abstractmethod
    def get_file_extension(self) -> str:
        """Get file extension for this format."""
        pass


class JSONSerializer(BaseSerializer):
    """
    Serialize data to JSON format.
    
    Uses Python's json module from the standard library.
    Creates a structured JSON file with metadata and data sections.
    
    Example:
        >>> serializer = JSONSerializer()
        >>> count = serializer.serialize(data, Path('export.json'))
    """
    
    def __init__(self, indent: int = 2):
        """
        Initialize JSON serializer.
        
        Args:
            indent: Number of spaces for indentation (default: 2)
        """
        self.indent = indent
    
    def serialize(
        self,
        data: Dict[str, List[Dict[str, Any]]],
        output_path: Path
    ) -> int:
        """
        Serialize data to JSON format.
        
        Creates a structured export with:
        - Metadata (export timestamp, version)
        - Data sections by table
        
        Args:
            data: Dictionary mapping table names to row lists
            output_path: Path to write JSON file
            
        Returns:
            Total number of records serialized
        """
        total_records = 0
        
        # Build export structure
        export_data = {
            'metadata': {
                'exported_at': datetime.now().isoformat(),
                'version': '1.0.0',
                'format': 'json',
                'tables': list(data.keys()),
            },
            'data': {}
        }
        
        # Process each table
        for table_name, rows in data.items():
            # Convert datetime objects to ISO strings
            processed_rows = []
            for row in rows:
                processed_row = {}
                for key, value in row.items():
                    if isinstance(value, datetime):
                        processed_row[key] = value.isoformat()
                    else:
                        processed_row[key] = value
                processed_rows.append(processed_row)
            
            export_data['data'][table_name] = processed_rows
            total_records += len(processed_rows)
        
        # Write to file
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=self.indent, default=str)
        
        logger.info(f"JSON export complete: {total_records} records to {output_path}")
        
        return total_records
    
    def get_file_extension(self) -> str:
        """Get file extension for JSON format."""
        return '.json'


class CSVSerializer(BaseSerializer):
    """
    Serialize data to CSV format.
    
    Uses Python's csv module from the standard library.
    Creates one CSV file per table in a directory.
    
    Example:
        >>> serializer = CSVSerializer()
        >>> count = serializer.serialize(data, Path('export_dir'))
    """
    
    def __init__(self, delimiter: str = ','):
        """
        Initialize CSV serializer.
        
        Args:
            delimiter: CSV field delimiter (default: comma)
        """
        self.delimiter = delimiter
    
    def serialize(
        self,
        data: Dict[str, List[Dict[str, Any]]],
        output_path: Path
    ) -> int:
        """
        Serialize data to CSV format.
        
        Creates a directory with one CSV file per table.
        
        Args:
            data: Dictionary mapping table names to row lists
            output_path: Directory path for CSV files
            
        Returns:
            Total number of records serialized
        """
        total_records = 0
        
        # Create output directory
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Create manifest file
        manifest = {
            'exported_at': datetime.now().isoformat(),
            'version': '1.0.0',
            'format': 'csv',
            'tables': {},
        }
        
        # Process each table
        for table_name, rows in data.items():
            if not rows:
                continue
            
            # Create CSV file for this table
            csv_path = output_path / f"{table_name}.csv"
            
            # Get column names from first row
            fieldnames = list(rows[0].keys())
            
            with open(csv_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=self.delimiter)
                writer.writeheader()
                
                for row in rows:
                    # Convert all values to strings
                    processed_row = {}
                    for key, value in row.items():
                        if isinstance(value, datetime):
                            processed_row[key] = value.isoformat()
                        elif value is None:
                            processed_row[key] = ''
                        else:
                            processed_row[key] = str(value)
                    writer.writerow(processed_row)
            
            total_records += len(rows)
            manifest['tables'][table_name] = {
                'file': f"{table_name}.csv",
                'records': len(rows),
                'columns': fieldnames,
            }
        
        # Write manifest
        manifest_path = output_path / 'manifest.json'
        with open(manifest_path, 'w', encoding='utf-8') as f:
            json.dump(manifest, f, indent=2)
        
        logger.info(f"CSV export complete: {total_records} records to {output_path}")
        
        return total_records
    
    def get_file_extension(self) -> str:
        """Get file extension for CSV format (returns directory)."""
        return ''  # CSV creates a directory


class SQLiteSerializer(BaseSerializer):
    """
    Serialize data to SQLite database format.
    
    Uses Python's sqlite3 module from the standard library.
    Creates a SQLite database with the same schema as the source.
    
    Example:
        >>> serializer = SQLiteSerializer()
        >>> count = serializer.serialize(data, Path('export.db'))
    """
    
    def serialize(
        self,
        data: Dict[str, List[Dict[str, Any]]],
        output_path: Path
    ) -> int:
        """
        Serialize data to SQLite format.
        
        Creates a SQLite database with all exported tables.
        
        Args:
            data: Dictionary mapping table names to row lists
            output_path: Path for SQLite database file
            
        Returns:
            Total number of records serialized
        """
        total_records = 0
        
        # Remove existing file if present
        if output_path.exists():
            output_path.unlink()
        
        # Create new database
        conn = sqlite3.connect(str(output_path))
        cursor = conn.cursor()
        
        # Create metadata table
        cursor.execute('''
            CREATE TABLE export_metadata (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        ''')
        
        cursor.execute("INSERT INTO export_metadata VALUES (?, ?)", ('exported_at', datetime.now().isoformat()))
        cursor.execute("INSERT INTO export_metadata VALUES (?, ?)", ('version', '1.0.0'))
        cursor.execute("INSERT INTO export_metadata VALUES (?, ?)", ('format', 'sqlite'))
        
        # Process each table
        for table_name, rows in data.items():
            if not rows:
                continue
            
            # Get column names and infer types
            columns = list(rows[0].keys())
            column_defs = []
            
            for col in columns:
                # Infer type from first row
                sample_value = rows[0].get(col)
                if isinstance(sample_value, int):
                    col_type = 'INTEGER'
                elif isinstance(sample_value, float):
                    col_type = 'REAL'
                elif isinstance(sample_value, bool):
                    col_type = 'INTEGER'  # SQLite uses 0/1 for boolean
                else:
                    col_type = 'TEXT'
                column_defs.append(f"{col} {col_type}")
            
            # Create table
            create_sql = f"CREATE TABLE {table_name} ({', '.join(column_defs)})"
            cursor.execute(create_sql)
            
            # Insert rows
            placeholders = ', '.join(['?' for _ in columns])
            insert_sql = f"INSERT INTO {table_name} VALUES ({placeholders})"
            
            for row in rows:
                values = []
                for col in columns:
                    value = row.get(col)
                    if isinstance(value, datetime):
                        value = value.isoformat()
                    elif isinstance(value, bool):
                        value = 1 if value else 0
                    values.append(value)
                cursor.execute(insert_sql, values)
            
            total_records += len(rows)
        
        conn.commit()
        conn.close()
        
        logger.info(f"SQLite export complete: {total_records} records to {output_path}")
        
        return total_records
    
    def get_file_extension(self) -> str:
        """Get file extension for SQLite format."""
        return '.db'
    
    def copy_database(
        self,
        source_path: Path,
        output_path: Path
    ) -> int:
        """
        Copy entire SQLite database.
        
        For full database exports, this is more efficient than
        reading and re-writing all data.
        
        Args:
            source_path: Path to source database
            output_path: Path for copied database
            
        Returns:
            Number of tables copied
        """
        # Remove existing file if present
        if output_path.exists():
            output_path.unlink()
        
        # Copy file
        shutil.copy2(source_path, output_path)
        
        # Count tables
        conn = sqlite3.connect(str(output_path))
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table'")
        table_count = cursor.fetchone()[0]
        conn.close()
        
        logger.info(f"SQLite database copied: {table_count} tables to {output_path}")
        
        return table_count


def get_serializer(format: str) -> BaseSerializer:
    """
    Get appropriate serializer for format.
    
    Args:
        format: Format name ('json', 'csv', 'sqlite')
        
    Returns:
        Serializer instance
        
    Raises:
        ValueError: If format is not supported
    """
    serializers = {
        'json': JSONSerializer,
        'csv': CSVSerializer,
        'sqlite': SQLiteSerializer,
    }
    
    serializer_class = serializers.get(format.lower())
    if serializer_class is None:
        raise ValueError(f"Unsupported format: {format}")
    
    return serializer_class()