"""
Reference Index for AI Assistant

Implements reference-by-substitution pattern for managing large code blocks.
Instead of loading full file contents into active memory, stores lightweight
references with metadata and loads content on-demand.

Based on AI agent research (2024-2025):
- Reference-by-substitution for large items
- Lazy loading of code content
- Metadata indexing for quick lookup

Usage:
    from brain.ai_assistant.reference_index import ReferenceIndex
    
    index = ReferenceIndex()
    
    # Create reference (stores metadata, not full content)
    ref_id = index.create_reference(
        file_path="brain/core/brain.py",
        description="Main brain entry point"
    )
    
    # Load full content only when needed
    content = index.load_reference(ref_id)
"""

import hashlib
import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field, asdict
from pathlib import Path


@dataclass
class FileReference:
    """Lightweight reference to a code file."""
    ref_id: str
    file_path: str
    description: str
    line_count: int = 0
    size_bytes: int = 0
    last_modified: Optional[datetime] = None
    tags: List[str] = field(default_factory=list)
    checksum: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    access_count: int = 0


@dataclass
class CodeBlockReference:
    """Reference to a specific code block within a file."""
    ref_id: str
    file_path: str
    start_line: int
    end_line: int
    description: str
    function_name: Optional[str] = None
    class_name: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    checksum: Optional[str] = None


