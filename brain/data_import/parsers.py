"""
Data Import Parsers

Python parsers for JSON and CSV formats using Python standard library.
All implementation is in Python 3.10+

Uses:
- json module for JSON parsing
- csv module for CSV parsing
- sqlite3 module for SQLite import
"""

import json
import csv
import sqlite3
from pathlib import Path
from typing import Dict, List, Any, Optional, Iterator
from dataclasses import dataclass


@dataclass
class ParsedData:
    """Result of parsing an import file."""
    modules: Dict[str, List[Dict[str, Any]]]
    metadata: Dict[str, Any]
    warnings: List[str]


class JSONParser:
    """
    Parser for JSON export files.
    
    Uses Python's built-in json module for parsing.
    Expects JSON structure from DataExporter.
    """
    
    def __init__(self, file_path: str):
        """
        Initialize JSON parser.
        
        Args:
            file_path: Path to JSON file to parse
        """
        self.file_path = Path(file_path)
        self.data: Dict[str, Any] = {}
        self.warnings: List[str] = []
    
    def parse(self) -> ParsedData:
        """
        Parse JSON file and extract module data.
        
        Returns:
            ParsedData with modules and metadata
            
        Raises:
            FileNotFoundError: If file doesn't exist
            json.JSONDecodeError: If file is not valid JSON
        """
        if not self.file_path.exists():
            raise FileNotFoundError(f"Import file not found: {self.file_path}")
        
        # Read and parse JSON using Python's json module
        with open(self.file_path, 'r', encoding='utf-8') as f:
            self.data = json.load(f)
        
        # Extract modules
        modules = {}
        metadata = self.data.get('metadata', {})
        
        # Process each module in the export
        for module_name, records in self.data.items():
            if module_name == 'metadata':
                continue
            
            if not isinstance(records, list):
                self.warnings.append(f"Module '{module_name}' is not a list, skipping")
                continue
            
            modules[module_name] = records
        
        return ParsedData(
            modules=modules,
            metadata=metadata,
            warnings=self.warnings
        )
    
    def validate_structure(self) -> bool:
        """
        Validate JSON structure matches expected format.
        
        Returns:
            True if valid, False otherwise
        """
        if not self.data:
            return False
        
        # Should have at least one module or metadata
        has_modules = any(k != 'metadata' for k in self.data.keys())
        has_metadata = 'metadata' in self.data
        
        return has_modules or has_metadata


class CSVParser:
    """
    Parser for CSV export files.
    
    Uses Python's built-in csv module with DictReader for parsing.
    Expects one CSV file per module or a ZIP of CSVs.
    """
    
    def __init__(self, file_path: str, module_name: str = None):
        """
        Initialize CSV parser.
        
        Args:
            file_path: Path to CSV file or ZIP of CSVs
            module_name: If CSV is single module, name of that module
        """
        self.file_path = Path(file_path)
        self.module_name = module_name
        self.warnings: List[str] = []
    
    def parse(self) -> ParsedData:
        """
        Parse CSV file(s) and extract module data.
        
        Returns:
            ParsedData with modules and metadata
            
        Raises:
            FileNotFoundError: If file doesn't exist
        """
        if not self.file_path.exists():
            raise FileNotFoundError(f"Import file not found: {self.file_path}")
        
        modules = {}
        
        # If single CSV file
        if self.file_path.suffix == '.csv':
            module_name = self.module_name or self.file_path.stem
            modules[module_name] = self._parse_csv_file(self.file_path)
        
        # If ZIP of CSVs
        elif self.file_path.suffix == '.zip':
            modules = self._parse_csv_zip(self.file_path)
        
        return ParsedData(
            modules=modules,
            metadata={'source': str(self.file_path)},
            warnings=self.warnings
        )
    
    def _parse_csv_file(self, csv_path: Path) -> List[Dict[str, Any]]:
        """
        Parse a single CSV file using Python's csv.DictReader.
        
        Args:
            csv_path: Path to CSV file
            
        Returns:
            List of row dictionaries
        """
        records = []
        
        with open(csv_path, 'r', encoding='utf-8', newline='') as f:
            # Use csv.DictReader for automatic header parsing
            reader = csv.DictReader(f)
            
            for row in reader:
                # Convert empty strings to None
                cleaned_row = {
                    k: (None if v == '' else v)
                    for k, v in row.items()
                }
                records.append(cleaned_row)
        
        return records
    
    def _parse_csv_zip(self, zip_path: Path) -> Dict[str, List[Dict[str, Any]]]:
        """
        Parse ZIP file containing multiple CSVs.
        
        Args:
            zip_path: Path to ZIP file
            
        Returns:
            Dictionary mapping module names to records
        """
        import zipfile
        
        modules = {}
        
        with zipfile.ZipFile(zip_path, 'r') as zf:
            for filename in zf.namelist():
                if not filename.endswith('.csv'):
                    continue
                
                module_name = Path(filename).stem
                with zf.open(filename) as f:
                    # Decode bytes to string for csv module
                    text_file = (line.decode('utf-8') for line in f)
                    reader = csv.DictReader(text_file)
                    
                    modules[module_name] = [
                        {k: (None if v == '' else v) for k, v in row.items()}
                        for row in reader
                    ]
        
        return modules


