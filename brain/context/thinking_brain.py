"""
ThinkingBrain - The AI Context Processor

The ThinkingBrain is the bridge between simple user prompts and the
deep understanding embedded in the brain system architecture.

It follows the Brain Context Protocol:
1. ALWAYS read README.md files for context
2. ALWAYS use the brain folder as the thinking process
3. Simple prompts → Deep understanding through brain architecture

Usage:
    from brain.context import ThinkingBrain
    
    brain = ThinkingBrain()
    
    # Process a simple prompt
    result = brain.think("add a habit")
    
    # Get the thinking trace
    print(result.reasoning)
    print(result.action)
"""
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import re
import json

from brain.context.context_loader import ContextLoader, get_context_loader


class IntentCategory(str, Enum):
    """Categories of user intent"""
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    QUERY = "query"
    NAVIGATE = "navigate"
    CONFIGURE = "configure"
    ANALYZE = "analyze"
    HELP = "help"
    UNKNOWN = "unknown"


class Domain(str, Enum):
    """System domains"""
    HABITS = "habits"
    TASKS = "tasks"
    FINANCES = "finances"
    HEALTH = "health"
    TIME = "time"
    GOALS = "goals"
    ACHIEVEMENTS = "achievements"
    SYSTEM = "system"
    BRAIN = "brain"
    UNKNOWN = "unknown"


@dataclass
class ThinkingResult:
    """Result of the thinking process"""
    original_prompt: str
    interpreted_intent: IntentCategory
    identified_domain: Domain
    reasoning: str
    context_used: List[str]
    action: str
    suggested_command: Optional[str] = None
    suggested_params: Dict[str, Any] = field(default_factory=dict)
    confidence: float = 0.0
    alternative_interpretations: List[str] = field(default_factory=list)
    brain_pathway: str = ""
    related_features: List[str] = field(default_factory=list)


@dataclass
class BrainPathway:
    """Represents a processing pathway through the brain"""
    name: str
    description: str
    steps: List[str]
    brain_components: List[str]