class ReferenceIndex:
    """
    Manages lightweight references to code files and blocks.
    
    Features:
    - Creates unique IDs for files/blocks
    - Stores metadata without loading full content
    - Lazy loading when full content needed
    - Tag-based search and filtering
    """
    
    def __init__(self, index_file: Optional[str] = None,
                 base_path: Optional[str] = None):
        """
        Initialize reference index.
        
        Args:
            index_file: Path to store index (default: ai_assistant/reference_index.json)
            base_path: Base path for resolving relative file paths
        """
        if base_path is None:
            base_path = Path(__file__).parent.parent.parent
        self.base_path = Path(base_path)
        
        if index_file is None:
            index_file = str(Path(__file__).parent / "reference_index.json")
        self.index_file = index_file
        
        # In-memory index
        self._file_references: Dict[str, FileReference] = {}
        self._block_references: Dict[str, CodeBlockReference] = {}
        self._tag_index: Dict[str, List[str]] = {}  # tag -> [ref_ids]
        
        # Load existing index
        self._load_index()
    
    def _load_index(self) -> None:
        """Load index from file."""
        try:
            if os.path.exists(self.index_file):
                with open(self.index_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Load file references
                for ref_data in data.get('file_references', []):
                    ref = FileReference(**ref_data)
                    self._file_references[ref.ref_id] = ref
                
                # Load block references
                for ref_data in data.get('block_references', []):
                    ref = CodeBlockReference(**ref_data)
                    self._block_references[ref.ref_id] = ref
                
                # Load tag index
                self._tag_index = data.get('tag_index', {})
                
        except Exception as e:
            print(f"Warning: Could not load reference index: {e}")
    
    def _save_index(self) -> None:
        """Save index to file."""
        try:
            data = {
                'file_references': [asdict(ref) for ref in self._file_references.values()],
                'block_references': [asdict(ref) for ref in self._block_references.values()],
                'tag_index': self._tag_index
            }
            
            with open(self.index_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, default=str)
                
        except Exception as e:
            print(f"Warning: Could not save reference index: {e}")
    
    def _generate_ref_id(self, file_path: str, **kwargs) -> str:
        """Generate unique reference ID."""
        content = f"{file_path}{kwargs}{datetime.now().isoformat()}"
        return f"ref_{hashlib.md5(content.encode()).hexdigest()[:12]}"
    
    def _calculate_checksum(self, file_path: str) -> Optional[str]:
        """Calculate file checksum for change detection."""
        try:
            full_path = self.base_path / file_path
            if not full_path.exists():
                return None
            
            with open(full_path, 'rb') as f:
                return hashlib.md5(f.read()).hexdigest()
        except:
            return None
    
    def create_reference(self, file_path: str, description: str,
                        tags: Optional[List[str]] = None,
                        metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Create a lightweight reference to a file.
        
        Args:
            file_path: Path to the file (relative to base_path)
            description: Brief description of the file
            tags: Optional tags for categorization
            metadata: Optional additional metadata
            
        Returns:
            Reference ID (lightweight, can be stored in active memory)
        """
        full_path = self.base_path / file_path
        
        # Get file metadata without loading content
        line_count = 0
        size_bytes = 0
        last_modified = None
        
        if full_path.exists():
            try:
                size_bytes = full_path.stat().st_size
                last_modified = datetime.fromtimestamp(full_path.stat().st_mtime)
                
                with open(full_path, 'r', encoding='utf-8') as f:
                    line_count = sum(1 for _ in f)
            except:
                pass
        
        # Generate reference
        ref_id = self._generate_ref_id(file_path, description=description)
        checksum = self._calculate_checksum(file_path)
        
        reference = FileReference(
            ref_id=ref_id,
            file_path=str(file_path),
            description=description,
            line_count=line_count,
            size_bytes=size_bytes,
            last_modified=last_modified,
            tags=tags or [],
            checksum=checksum,
            metadata=metadata or {}
        )
        
        # Store reference
        self._file_references[ref_id] = reference
        
        # Update tag index
        for tag in reference.tags:
            if tag not in self._tag_index:
                self._tag_index[tag] = []
            self._tag_index[tag].append(ref_id)
        
        # Persist index
        self._save_index()
        
        return ref_id
    
    def create_block_reference(self, file_path: str, start_line: int, end_line: int,
                               description: str, tags: Optional[List[str]] = None,
                               function_name: Optional[str] = None,
                               class_name: Optional[str] = None) -> str:
        """
        Create a reference to a specific code block within a file.
        
        Args:
            file_path: Path to the file
            start_line: Starting line number (1-indexed)
            end_line: Ending line number (inclusive)
            description: Description of the code block
            tags: Optional tags
            function_name: Optional function name
            class_name: Optional class name
            
        Returns:
            Reference ID
        """
        ref_id = self._generate_ref_id(file_path, start=start_line, end=end_line)
        checksum = self._calculate_checksum(file_path)
        
        reference = CodeBlockReference(
            ref_id=ref_id,
            file_path=str(file_path),
            start_line=start_line,
            end_line=end_line,
            description=description,
            function_name=function_name,
            class_name=class_name,
            tags=tags or [],
            checksum=checksum
        )
        
        self._block_references[ref_id] = reference
        
        # Update tag index
        for tag in reference.tags:
            if tag not in self._tag_index:
                self._tag_index[tag] = []
            self._tag_index[tag].append(ref_id)
        
        self._save_index()
        
        return ref_id
    
    def load_reference(self, ref_id: str) -> Optional[str]:
        """
        Load full content for a reference (lazy loading).
        
        Args:
            ref_id: Reference ID
            
        Returns:
            Full file content or None if not found
        """
        # Check file references
        if ref_id in self._file_references:
            ref = self._file_references[ref_id]
            ref.access_count += 1
            
            try:
                full_path = self.base_path / ref.file_path
                with open(full_path, 'r', encoding='utf-8') as f:
                    return f.read()
            except Exception as e:
                print(f"Warning: Could not load file {ref.file_path}: {e}")
                return None
        
        # Check block references
        if ref_id in self._block_references:
            ref = self._block_references[ref_id]
            ref.access_count += 1  # Note: This won't persist without saving
            
            try:
                full_path = self.base_path / ref.file_path
                with open(full_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    block_lines = lines[ref.start_line-1:ref.end_line]
                    return ''.join(block_lines)
            except Exception as e:
                print(f"Warning: Could not load block from {ref.file_path}: {e}")
                return None
        
        return None
    
    def get_reference(self, ref_id: str) -> Optional[Dict[str, Any]]:
        """
        Get reference metadata without loading content.
        
        Args:
            ref_id: Reference ID
            
        Returns:
            Reference metadata dict or None
        """
        if ref_id in self._file_references:
            return asdict(self._file_references[ref_id])
        
        if ref_id in self._block_references:
            return asdict(self._block_references[ref_id])
        
        return None
    
    def find_references(self, tags: Optional[List[str]] = None,
                       search_text: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Find references by tags or search text.
        
        Args:
            tags: Filter by tags
            search_text: Search in descriptions
            
        Returns:
            List of reference metadata dicts
        """
        results = []
        
        # Filter by tags
        if tags:
            matching_refs = set()
            for tag in tags:
                if tag in self._tag_index:
                    matching_refs.update(self._tag_index[tag])
            
            for ref_id in matching_refs:
                ref = self.get_reference(ref_id)
                if ref:
                    results.append(ref)
        else:
            # No tag filter - return all
            all_refs = []
            for ref_id in list(self._file_references.keys()) + list(self._block_references.keys()):
                ref = self.get_reference(ref_id)
                if ref:
                    all_refs.append(ref)
            results = all_refs
        
        # Filter by search text
        if search_text:
            search_lower = search_text.lower()
            results = [
                ref for ref in results
                if search_lower in ref.get('description', '').lower()
            ]
        
        return results
    
    def check_for_changes(self, ref_id: str) -> bool:
        """
        Check if a file has changed since reference was created.
        
        Args:
            ref_id: Reference ID
            
        Returns:
            True if file has changed, False otherwise
        """
        ref = self.get_reference(ref_id)
        if not ref:
            return False
        
        current_checksum = self._calculate_checksum(ref['file_path'])
        return current_checksum != ref.get('checksum')
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get index statistics."""
        return {
            'total_file_references': len(self._file_references),
            'total_block_references': len(self._block_references),
            'total_tags': len(self._tag_index),
            'most_accessed': self._get_most_accessed(5)
        }
    
    def _get_most_accessed(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Get most frequently accessed references."""
        all_refs = list(self._file_references.values()) + list(self._block_references.values())
        sorted_refs = sorted(all_refs, key=lambda r: r.access_count, reverse=True)
        
        return [
            {'ref_id': ref.ref_id, 'description': ref.description, 'access_count': ref.access_count}
            for ref in sorted_refs[:limit]
        ]
    
    def clear_cache(self) -> None:
        """Clear in-memory index (useful for testing)."""
        self._file_references = {}
        self._block_references = {}
        self._tag_index = {}


# Convenience functions
def create_reference(file_path: str, description: str,
                    tags: Optional[List[str]] = None) -> str:
    """Quick reference creation."""
    index = ReferenceIndex()
    return index.create_reference(file_path, description, tags)


def load_reference(ref_id: str) -> Optional[str]:
    """Quick reference loading."""
    index = ReferenceIndex()
    return index.load_reference(ref_id)


def find_references(tags: Optional[List[str]] = None) -> List[Dict[str, Any]]:
    """Quick reference search."""
    index = ReferenceIndex()
    return index.find_references(tags)


__all__ = [
    "ReferenceIndex",
    "FileReference",
    "CodeBlockReference",
    "create_reference",
    "load_reference",
    "find_references",
]
