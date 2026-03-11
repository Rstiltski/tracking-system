"""
Memory Manager for AI Assistant

Implements memory compression, relevance scoring, and intent-driven retrieval
for the AI assistant working on the Veryfyn Tracking System.

Based on AI agent research (2024-2025):
- Memory compression and forgetting strategies
- Sliding window for recent interactions
- Relevance scoring for retrieval
- Intent-driven memory selection

Usage:
    from brain.ai_assistant.memory_manager import MemoryManager
    
    memory = MemoryManager()
    relevant = memory.get_relevant_decisions(intent="Adding new feature")
"""

import json
import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, field, asdict
from pathlib import Path


@dataclass
class DecisionEntry:
    """A single decision from the decision log."""
    id: str
    timestamp: datetime
    summary: str
    choice: str
    reasoning: str
    implication: str
    relevance_score: float = 1.0
    decay_factor: float = 1.0


@dataclass
class MemorySummary:
    """Compressed summary of recent activity."""
    period: str  # "last_hour", "last_24h", "last_week"
    key_decisions: List[str]
    active_tasks: List[str]
    patterns_identified: List[str]
    timestamp: datetime = field(default_factory=datetime.now)


class MemoryManager:
    """
    Manages memory compression and retrieval for AI assistant.
    
    Features:
    - Sliding window for recent interactions
    - Summarization of older entries
    - Relevance scoring based on intent
    - Timestamp decay for stale data
    """
    
    def __init__(self, decisions_log_path: Optional[str] = None,
                 session_state_path: Optional[str] = None):
        """
        Initialize memory manager.
        
        Args:
            decisions_log_path: Path to decisions.log file
            session_state_path: Path to session.json file
        """
        # Default paths relative to project root
        base_path = Path(__file__).parent.parent.parent
        self.decisions_log_path = decisions_log_path or str(base_path / "decisions.log")
        self.session_state_path = session_state_path or str(base_path / "session.json")
        
        # Sliding window parameters
        self.active_window_size = 10  # Keep last 10 interactions active
        self.summary_window_size = 50  # Summarize interactions 11-50
        
        # Decay parameters
        self.decay_half_life = timedelta(hours=24)  # 24 hours half-life
        
        # Cache for loaded decisions
        self._decisions_cache: List[DecisionEntry] = []
        self._cache_timestamp: Optional[datetime] = None
        
    def load_decisions(self, force_reload: bool = False) -> List[DecisionEntry]:
        """
        Load decisions from log file.
        
        Args:
            force_reload: Force reload even if cache exists
            
        Returns:
            List of decision entries
        """
        # Check cache validity (5 minutes)
        if (self._decisions_cache and 
            self._cache_timestamp and 
            datetime.now() - self._cache_timestamp < timedelta(minutes=5) and
            not force_reload):
            return self._decisions_cache
        
        decisions = []
        
        try:
            with open(self.decisions_log_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Parse decision entries (simplified parsing)
            # In production, would use more robust parsing
            current_decision = {}
            for line in content.split('\n'):
                line = line.strip()
                
                if line.startswith('## '):
                    # New decision section
                    if current_decision:
                        decisions.append(self._parse_decision(current_decision))
                    current_decision = {'title': line[3:]}
                    
                elif line.startswith('**Date:**'):
                    current_decision['date'] = line[9:]
                elif line.startswith('**Status:**'):
                    current_decision['status'] = line[11:]
                elif line.startswith('### Summary'):
                    current_decision['summary'] = line[11:]
                elif 'Details:' in line:
                    current_decision['details'] = line[9:]
                    
            # Add last decision
            if current_decision:
                decisions.append(self._parse_decision(current_decision))
                
        except FileNotFoundError:
            # No decisions log yet
            pass
        except Exception as e:
            print(f"Warning: Could not load decisions log: {e}")
            
        self._decisions_cache = decisions
        self._cache_timestamp = datetime.now()
        
        return decisions
    
    def _parse_decision(self, raw: Dict[str, str]) -> DecisionEntry:
        """Parse raw decision dict into DecisionEntry."""
        # Parse timestamp
        timestamp = datetime.now()
        if 'date' in raw:
            try:
                # Try to parse date string
                timestamp = datetime.fromisoformat(raw['date'].replace('Z', '+00:00'))
            except:
                pass
        
        # Extract choice, reasoning, implication from details
        choice = raw.get('details', '').split('->')[0] if '->' in raw.get('details', '') else raw.get('summary', '')
        reasoning = raw.get('details', '').split('->')[1] if '->' in raw.get('details', '') and len(raw.get('details', '').split('->')) > 1 else ''
        implication = raw.get('details', '').split('->')[2] if '->' in raw.get('details', '') and len(raw.get('details', '').split('->')) > 2 else ''
        
        return DecisionEntry(
            id=raw.get('title', 'unknown'),
            timestamp=timestamp,
            summary=raw.get('summary', ''),
            choice=choice,
            reasoning=reasoning,
            implication=implication,
            relevance_score=1.0,
            decay_factor=1.0
        )
    
    def get_relevant_decisions(self, intent: str, max_results: int = 5) -> List[DecisionEntry]:
        """
        Get decisions relevant to current intent.
        
        Args:
            intent: Current task intent (e.g., "Adding new brain component")
            max_results: Maximum number of decisions to return
            
        Returns:
            List of relevant decisions, sorted by relevance score
        """
        decisions = self.load_decisions()
        
        # Calculate relevance scores
        scored_decisions = []
        for decision in decisions:
            score = self._calculate_relevance(decision, intent)
            if score > 0.3:  # Threshold for relevance
                decision.relevance_score = score
                scored_decisions.append(decision)
        
        # Sort by relevance score (descending)
        scored_decisions.sort(key=lambda d: d.relevance_score, reverse=True)
        
        return scored_decisions[:max_results]
    
    def _calculate_relevance(self, decision: DecisionEntry, intent: str) -> float:
        """
        Calculate relevance score for a decision given current intent.
        
        Scoring factors:
        - Keyword match (40%)
        - Intent match (30%)
        - Recency (20%)
        - Decision impact (10%)
        
        Args:
            decision: Decision entry to score
            intent: Current intent string
            
        Returns:
            Relevance score (0.0 to 1.0)
        """
        # Keyword match (40%)
        keywords = set(intent.lower().split())
        decision_text = f"{decision.summary} {decision.choice} {decision.reasoning}".lower()
        keyword_matches = sum(1 for kw in keywords if kw in decision_text)
        keyword_score = (keyword_matches / len(keywords)) * 0.4 if keywords else 0
        
        # Intent match (30%) - simplified semantic match
        intent_patterns = {
            'adding': ['add', 'create', 'new', 'implement'],
            'modifying': ['modify', 'update', 'change', 'edit'],
            'fixing': ['fix', 'bug', 'error', 'issue'],
            'analyzing': ['analyze', 'review', 'examine', 'audit'],
            'planning': ['plan', 'roadmap', 'strategy', 'design']
        }
        
        intent_score = 0
        for pattern_type, pattern_words in intent_patterns.items():
            if pattern_type in intent.lower():
                if any(word in decision_text for word in pattern_words):
                    intent_score = 0.3
                    break
        
        # Recency (20%) - exponential decay
        age = datetime.now() - decision.timestamp
        decay_factor = 0.5 ** (age.total_seconds() / self.decay_half_life.total_seconds())
        recency_score = decay_factor * 0.2
        
        # Decision impact (10%) - based on status
        impact_score = 0.1
        if 'IMPLEMENTED' in decision.choice.upper() or 'COMPLETE' in decision.choice.upper():
            impact_score = 0.1
        elif 'PLANNED' in decision.choice.upper():
            impact_score = 0.05
        else:
            impact_score = 0.07
        
        return min(1.0, keyword_score + intent_score + recency_score + impact_score)
    
    def get_recent_summary(self, hours: int = 24) -> MemorySummary:
        """
        Get compressed summary of recent activity.
        
        Args:
            hours: Time window to summarize
            
        Returns:
            MemorySummary object
        """
        decisions = self.load_decisions()
        cutoff = datetime.now() - timedelta(hours=hours)
        
        recent_decisions = [d for d in decisions if d.timestamp > cutoff]
        
        # Extract key information
        key_decisions = [d.summary for d in recent_decisions[:5]]
        active_tasks = self._extract_active_tasks(recent_decisions)
        patterns = self._identify_patterns(recent_decisions)
        
        return MemorySummary(
            period=f"last_{hours}h",
            key_decisions=key_decisions,
            active_tasks=active_tasks,
            patterns_identified=patterns,
            timestamp=datetime.now()
        )
    
    def _extract_active_tasks(self, decisions: List[DecisionEntry]) -> List[str]:
        """Extract currently active tasks from recent decisions."""
        active = []
        for d in decisions:
            if 'IMPLEMENTED' in d.choice.upper() or 'COMPLETE' in d.status.upper() if hasattr(d, 'status') else False:
                continue
            if d.summary and len(d.summary) < 100:
                active.append(d.summary)
        return active[:5]
    
    def _identify_patterns(self, decisions: List[DecisionEntry]) -> List[str]:
        """Identify patterns in recent decisions."""
        patterns = []
        
        # Check for repeated themes
        themes = {}
        for d in decisions:
            theme = d.summary.split()[0] if d.summary else 'unknown'
            themes[theme] = themes.get(theme, 0) + 1
        
        # Extract frequent themes
        for theme, count in themes.items():
            if count >= 2:
                patterns.append(f"Repeated focus on {theme} ({count} times)")
        
        return patterns[:3]
    
    def log_decision(self, choice: str, reasoning: str, implication: str,
                     summary: Optional[str] = None) -> None:
        """
        Log a new decision to the decision log.
        
        Args:
            choice: What was decided
            reasoning: Why it was decided
            implication: What this means for future
            summary: Optional brief summary
        """
        timestamp = datetime.now().isoformat()
        decision_id = f"DECISION_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        entry = f"""
## {decision_id}: {summary or choice[:50]}

**Date:** {timestamp}
**Status:** IMPLEMENTED

### Summary
{summary or choice}

### Details
{choice} -> {reasoning} -> {implication}
"""
        
        try:
            with open(self.decisions_log_path, 'a', encoding='utf-8') as f:
                f.write(entry)
            
            # Invalidate cache
            self._cache_timestamp = None
            
        except Exception as e:
            print(f"Warning: Could not log decision: {e}")
    
    def compress_context(self, interactions: List[Dict[str, str]]) -> str:
        """
        Compress a list of interactions into a summary.
        
        Args:
            interactions: List of {role, content} dicts
            
        Returns:
            Compressed context string
        """
        if len(interactions) <= self.active_window_size:
            # Keep all interactions
            return self._format_interactions(interactions)
        
        # Keep recent, summarize older
        recent = interactions[-self.active_window_size:]
        older = interactions[:-self.active_window_size]
        
        older_summary = f"[{len(older)} earlier interactions summarized]"
        
        return f"{older_summary}\n\n" + self._format_interactions(recent)
    
    def _format_interactions(self, interactions: List[Dict[str, str]]) -> str:
        """Format interactions for display."""
        formatted = []
        for i, interaction in enumerate(interactions):
            role = interaction.get('role', 'unknown')
            content = interaction.get('content', '')[:200]  # Truncate long content
            formatted.append(f"{i+1}. {role}: {content}")
        return '\n'.join(formatted)
    
    def clear_cache(self) -> None:
        """Clear the decisions cache."""
        self._decisions_cache = []
        self._cache_timestamp = None


# Convenience functions
def get_memory_manager() -> MemoryManager:
    """Get a MemoryManager instance with default paths."""
    return MemoryManager()


def get_relevant_decisions(intent: str, max_results: int = 5) -> List[DecisionEntry]:
    """Quick access to relevant decisions."""
    memory = MemoryManager()
    return memory.get_relevant_decisions(intent, max_results)


def log_decision(choice: str, reasoning: str, implication: str,
                 summary: Optional[str] = None) -> None:
    """Quick decision logging."""
    memory = MemoryManager()
    memory.log_decision(choice, reasoning, implication, summary)


__all__ = [
    "MemoryManager",
    "DecisionEntry",
    "MemorySummary",
    "get_memory_manager",
    "get_relevant_decisions",
    "log_decision",
]