class ThinkingBrain:
    """
    The ThinkingBrain processes simple prompts through the brain architecture.
    
    It embodies the Brain Context Protocol:
    - README.md files are the source of truth
    - Brain folder is the thinking process
    - Simple prompts yield deep understanding
    
    Architecture:
    ┌─────────────────────────────────────────────────────────────┐
    │                    THINKING BRAIN                            │
    │                  (Context Processor)                         │
    ├─────────────────────────────────────────────────────────────┤
    │                                                              │
    │  1. LOAD CONTEXT                                             │
    │     └── ContextLoader → All README.md files                  │
    │                                                              │
    │  2. INTERPRET INTENT                                         │
    │     └── Parse prompt → Identify domain & action              │
    │                                                              │
    │  3. MAP TO BRAIN                                             │
    │     └── Find brain pathway for execution                     │
    │                                                              │
    │  4. GENERATE RESPONSE                                        │
    │     └── Return action with reasoning                         │
    │                                                              │
    └─────────────────────────────────────────────────────────────┘
    
    Usage:
        brain = ThinkingBrain()
        result = brain.think("add a habit")
        
        print(f"Intent: {result.interpreted_intent}")
        print(f"Domain: {result.identified_domain}")
        print(f"Action: {result.action}")
    """
    
    # Intent keywords mapping
    INTENT_KEYWORDS = {
        IntentCategory.CREATE: [
            "add", "create", "new", "make", "start", "begin", "set up",
            "initialize", "launch", "establish"
        ],
        IntentCategory.READ: [
            "show", "display", "list", "get", "view", "see", "read",
            "what", "which", "find"
        ],
        IntentCategory.UPDATE: [
            "update", "edit", "modify", "change", "alter", "adjust",
            "revise", "correct"
        ],
        IntentCategory.DELETE: [
            "delete", "remove", "clear", "erase", "drop", "trash",
            "eliminate"
        ],
        IntentCategory.QUERY: [
            "how many", "how much", "count", "total", "sum", "average",
            "statistics", "report", "analyze"
        ],
        IntentCategory.NAVIGATE: [
            "go to", "open", "switch", "navigate", "move to", "jump"
        ],
        IntentCategory.CONFIGURE: [
            "configure", "settings", "preferences", "setup", "options",
            "customize"
        ],
        IntentCategory.ANALYZE: [
            "analyze", "examine", "inspect", "review", "assess",
            "evaluate", "diagnose"
        ],
        IntentCategory.HELP: [
            "help", "how do i", "what is", "explain", "guide",
            "tutorial", "documentation"
        ],
    }
    
    # Domain keywords mapping
    DOMAIN_KEYWORDS = {
        Domain.HABITS: [
            "habit", "streak", "daily", "routine", "consistency",
            "check-in", "tracker"
        ],
        Domain.TASKS: [
            "task", "todo", "to-do", "item", "priority", "due",
            "complete", "finish"
        ],
        Domain.FINANCES: [
            "finance", "money", "budget", "expense", "income",
            "transaction", "cost", "payment", "dollar"
        ],
        Domain.HEALTH: [
            "health", "weight", "sleep", "mood", "exercise",
            "wellness", "fitness", "calories"
        ],
        Domain.TIME: [
            "time", "timer", "stopwatch", "clock", "hours",
            "productivity", "focus", "session"
        ],
        Domain.GOALS: [
            "goal", "target", "objective", "milestone", "progress",
            "deadline", "aim"
        ],
        Domain.ACHIEVEMENTS: [
            "achievement", "badge", "reward", "xp", "level",
            "unlock", "celebrate", "gamification"
        ],
        Domain.BRAIN: [
            "brain", "ai", "neural", "cognitive", "thinking",
            "processing", "intelligence"
        ],
        Domain.SYSTEM: [
            "system", "settings", "config", "theme", "dark mode",
            "export", "import", "backup"
        ],
    }
    
    # Brain pathways for different operations
    BRAIN_PATHWAYS = {
        "habit_create": BrainPathway(
            name="Habit Creation",
            description="Create a new habit with gamification",
            steps=[
                "1. Validate habit parameters",
                "2. Create habit entity",
                "3. Initialize streak counter",
                "4. Award XP for creation",
                "5. Emit HABIT_CREATED event"
            ],
            brain_components=["Router", "OpsBrain", "Cerebellum", "NervousSystem"]
        ),
        "task_create": BrainPathway(
            name="Task Creation",
            description="Create a new task with priority",
            steps=[
                "1. Validate task parameters",
                "2. Set priority level",
                "3. Calculate XP reward",
                "4. Create task entity",
                "5. Emit TASK_CREATED event"
            ],
            brain_components=["Router", "OpsBrain", "Cerebellum", "NervousSystem"]
        ),
        "finance_record": BrainPathway(
            name="Financial Recording",
            description="Record a financial transaction",
            steps=[
                "1. Validate transaction data",
                "2. Categorize transaction",
                "3. Update budget calculations",
                "4. Record to ledger",
                "5. Emit TRANSACTION_RECORDED event"
            ],
            brain_components=["Router", "FinanceBrain", "Cerebellum", "NervousSystem"]
        ),
        "goal_set": BrainPathway(
            name="Goal Setting",
            description="Set a new personal goal",
            steps=[
                "1. Validate goal parameters",
                "2. Calculate milestones",
                "3. Set deadline tracking",
                "4. Create goal entity",
                "5. Emit GOAL_CREATED event"
            ],
            brain_components=["Router", "OpsBrain", "Cerebellum", "NervousSystem"]
        ),
        "health_log": BrainPathway(
            name="Health Logging",
            description="Log health metrics",
            steps=[
                "1. Validate health data",
                "2. Calculate health score",
                "3. Update trends",
                "4. Store entry",
                "5. Emit HEALTH_LOGGED event"
            ],
            brain_components=["Router", "OpsBrain", "Cerebellum", "NervousSystem"]
        ),
        "time_track": BrainPathway(
            name="Time Tracking",
            description="Track time for productivity",
            steps=[
                "1. Start/stop timer",
                "2. Categorize time",
                "3. Calculate duration",
                "4. Store time entry",
                "5. Emit TIME_LOGGED event"
            ],
            brain_components=["Router", "OpsBrain", "Cerebellum", "NervousSystem"]
        ),
        "system_query": BrainPathway(
            name="System Query",
            description="Query system state or data",
            steps=[
                "1. Parse query parameters",
                "2. Route to appropriate brain",
                "3. Retrieve data",
                "4. Format response",
                "5. Return results"
            ],
            brain_components=["Router", "OpsBrain", "FinanceBrain", "RelationBrain"]
        ),
        "brain_process": BrainPathway(
            name="Brain Processing",
            description="Process through brain architecture",
            steps=[
                "1. Load context from READMEs",
                "2. Interpret intent",
                "3. Route through brain",
                "4. Execute via Cerebellum",
                "5. Emit completion event"
            ],
            brain_components=["ContextLoader", "Router", "MetaBrain", "Cerebellum"]
        ),
    }
    
    def __init__(self, context_loader: Optional[ContextLoader] = None):
        """
        Initialize the ThinkingBrain.
        
        Args:
            context_loader: Optional custom context loader
        """
        self.context_loader = context_loader or get_context_loader()
        self._context_loaded = False
    
    def _ensure_context(self):
        """Ensure context is loaded before processing"""
        if not self._context_loaded:
            self.context_loader.load_all()
            self._context_loaded = True
    
    def think(self, prompt: str) -> ThinkingResult:
        """
        Process a simple prompt through the brain architecture.
        
        This is the main entry point for the ThinkingBrain.
        It follows the Brain Context Protocol:
        1. Load context from README.md files
        2. Interpret the user's intent
        3. Map to the appropriate brain pathway
        4. Return a detailed thinking result
        
        Args:
            prompt: Simple user prompt (e.g., "add a habit")
            
        Returns:
            ThinkingResult with full reasoning and action
        """
        self._ensure_context()
        
        # Step 1: Interpret intent
        intent = self._interpret_intent(prompt)
        
        # Step 2: Identify domain
        domain = self._identify_domain(prompt)
        
        # Step 3: Find relevant context
        context_used = self._find_relevant_context(prompt, domain)
        
        # Step 4: Determine brain pathway
        pathway = self._determine_pathway(intent, domain)
        
        # Step 5: Generate action
        action, command, params = self._generate_action(intent, domain, prompt)
        
        # Step 6: Find related features
        related = self._find_related_features(domain)
        
        # Step 7: Calculate confidence
        confidence = self._calculate_confidence(intent, domain, context_used)
        
        # Step 8: Generate reasoning
        reasoning = self._generate_reasoning(
            prompt, intent, domain, pathway, context_used
        )
        
        # Step 9: Generate alternatives
        alternatives = self._generate_alternatives(prompt, intent, domain)
        
        return ThinkingResult(
            original_prompt=prompt,
            interpreted_intent=intent,
            identified_domain=domain,
            reasoning=reasoning,
            context_used=context_used,
            action=action,
            suggested_command=command,
            suggested_params=params,
            confidence=confidence,
            alternative_interpretations=alternatives,
            brain_pathway=pathway.name if pathway else "",
            related_features=related
        )
    
    def _interpret_intent(self, prompt: str) -> IntentCategory:
        """Interpret the user's intent from the prompt"""
        prompt_lower = prompt.lower()
        
        # Check each intent category
        for intent, keywords in self.INTENT_KEYWORDS.items():
            for keyword in keywords:
                if keyword in prompt_lower:
                    return intent
        
        return IntentCategory.UNKNOWN
    
    def _identify_domain(self, prompt: str) -> Domain:
        """Identify the domain the prompt relates to"""
        prompt_lower = prompt.lower()
        
        # Check each domain
        for domain, keywords in self.DOMAIN_KEYWORDS.items():
            for keyword in keywords:
                if keyword in prompt_lower:
                    return domain
        
        return Domain.UNKNOWN
    
    def _find_relevant_context(self, prompt: str, domain: Domain) -> List[str]:
        """Find relevant context from README files"""
        context_used = []
        
        # Always include main README
        main_readme = self.context_loader.get_main_readme()
        if main_readme:
            context_used.append("README.md")
        
        # Include brain README for brain-related queries
        if domain == Domain.BRAIN or "brain" in prompt.lower():
            brain_readme = self.context_loader.get_brain_readme()
            if brain_readme:
                context_used.append("brain/README.md")
        
        # Search for domain-specific context
        search_results = self.context_loader.search(domain.value)
        for path in search_results.keys():
            if path not in context_used:
                context_used.append(path)
        
        return context_used[:5]  # Limit to top 5
    
    def _determine_pathway(self, intent: IntentCategory, domain: Domain) -> Optional[BrainPathway]:
        """Determine the brain pathway for this request"""
        pathway_key = None
        
        if domain == Domain.HABITS:
            if intent == IntentCategory.CREATE:
                pathway_key = "habit_create"
            elif intent == IntentCategory.READ:
                pathway_key = "system_query"
        
        elif domain == Domain.TASKS:
            if intent == IntentCategory.CREATE:
                pathway_key = "task_create"
            elif intent == IntentCategory.READ:
                pathway_key = "system_query"
        
        elif domain == Domain.FINANCES:
            if intent in [IntentCategory.CREATE, IntentCategory.UPDATE]:
                pathway_key = "finance_record"
            elif intent == IntentCategory.READ:
                pathway_key = "system_query"
        
        elif domain == Domain.GOALS:
            if intent == IntentCategory.CREATE:
                pathway_key = "goal_set"
            elif intent == IntentCategory.READ:
                pathway_key = "system_query"
        
        elif domain == Domain.HEALTH:
            if intent in [IntentCategory.CREATE, IntentCategory.UPDATE]:
                pathway_key = "health_log"
            elif intent == IntentCategory.READ:
                pathway_key = "system_query"
        
        elif domain == Domain.TIME:
            if intent in [IntentCategory.CREATE, IntentCategory.UPDATE]:
                pathway_key = "time_track"
            elif intent == IntentCategory.READ:
                pathway_key = "system_query"
        
        elif domain == Domain.BRAIN:
            pathway_key = "brain_process"
        
        # Default to system query for read operations
        if pathway_key is None and intent == IntentCategory.READ:
            pathway_key = "system_query"
        
        return self.BRAIN_PATHWAYS.get(pathway_key)
    
    def _generate_action(self, intent: IntentCategory, domain: Domain, prompt: str) -> Tuple[str, Optional[str], Dict[str, Any]]:
        """Generate the action to take"""
        action_parts = []
        command = None
        params = {}
        
        # Build action description
        action_parts.append(f"Intent: {intent.value}")
        action_parts.append(f"Domain: {domain.value}")
        
        # Determine specific action
        if domain == Domain.HABITS and intent == IntentCategory.CREATE:
            action_parts.append("Action: Create new habit in the tracking system")
            command = "HabitCreate"
            params = {"name": "", "icon": "✓", "color": "#6366f1", "frequency": "daily"}
        
        elif domain == Domain.TASKS and intent == IntentCategory.CREATE:
            action_parts.append("Action: Create new task with priority")
            command = "TaskCreate"
            params = {"title": "", "priority": "medium", "completed": False}
        
        elif domain == Domain.FINANCES and intent in [IntentCategory.CREATE, IntentCategory.UPDATE]:
            action_parts.append("Action: Record financial transaction")
            command = "TransactionCreate"
            params = {"description": "", "amount": 0, "type": "expense", "category": "general"}
        
        elif domain == Domain.GOALS and intent == IntentCategory.CREATE:
            action_parts.append("Action: Create new goal with target")
            command = "GoalCreate"
            params = {"title": "", "target": 100, "current": 0, "unit": "%"}
        
        elif domain == Domain.HEALTH and intent in [IntentCategory.CREATE, IntentCategory.UPDATE]:
            action_parts.append("Action: Log health metrics")
            command = "HealthLog"
            params = {"weight": None, "sleepHours": None, "mood": "good"}
        
        elif domain == Domain.TIME and intent in [IntentCategory.CREATE, IntentCategory.UPDATE]:
            action_parts.append("Action: Track time entry")
            command = "TimeTrack"
            params = {"category": "general", "duration": 0}
        
        elif intent == IntentCategory.HELP:
            action_parts.append("Action: Provide help and documentation")
            command = "HelpRequest"
        
        elif intent == IntentCategory.READ or intent == IntentCategory.QUERY:
            action_parts.append("Action: Query and display data")
            command = "DataQuery"
        
        else:
            action_parts.append("Action: Process through brain system")
            command = "GenericCommand"
        
        return '\n'.join(action_parts), command, params
    
    def _find_related_features(self, domain: Domain) -> List[str]:
        """Find features related to the identified domain"""
        feature_map = {
            Domain.HABITS: [
                "Streak tracking",
                "XP rewards for completion",
                "Daily check-ins",
                "Habit categories",
                "Completion history"
            ],
            Domain.TASKS: [
                "Priority levels (low/medium/high)",
                "Due date tracking",
                "Category organization",
                "XP rewards by priority",
                "Completion status"
            ],
            Domain.FINANCES: [
                "Income/expense tracking",
                "Budget monitoring",
                "Category-based organization",
                "Financial charts",
                "Transaction history"
            ],
            Domain.HEALTH: [
                "Weight tracking",
                "Sleep logging",
                "Mood tracking",
                "Health score calculation",
                "Trend visualization"
            ],
            Domain.TIME: [
                "Timer/stopwatch",
                "Time persistence",
                "Category tracking",
                "Productivity charts",
                "Daily activity overview"
            ],
            Domain.GOALS: [
                "Progress tracking",
                "Deadline management",
                "Milestone celebrations",
                "Visual progress bars",
                "Goal completion rewards"
            ],
            Domain.ACHIEVEMENTS: [
                "XP system",
                "Level progression",
                "Achievement badges",
                "Celebration effects",
                "Gamification rewards"
            ],
            Domain.BRAIN: [
                "Command routing",
                "Policy enforcement",
                "State machines",
                "Audit logging",
                "Self-repair system"
            ],
            Domain.SYSTEM: [
                "Theme switching",
                "Data export/import",
                "Notification settings",
                "Dark mode",
                "Backup/restore"
            ],
        }
        
        return feature_map.get(domain, [])
    
    def _calculate_confidence(self, intent: IntentCategory, domain: Domain, context_used: List[str]) -> float:
        """Calculate confidence score for the interpretation"""
        confidence = 0.5  # Base confidence
        
        # Increase confidence for clear intent
        if intent != IntentCategory.UNKNOWN:
            confidence += 0.2
        
        # Increase confidence for clear domain
        if domain != Domain.UNKNOWN:
            confidence += 0.2
        
        # Increase confidence for context found
        if context_used:
            confidence += min(0.1 * len(context_used), 0.1)
        
        return min(confidence, 1.0)
    
    def _generate_reasoning(self, prompt: str, intent: IntentCategory, domain: Domain, 
                           pathway: Optional[BrainPathway], context_used: List[str]) -> str:
        """Generate human-readable reasoning"""
        reasoning_parts = [
            f"Analyzing prompt: '{prompt}'",
            "",
            "## Context Loading",
            f"Loaded {len(context_used)} README files for context:",
        ]
        
        for ctx in context_used:
            reasoning_parts.append(f"  - {ctx}")
        
        reasoning_parts.extend([
            "",
            "## Intent Analysis",
            f"Detected intent: **{intent.value}**",
            f"This indicates the user wants to {self._intent_description(intent)}.",
            "",
            "## Domain Identification",
            f"Identified domain: **{domain.value}**",
            f"This relates to the {domain.value} module of the tracking system.",
        ])
        
        if pathway:
            reasoning_parts.extend([
                "",
                "## Brain Pathway",
                f"Selected pathway: **{pathway.name}**",
                f"{pathway.description}",
                "",
                "Processing steps:",
            ])
            for step in pathway.steps:
                reasoning_parts.append(f"  {step}")
            
            reasoning_parts.append("")
            reasoning_parts.append("Brain components involved:")
            for component in pathway.brain_components:
                reasoning_parts.append(f"  - {component}")
        
        reasoning_parts.extend([
            "",
            "## Conclusion",
            f"The prompt '{prompt}' has been interpreted as a **{intent.value}**",
            f"operation in the **{domain.value}** domain.",
        ])
        
        return '\n'.join(reasoning_parts)
    
    def _intent_description(self, intent: IntentCategory) -> str:
        """Get human description for an intent"""
        descriptions = {
            IntentCategory.CREATE: "create something new",
            IntentCategory.READ: "view or retrieve information",
            IntentCategory.UPDATE: "modify existing data",
            IntentCategory.DELETE: "remove something",
            IntentCategory.QUERY: "analyze or get statistics",
            IntentCategory.NAVIGATE: "move to a different view",
            IntentCategory.CONFIGURE: "change settings or preferences",
            IntentCategory.ANALYZE: "examine or diagnose",
            IntentCategory.HELP: "get help or documentation",
            IntentCategory.UNKNOWN: "perform an action",
        }
        return descriptions.get(intent, "perform an action")
    
    def _generate_alternatives(self, prompt: str, intent: IntentCategory, domain: Domain) -> List[str]:
        """Generate alternative interpretations"""
        alternatives = []
        
        # If domain is unknown, suggest possible domains
        if domain == Domain.UNKNOWN:
            # Check for partial matches
            prompt_lower = prompt.lower()
            for d, keywords in self.DOMAIN_KEYWORDS.items():
                for keyword in keywords:
                    if keyword in prompt_lower:
                        alternatives.append(f"Could also relate to: {d.value}")
                        break
        
        # If intent is unclear, suggest alternatives
        if intent == IntentCategory.UNKNOWN:
            alternatives.append("Could be a query or navigation request")
        
        return alternatives[:3]  # Limit to 3 alternatives
    
    def get_thinking_trace(self, prompt: str) -> str:
        """
        Get a detailed thinking trace for debugging.
        
        This shows the full reasoning process for a prompt.
        """
        result = self.think(prompt)
        
        trace = [
            "=" * 60,
            "THINKING BRAIN - PROCESSING TRACE",
            "=" * 60,
            "",
            f"Input: '{prompt}'",
            "",
            result.reasoning,
            "",
            "=" * 60,
            "RESULT",
            "=" * 60,
            "",
            f"Intent: {result.interpreted_intent.value}",
            f"Domain: {result.identified_domain.value}",
            f"Confidence: {result.confidence:.0%}",
            "",
            "Action:",
            result.action,
        ]
        
        if result.suggested_command:
            trace.extend([
                "",
                f"Suggested Command: {result.suggested_command}",
                f"Parameters: {json.dumps(result.suggested_params, indent=2)}",
            ])
        
        if result.related_features:
            trace.extend([
                "",
                "Related Features:",
            ])
            for feature in result.related_features:
                trace.append(f"  - {feature}")
        
        return '\n'.join(trace)


# Convenience functions
def think(prompt: str) -> ThinkingResult:
    """Process a prompt through the ThinkingBrain"""
    brain = ThinkingBrain()
    return brain.think(prompt)


def get_thinking_trace(prompt: str) -> str:
    """Get a detailed thinking trace for a prompt"""
    brain = ThinkingBrain()
    return brain.get_thinking_trace(prompt)