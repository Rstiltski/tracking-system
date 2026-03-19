"""
Memory Manager for AI Assistant (Upgraded to RAISE Architecture)

Implements memory compression, relevance scoring, intent-driven retrieval,
and the RAISE (Reasoning and Acting through Integrated Storage and Execution) framework.

Features:
- Stateful Memory Segmentation: Short-Term (Session), Working (Scratchpad), Long-Term (Decisions).
- Sliding window for recent interactions.
- Relevance scoring based on intent and extracted entities.
- Timestamp decay for stale data.
- Reflexion storage for self-critique.

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
    """A single decision from the long-term decision log."""
    id: str
    timestamp: datetime
    summary: str
    choice: str
    reasoning: str
    implication: str
    extracted_entities: List[str] = field(default_factory=list)  # Added for RAISE
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
    Manages the RAISE architecture memory for the AI assistant.
    Segmentation:
    1. Short-Term: Session context (sliding window)
    2. Working Memory: The Scratchpad (cognitive buffer)
    3. Long-Term: The decisions log (persistent)
    """
    
    def __init__(self, decisions_log_path: Optional[str] = None,
                 session_state_path: Optional[str] = None,
                 scratchpad_path: Optional[str] = None):
        """
        Initialize memory manager.
        """
        # Default paths relative to project root
        base_path = Path(__file__).parent.parent.parent
        self.decisions_log_path = decisions_log_path or str(base_path / "decisions.log")
        self.session_state_path = session_state_path or str(base_path / "session.json")
        self.scratchpad_path = scratchpad_path or str(base_path / ".scratchpad.json")
        
        # Sliding window parameters
        self.active_window_size = 10
        self.summary_window_size = 50
        
        # Decay parameters
        self.decay_half_life = timedelta(hours=24)
        
        # Cache for loaded decisions
        self._decisions_cache: List[DecisionEntry] = []
        self._cache_timestamp: Optional[datetime] = None

    # --- WORKING MEMORY (SCRATCHPAD) ---

    def read_scratchpad(self) -> Dict[str, Any]:
        """Read the temporary cognitive buffer (scratchpad)."""
        try:
            if os.path.exists(self.scratchpad_path):
                with open(self.scratchpad_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception:
            pass
        return {"variables": {}, "partial_calculations": []}

    def write_scratchpad(self, key: str, value: Any) -> None:
        """Write intermediate state to the scratchpad."""
        data = self.read_scratchpad()
        data["variables"][key] = value
        data["last_updated"] = datetime.now().isoformat()
        try:
            with open(self.scratchpad_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not write to scratchpad: {e}")

    def clear_scratchpad(self) -> None:
        """Flush the cognitive buffer."""
        try:
            if os.path.exists(self.scratchpad_path):
                os.remove(self.scratchpad_path)
        except Exception:
            pass

    # --- REFLEXION (SELF-CRITIQUE) ---

    def store_reflection(self, reflection: Dict[str, str]) -> None:
        """Store linguistic critique of previous actions (Reflexion framework)."""
        reasoning = f"{reflection.get('what_worked', '')} | {reflection.get('what_to_improve', '')}"
        implication = f"Pattern learned: {reflection.get('pattern_learned', '')}"
        
        self.log_decision(
            choice="Self-Reflection generated",
            reasoning=reasoning,
            implication=implication,
            summary="Reflexion Checkpoint",
            entities=["reflexion", "self_critique", "learning"]
        )

    # --- LONG-TERM MEMORY (DECISIONS LOG) ---

    def load_decisions(self, force_reload: bool = False) -> List[DecisionEntry]:
        """Load decisions from log file."""
        if (self._decisions_cache and 
            self._cache_timestamp and 
            datetime.now() - self._cache_timestamp < timedelta(minutes=5) and
            not force_reload):
            return self._decisions_cache
        
        decisions = []
        try:
            with open(self.decisions_log_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            current_decision = {}
            for line in content.split('\n'):
                line = line.strip()
                
                if line.startswith('## '):
                    if current_decision:
                        decisions.append(self._parse_decision(current_decision))
                    current_decision = {'title': line[3:]}
                elif line.startswith('**Date:**'):
                    current_decision['date'] = line[9:]
                elif line.startswith('**Status:**'):
                    current_decision['status'] = line[11:]
                elif line.startswith('### Summary'):
                    current_decision['summary'] = line[11:]
                elif line.startswith('**Entities:**'):
                    current_decision['entities'] = line[13:]
                elif 'Details:' in line:
                    current_decision['details'] = line[9:]
                    
            if current_decision:
                decisions.append(self._parse_decision(current_decision))
                
        except FileNotFoundError:
            pass
        except Exception as e:
            print(f"Warning: Could not load decisions log: {e}")
            
        self._decisions_cache = decisions
        self._cache_timestamp = datetime.now()
        
        return decisions
    
    def _parse_decision(self, raw: Dict[str, str]) -> DecisionEntry:
        """Parse raw decision dict into DecisionEntry."""
        timestamp = datetime.now()
        if 'date' in raw:
            try:
                timestamp = datetime.fromisoformat(raw['date'].replace('Z', '+00:00'))
            except:
                pass
        
        details = raw.get('details', '')
        parts = details.split('->')
        choice = parts[0].strip() if len(parts) > 0 else raw.get('summary', '')
        reasoning = parts[1].strip() if len(parts) > 1 else ''
        implication = parts[2].strip() if len(parts) > 2 else ''
        
        entities = [e.strip() for e in raw.get('entities', '').split(',') if e.strip()]
        
        return DecisionEntry(
            id=raw.get('title', 'unknown'),
            timestamp=timestamp,
            summary=raw.get('summary', ''),
            choice=choice,
            reasoning=reasoning,
            implication=implication,
            extracted_entities=entities,
            relevance_score=1.0,
            decay_factor=1.0
        )
    
    def get_relevant_decisions(self, intent: str, entities: List[str] = None, max_results: int = 5) -> List[DecisionEntry]:
        """Get decisions relevant to current intent and entities (RAISE feature)."""
        decisions = self.load_decisions()
        scored_decisions = []
        for decision in decisions:
            score = self._calculate_relevance(decision, intent, entities or [])
            if score > 0.3:
                decision.relevance_score = score
                scored_decisions.append(decision)
        
        scored_decisions.sort(key=lambda d: d.relevance_score, reverse=True)
        return scored_decisions[:max_results]
    
    def _calculate_relevance(self, decision: DecisionEntry, intent: str, entities: List[str]) -> float:
        """Calculate relevance using Semantic Intent + Entity Recognition."""
        # Keyword match (30%)
        keywords = set(intent.lower().split())
        decision_text = f"{decision.summary} {decision.choice} {decision.reasoning}".lower()
        keyword_matches = sum(1 for kw in keywords if kw in decision_text)
        keyword_score = (keyword_matches / len(keywords)) * 0.3 if keywords else 0
        
        # Entity match (30%) - Crucial for RAISE
        entity_score = 0.0
        if entities and decision.extracted_entities:
            ent_matches = sum(1 for e in entities if e in decision.extracted_entities)
            entity_score = (ent_matches / len(entities)) * 0.3
            
        # Intent match (20%)
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
                    intent_score = 0.2
                    break
        
        # Recency (15%)
        age = datetime.now() - decision.timestamp
        decay_factor = 0.5 ** (age.total_seconds() / self.decay_half_life.total_seconds())
        recency_score = decay_factor * 0.15
        
        # Impact (5%)
        impact_score = 0.05
        if 'IMPLEMENTED' in decision.choice.upper() or 'COMPLETE' in decision.choice.upper():
            impact_score = 0.05
        elif 'PLANNED' in decision.choice.upper():
            impact_score = 0.02
        
        return min(1.0, keyword_score + entity_score + intent_score + recency_score + impact_score)
    
    def get_recent_summary(self, hours: int = 24) -> MemorySummary:
        """Get compressed summary of recent activity."""
        decisions = self.load_decisions()
        cutoff = datetime.now() - timedelta(hours=hours)
        recent_decisions = [d for d in decisions if d.timestamp > cutoff]
        
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
            if 'IMPLEMENTED' in d.choice.upper() or 'COMPLETE' in (getattr(d, 'status', '').upper()):
                continue
            if d.summary and len(d.summary) < 100:
                active.append(d.summary)
        return active[:5]
    
    def _identify_patterns(self, decisions: List[DecisionEntry]) -> List[str]:
        """Identify patterns in recent decisions."""
        patterns = []
        themes = {}
        for d in decisions:
            theme = d.summary.split()[0] if d.summary else 'unknown'
            themes[theme] = themes.get(theme, 0) + 1
        
        for theme, count in themes.items():
            if count >= 2:
                patterns.append(f"Repeated focus on {theme} ({count} times)")
        
        return patterns[:3]
    
    def log_decision(self, choice: str, reasoning: str, implication: str,
                     summary: Optional[str] = None, entities: List[str] = None) -> None:
        """Log a new decision to the decision log with Entity Extraction."""
        timestamp = datetime.now().isoformat()
        decision_id = f"DECISION_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        ent_str = f"\\n**Entities:** {','.join(entities)}" if entities else ""
        
        entry = [
            f"## {decision_id}: {summary or choice[:50]}",
            "",
            f"**Date:** {timestamp}",
            f"**Status:** IMPLEMENTED{ent_str}",
            "",
            "### Summary",
            f"{summary or choice}",
            "",
            "### Details",
            f"{choice} -> {reasoning} -> {implication}",
            ""
        ]
        
        try:
            with open(self.decisions_log_path, 'a', encoding='utf-8') as f:
                f.write("\\n".join(entry) + "\\n")
            
            self._cache_timestamp = None
        except Exception as e:
            print(f"Warning: Could not log decision: {e}")
    
    def compress_context(self, interactions: List[Dict[str, str]]) -> str:
        """Compress a list of interactions into a summary."""
        if len(interactions) <= self.active_window_size:
            return self._format_interactions(interactions)
        
        recent = interactions[-self.active_window_size:]
        older = interactions[:-self.active_window_size]
        older_summary = f"[{len(older)} earlier interactions summarized]"
        
        return f"{older_summary}\\n\\n" + self._format_interactions(recent)
    
    def _format_interactions(self, interactions: List[Dict[str, str]]) -> str:
        """Format interactions for display."""
        formatted = []
        for i, interaction in enumerate(interactions):
            role = interaction.get('role', 'unknown')
            content = interaction.get('content', '')[:200]
            formatted.append(f"{i+1}. {role}: {content}")
        return '\\n'.join(formatted)
    
    def clear_cache(self) -> None:
        """Clear the decisions cache."""
        self._decisions_cache = []
        self._cache_timestamp = None


# Convenience functions
def get_memory_manager() -> MemoryManager:
    return MemoryManager()

def get_relevant_decisions(intent: str, entities: List[str] = None, max_results: int = 5) -> List[DecisionEntry]:
    memory = MemoryManager()
    return memory.get_relevant_decisions(intent, entities, max_results)

def log_decision(choice: str, reasoning: str, implication: str,
                 summary: Optional[str] = None, entities: List[str] = None) -> None:
    memory = MemoryManager()
    memory.log_decision(choice, reasoning, implication, summary, entities)

__all__ = [
    "MemoryManager",
    "DecisionEntry",
    "MemorySummary",
    "get_memory_manager",
    "get_relevant_decisions",
    "log_decision",
]