class SQLiteImporter:
    """
    Direct SQLite database import.
    
    Uses Python's sqlite3 module to attach and copy data
    from an exported SQLite database.
    """
    
    def __init__(self, db_path: str, source_db_path: str):
        """
        Initialize SQLite importer.
        
        Args:
            db_path: Path to target database
            source_db_path: Path to source database (export)
        """
        self.db_path = db_path
        self.source_db_path = source_db_path
        self.warnings: List[str] = []
    
    def import_tables(self, tables: List[str] = None) -> Dict[str, int]:
        """
        Import tables from source database.
        
        Args:
            tables: List of table names to import (None = all)
            
        Returns:
            Dictionary mapping table names to row counts
        """
        import sqlite3
        
        # Connect to both databases using Python's sqlite3 module
        target_conn = sqlite3.connect(self.db_path)
        source_conn = sqlite3.connect(self.source_db_path)
        
        # Attach source database
        target_conn.execute(
            f"ATTACH DATABASE '{self.source_db_path}' AS source"
        )
        
        # Get list of tables to import
        if tables is None:
            tables = self._get_table_names(source_conn)
        
        results = {}
        
        # Import each table
        for table_name in tables:
            count = self._import_table(
                target_conn, source_conn, table_name
            )
            results[table_name] = count
        
        # Detach source database
        target_conn.execute("DETACH DATABASE source")
        target_conn.commit()
        
        target_conn.close()
        source_conn.close()
        
        return results
    
    def _get_table_names(self, conn: sqlite3.Connection) -> List[str]:
        """Get list of user tables from database."""
        cursor = conn.execute(
            """SELECT name FROM sqlite_master 
               WHERE type='table' AND name NOT LIKE 'sqlite_%'"""
        )
        return [row[0] for row in cursor.fetchall()]
    
    def _import_table(
        self,
        target_conn: sqlite3.Connection,
        source_conn: sqlite3.Connection,
        table_name: str
    ) -> int:
        """
        Import a single table using INSERT OR REPLACE.
        
        Args:
            target_conn: Target database connection
            source_conn: Source database connection
            table_name: Name of table to import
            
        Returns:
            Number of rows imported
        """
        # Get table schema from source
        cursor = source_conn.execute(
            f"SELECT sql FROM sqlite_master WHERE type='table' AND name=?",
            (table_name,)
        )
        schema = cursor.fetchone()
        
        if not schema:
            self.warnings.append(f"Table '{table_name}' not found in source")
            return 0
        
        # Create table if not exists in target
        target_conn.execute(schema[0])
        
        # Copy data using INSERT OR REPLACE
        target_conn.execute(f"""
            INSERT OR REPLACE INTO {table_name}
            SELECT * FROM source.{table_name}
        """)
        
        # Get row count
        cursor = target_conn.execute(f"SELECT COUNT(*) FROM {table_name}")
        count = cursor.fetchone()[0]
        
        return count
