"""
GitHub Cortex Client

Provides GitHub integration for the immune system to create branches and PRs
for harvest proposals.

This is a stub implementation. In production, this would integrate with the
GitHub API to create branches, commit files, and open pull requests.
"""

import logging
import os
from typing import Optional, Dict, Any, List

logger = logging.getLogger(__name__)


class GitHubCortexClient:
    """
    GitHub API client for immune system operations.
    
    This client handles:
    - Creating branches from default branch
    - Creating/updating files
    - Creating pull requests
    
    Requires GITHUB_TOKEN and GITHUB_REPOSITORY environment variables.
    """
    
    def __init__(self, token: Optional[str] = None, repository: Optional[str] = None):
        """
        Initialize the GitHub client.
        
        Args:
            token: GitHub personal access token. Defaults to GITHUB_TOKEN env var.
            repository: Repository in format 'owner/repo'. Defaults to GITHUB_REPOSITORY env var.
        """
        self.token = token or os.environ.get('GITHUB_TOKEN')
        self.repository = repository or os.environ.get('GITHUB_REPOSITORY')
        self.base_url = 'https://api.github.com'
        self._available = bool(self.token and self.repository)
        
        if not self._available:
            logger.debug('GitHubCortexClient: GITHUB_TOKEN or GITHUB_REPOSITORY not set')
    
    def is_available(self) -> bool:
        """Check if GitHub client is configured and available."""
        return self._available
    
    def get_default_branch(self) -> Optional[str]:
        """Get the default branch name for the repository."""
        if not self._available:
            return None
        # In a real implementation, this would call the GitHub API
        return 'main'
    
    def create_branch_from_default(self, branch_name: str, message: str = 'Create branch') -> bool:
        """
        Create a new branch from the default branch.
        
        Args:
            branch_name: Name of the new branch
            message: Commit message for the branch creation
            
        Returns:
            True if successful, False otherwise
        """
        if not self._available:
            logger.debug('GitHub not available, skipping branch creation')
            return False
        
        # In a real implementation, this would:
        # 1. Get the SHA of the default branch
        # 2. Create a new ref with that SHA
        logger.info('Would create branch: %s', branch_name)
        return True
    
    def create_or_update_file(self, path: str, content: str, branch: str, 
                              message: str) -> bool:
        """
        Create or update a file in the repository.
        
        Args:
            path: Path to the file
            content: File content
            branch: Branch to commit to
            message: Commit message
            
        Returns:
            True if successful, False otherwise
        """
        if not self._available:
            logger.debug('GitHub not available, skipping file creation')
            return False
        
        # In a real implementation, this would:
        # 1. Check if file exists (get SHA if it does)
        # 2. Create/update the file with the content
        logger.info('Would create/update file: %s on branch %s', path, branch)
        return True
    
    def create_pr(self, title: str, body: str, head: str, 
                  base: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Create a pull request.
        
        Args:
            title: PR title
            body: PR description
            head: Source branch
            base: Target branch (defaults to repository default)
            
        Returns:
            PR data dict if successful, None otherwise
        """
        if not self._available:
            logger.debug('GitHub not available, skipping PR creation')
            return None
        
        if base is None:
            base = self.get_default_branch()
        
        # In a real implementation, this would call the GitHub API
        logger.info('Would create PR: %s from %s to %s', title, head, base)
        
        # Return a mock PR object
        return {
            'number': 1,
            'title': title,
            'html_url': f'https://github.com/{self.repository}/pull/1'
        }


def build_emotional_pr_body(title: str, description: str, coring_score: float,
                           emotion: str, confidence: float, 
                           files: Dict[str, bool]) -> str:
    """
    Build an emotionally-aware PR description.
    
    Args:
        title: PR title
        description: Base description
        coring_score: Score indicating importance/impact
        emotion: Detected emotion (e.g., 'concerned', 'excited', 'neutral')
        confidence: Confidence in the analysis
        files: Dict of file paths to success status
        
    Returns:
        Formatted PR body string
    """
    # Emotion-based prefixes
    emotion_prefixes = {
        'concerned': '⚠️',
        'excited': '✨',
        'neutral': '📝',
        'confident': '✅',
        'cautious': '🤔'
    }
    
    prefix = emotion_prefixes.get(emotion, '📝')
    
    # Build file changes section
    files_section = ''
    if files:
        files_section = '\n\n### Files Changed\n'
        for path, success in files.items():
            status = '✅' if success else '❌'
            files_section += f'{status} `{path}`\n'
    
    # Build the body
    body = f"""{prefix} {title}

{description}

### Analysis
- **Coring Score**: {coring_score:.2f}
- **Emotion**: {emotion}
- **Confidence**: {confidence:.1%}
{files_section}
---
*This PR was generated automatically by the Immune System.*
"""
    
    return body
