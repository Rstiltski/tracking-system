"""
Context Loader - Loads README.md files as AI Context

The ContextLoader is responsible for:
1. Finding all README.md files in the project
2. Loading their content as structured context
3. Providing easy access to project knowledge

This ensures AI always has the full picture when processing tasks.
"""
import os
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
import re


@dataclass
class ReadmeContext:
    """Represents a loaded README.md file"""
    path: str
    relative_path: str
    content: str
    sections: Dict[str, str] = field(default_factory=dict)
    title: str = ""
    
    def get_section(self, section_name: str) -> Optional[str]:
        """Get a specific section by name"""
        return self.sections.get(section_name.lower())
    
    def search(self, query: str) -> List[str]:
        """Search for text in the README"""
        results = []
        lines = self.content.split('\n')
        for i, line in enumerate(lines):
            if query.lower() in line.lower():
                # Get context around the match
                start = max(0, i - 2)
                end = min(len(lines), i + 3)
                context = '\n'.join(lines[start:end])
                results.append(context)
        return results


class ContextLoader:
    """
    Loads and manages README.md context files.
    
    The ContextLoader ensures that AI assistants always have access
    to the full project documentation when processing tasks.
    
    Usage:
        loader = ContextLoader()
        
        # Load all README files
        contexts = loader.load_all()
        
        # Get specific context
        brain_readme = loader.get("brain/README.md")
        
        # Search across all READMEs
        results = loader.search("habit")
    """
    
    # Priority order for README loading (most important first)
    PRIORITY_PATHS = [
        "README.md",  # Main project README
        "brain/README.md",  # Brain system docs
        "PROJECT_RULES.md",  # Project rules
        "brain/core/README.md",  # Core brain docs
        "brain/tools/README.md",  # Tools docs
        "brain/design/README.md",  # Design docs
    ]
    
    def __init__(self, project_root: Optional[str] = None):
        """
        Initialize the ContextLoader.
        
        Args:
            project_root: Root directory of the project (auto-detected if None)
        """
        if project_root is None:
            # Auto-detect project root
            current = Path(__file__).resolve()
            while current.parent != current:
                if (current / "README.md").exists():
                    self.project_root = str(current)
                    break
                current = current.parent
            else:
                self.project_root = os.getcwd()
        else:
            self.project_root = project_root
        
        self._cache: Dict[str, ReadmeContext] = {}
        self._loaded = False
    
    def find_all_readmes(self) -> List[str]:
        """
        Find all README.md files in the project.
        
        Returns:
            List of relative paths to README files
        """
        readmes = []
        project_path = Path(self.project_root)
        
        for path in project_path.rglob("README.md"):
            # Skip node_modules, .git, and other non-essential directories
            if any(part.startswith('.') or part in ['node_modules', '__pycache__', 'venv', 'env'] 
                   for part in path.parts):
                continue
            relative = str(path.relative_to(project_path))
            readmes.append(relative)
        
        # Sort by priority
        def priority_sort(path: str) -> int:
            try:
                return self.PRIORITY_PATHS.index(path)
            except ValueError:
                return len(self.PRIORITY_PATHS)
        
        readmes.sort(key=priority_sort)
        return readmes
    
    def load_readme(self, relative_path: str) -> Optional[ReadmeContext]:
        """
        Load a specific README.md file.
        
        Args:
            relative_path: Path relative to project root
            
        Returns:
            ReadmeContext or None if not found
        """
        if relative_path in self._cache:
            return self._cache[relative_path]
        
        full_path = Path(self.project_root) / relative_path
        
        if not full_path.exists():
            return None
        
        try:
            content = full_path.read_text(encoding='utf-8')
            
            # Parse sections
            sections = self._parse_sections(content)
            
            # Extract title
            title = self._extract_title(content)
            
            context = ReadmeContext(
                path=str(full_path),
                relative_path=relative_path,
                content=content,
                sections=sections,
                title=title
            )
            
            self._cache[relative_path] = context
            return context
            
        except Exception as e:
            print(f"Warning: Failed to load {relative_path}: {e}")
            return None
    
    def load_all(self, force_reload: bool = False) -> Dict[str, ReadmeContext]:
        """
        Load all README.md files in the project.
        
        Args:
            force_reload: Force reload even if cached
            
        Returns:
            Dictionary mapping relative paths to ReadmeContext
        """
        if self._loaded and not force_reload:
            return self._cache
        
        readmes = self.find_all_readmes()
        
        for path in readmes:
            self.load_readme(path)
        
        self._loaded = True
        return self._cache
    
    def get(self, relative_path: str) -> Optional[ReadmeContext]:
        """
        Get a specific README context.
        
        Args:
            relative_path: Path to the README file
            
        Returns:
            ReadmeContext or None
        """
        if not self._loaded:
            self.load_all()
        return self._cache.get(relative_path)
    
    def get_main_readme(self) -> Optional[ReadmeContext]:
        """Get the main project README"""
        return self.get("README.md")
    
    def get_brain_readme(self) -> Optional[ReadmeContext]:
        """Get the brain system README"""
        return self.get("brain/README.md")
    
    def get_rules(self) -> Optional[ReadmeContext]:
        """Get the project rules"""
        return self.get("PROJECT_RULES.md")
    
    def search(self, query: str) -> Dict[str, List[str]]:
        """
        Search across all loaded READMEs.
        
        Args:
            query: Search query
            
        Returns:
            Dictionary mapping file paths to search results
        """
        if not self._loaded:
            self.load_all()
        
        results = {}
        for path, context in self._cache.items():
            matches = context.search(query)
            if matches:
                results[path] = matches
        
        return results
    
    def get_context_summary(self) -> str:
        """
        Get a summary of all loaded context.
        
        Returns:
            Human-readable summary of available context
        """
        if not self._loaded:
            self.load_all()
        
        summary_lines = [
            "# Project Context Summary",
            f"Project Root: {self.project_root}",
            f"Loaded {len(self._cache)} README files:",
            ""
        ]
        
        for path, context in self._cache.items():
            summary_lines.append(f"## {path}")
            if context.title:
                summary_lines.append(f"Title: {context.title}")
            summary_lines.append(f"Sections: {', '.join(context.sections.keys())}")
            summary_lines.append("")
        
        return '\n'.join(summary_lines)
    
    def get_full_context(self) -> str:
        """
        Get the full context for AI processing.
        
        This combines all README content into a single string
        that can be used as context for AI assistants.
        
        Returns:
            Combined context string
        """
        if not self._loaded:
            self.load_all()
        
        parts = [
            "=" * 60,
            "PROJECT CONTEXT - LOADED FROM README FILES",
            "=" * 60,
            ""
        ]
        
        for path in self.PRIORITY_PATHS:
            if path in self._cache:
                context = self._cache[path]
                parts.append(f"\n{'=' * 60}")
                parts.append(f"FILE: {path}")
                parts.append("=" * 60)
                parts.append(context.content)
        
        # Add other READMEs not in priority list
        for path, context in self._cache.items():
            if path not in self.PRIORITY_PATHS:
                parts.append(f"\n{'=' * 60}")
                parts.append(f"FILE: {path}")
                parts.append("=" * 60)
                parts.append(context.content)
        
        return '\n'.join(parts)
    
    def _parse_sections(self, content: str) -> Dict[str, str]:
        """
        Parse markdown sections from content.
        
        Args:
            content: Markdown content
            
        Returns:
            Dictionary mapping section names to content
        """
        sections = {}
        current_section = "intro"
        current_content = []
        
        for line in content.split('\n'):
            # Check for headers (## or ###)
            header_match = re.match(r'^#{1,3}\s+(.+)$', line)
            if header_match:
                # Save previous section
                if current_content:
                    sections[current_section] = '\n'.join(current_content).strip()
                current_section = header_match.group(1).lower().strip()
                current_content = []
            else:
                current_content.append(line)
        
        # Save last section
        if current_content:
            sections[current_section] = '\n'.join(current_content).strip()
        
        return sections
    
    def _extract_title(self, content: str) -> str:
        """Extract the title from a README file"""
        for line in content.split('\n'):
            if line.startswith('# '):
                return line[2:].strip()
        return ""


# Global instance for convenience
_loader_instance: Optional[ContextLoader] = None


def get_context_loader() -> ContextLoader:
    """Get the global ContextLoader instance"""
    global _loader_instance
    if _loader_instance is None:
        _loader_instance = ContextLoader()
    return _loader_instance


def load_context() -> Dict[str, ReadmeContext]:
    """Convenience function to load all context"""
    return get_context_loader().load_all()


def get_full_context() -> str:
    """Convenience function to get full context string"""
    return get_context_loader().get_full_context()