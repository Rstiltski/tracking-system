"""
Skills Integration Module

This module provides integration with skills installed in ~/.gemini/antigravity/skills
It allows loading, searching, and using skills within the tracking system.

Usage:
    from skills import SkillsManager
    
    manager = SkillsManager()
    skills = manager.list_skills()
    skill = manager.get_skill("skill-creator")
    content = manager.get_skill_content("skill-creator", "SKILL.md")
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field


# Default skills directories
DEFAULT_SKILLS_DIR = Path.home() / ".gemini" / "antigravity" / "skills"
LOCAL_SKILLS_DIR = Path(__file__).parent.parent / ".agent" / "skill" / "source"


@dataclass
class Skill:
    """Represents a skill from the skills directory"""
    name: str
    path: Path
    description: str = ""
    has_skill_md: bool = False
    has_readme: bool = False
    has_scripts: bool = False
    has_references: bool = False
    
    def __post_init__(self):
        # Check what files exist
        self.has_skill_md = (self.path / "SKILL.md").exists()
        self.has_readme = (self.path / "README.md").exists()
        self.has_scripts = (self.path / "scripts").exists() and any((self.path / "scripts").iterdir())
        self.has_references = (self.path / "references").exists() and any((self.path / "references").iterdir())


@dataclass
class SkillsManager:
    """
    Manager for loading and interacting with skills from ~/.gemini/antigravity/skills
    or from the local .agent/skill/source directory
    """
    skills_dir: Path = field(default_factory=lambda: DEFAULT_SKILLS_DIR)
    _skills_cache: Dict[str, Skill] = field(default_factory=dict)
    _loaded: bool = field(default=False)
    
    def __post_init__(self):
        """Validate skills directory exists - check both default and local locations"""
        # Check default location first
        if self.skills_dir.exists():
            return
        
        # Check local .agent/skill/source location
        if LOCAL_SKILLS_DIR.exists():
            self.skills_dir = LOCAL_SKILLS_DIR
            return
        
        # Neither exists
        raise FileNotFoundError(
            f"Skills directory not found. Checked:\n"
            f"  - {DEFAULT_SKILLS_DIR}\n"
            f"  - {LOCAL_SKILLS_DIR}\n"
            f"Please install skills first: test -d ~/.gemini/antigravity/skills"
        )
    
    def load_skills(self, force: bool = False) -> Dict[str, Skill]:
        """
        Load all skills from the skills directory
        
        Args:
            force: Force reload even if already loaded
            
        Returns:
            Dictionary of skill_name -> Skill
        """
        if self._loaded and not force:
            return self._skills_cache
        
        self._skills_cache.clear()
        
        if not self.skills_dir.exists():
            return self._skills_cache
        
        for item in self.skills_dir.iterdir():
            if item.is_dir() and not item.name.startswith('.'):
                skill = Skill(
                    name=item.name,
                    path=item,
                    description=self._extract_description(item)
                )
                self._skills_cache[item.name] = skill
        
        self._loaded = True
        return self._skills_cache
    
    def _extract_description(self, skill_path: Path) -> str:
        """Extract description from SKILL.md or README.md"""
        # Try SKILL.md first
        skill_md = skill_path / "SKILL.md"
        if skill_md.exists():
            try:
                content = skill_md.read_text(encoding='utf-8', errors='ignore')
                # Extract first few lines as description
                lines = [l.strip() for l in content.split('\n') if l.strip()]
                if lines:
                    # Skip the first line if it's a title
                    if lines[0].startswith('#'):
                        return lines[1] if len(lines) > 1 else ""
                    return lines[0][:100]  # First 100 chars
            except Exception:
                pass
        
        # Try README.md
        readme = skill_path / "README.md"
        if readme.exists():
            try:
                content = readme.read_text(encoding='utf-8', errors='ignore')
                lines = [l.strip() for l in content.split('\n') if l.strip()]
                if lines:
                    if lines[0].startswith('#'):
                        return lines[1] if len(lines) > 1 else ""
                    return lines[0][:100]
            except Exception:
                pass
        
        return ""
    
    def list_skills(self) -> List[str]:
        """Get list of all skill names"""
        if not self._loaded:
            self.load_skills()
        return sorted(self._skills_cache.keys())
    
    def get_skill(self, name: str) -> Optional[Skill]:
        """Get a specific skill by name"""
        if not self._loaded:
            self.load_skills()
        return self._skills_cache.get(name)
    
    def get_skill_content(self, name: str, file: str = "SKILL.md") -> Optional[str]:
        """
        Get content of a specific file from a skill
        
        Args:
            name: Skill name
            file: File name to read (default: SKILL.md)
            
        Returns:
            File content or None if not found
        """
        skill = self.get_skill(name)
        if not skill:
            return None
        
        file_path = skill.path / file
        if file_path.exists():
            try:
                return file_path.read_text(encoding='utf-8', errors='ignore')
            except Exception:
                return None
        return None
    
    def search_skills(self, query: str) -> List[Skill]:
        """
        Search skills by name or description
        
        Args:
            query: Search query (case-insensitive)
            
        Returns:
            List of matching skills
        """
        if not self._loaded:
            self.load_skills()
        
        query_lower = query.lower()
        results = []
        
        for name, skill in self._skills_cache.items():
            if query_lower in name.lower():
                results.append(skill)
            elif query_lower in skill.description.lower():
                results.append(skill)
        
        return results
    
    def get_skills_by_category(self, category_prefix: str) -> List[Skill]:
        """
        Get skills that start with a specific category prefix
        
        Args:
            category_prefix: Category prefix (e.g., "python-", "web-")
            
        Returns:
            List of matching skills
        """
        if not self._loaded:
            self.load_skills()
        
        return [
            skill for name, skill in self._skills_cache.items()
            if name.startswith(category_prefix)
        ]
    
    def get_all_categories(self) -> List[str]:
        """
        Get all unique category prefixes from skill names
        
        Returns:
            List of unique categories
        """
        if not self._loaded:
            self.load_skills()
        
        categories = set()
        for name in self._skills_cache.keys():
            # Extract category from skill name (first part before -)
            if '-' in name:
                category = name.split('-')[0]
                categories.add(category)
        
        return sorted(categories)
    
    def get_skill_files(self, name: str) -> Dict[str, Path]:
        """
        Get all files in a skill directory
        
        Args:
            name: Skill name
            
        Returns:
            Dictionary of file_type -> file_path
        """
        skill = self.get_skill(name)
        if not skill:
            return {}
        
        files = {}
        for item in skill.path.rglob('*'):
            if item.is_file():
                rel_path = item.relative_to(skill.path)
                file_type = str(rel_path).replace('/', '.').replace('\\', '.')
                files[file_type] = item
        
        return files
    
    def reload(self):
        """Force reload skills from disk"""
        self._loaded = False
        self._skills_cache.clear()
        self.load_skills()


# Convenience functions
def get_skills_manager() -> SkillsManager:
    """Get a singleton SkillsManager instance"""
    global _skills_manager
    if _skills_manager is None:
        _skills_manager = SkillsManager()
    return _skills_manager


def list_all_skills() -> List[str]:
    """List all available skills"""
    return get_skills_manager().list_skills()


def search_skills(query: str) -> List[Skill]:
    """Search skills by query"""
    return get_skills_manager().search_skills(query)


def get_skill(name: str) -> Optional[Skill]:
    """Get a specific skill"""
    return get_skills_manager().get_skill(name)


# Global instance
_skills_manager: Optional[SkillsManager] = None
