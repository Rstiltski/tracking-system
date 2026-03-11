"""
Task Decomposer for AI Assistant

Implements hierarchical task decomposition for breaking complex requests
into manageable subtasks.

Based on AI agent research (2024-2025):
- Hierarchical task decomposition
- Orchestrator-worker pattern
- Dependency tracking between subtasks

Usage:
    from brain.ai_assistant.task_decomposer import TaskDecomposer
    
    decomposer = TaskDecomposer()
    task_tree = decomposer.decompose(
        request="Add new correlation analysis feature",
        max_depth=3
    )
    
    # Get ordered subtasks (respecting dependencies)
    subtasks = task_tree.get_ordered_tasks()
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, field, asdict
from pathlib import Path
from enum import Enum


class TaskStatus(Enum):
    """Status of a task in the decomposition tree."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    BLOCKED = "blocked"
    SKIPPED = "skipped"


class TaskPriority(Enum):
    """Priority level for tasks."""
    CRITICAL = "critical"  # Must complete first
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class TaskNode:
    """A node in the task decomposition tree."""
    task_id: str
    description: str
    parent_id: Optional[str] = None
    children: List[str] = field(default_factory=list)  # Child task IDs
    dependencies: List[str] = field(default_factory=list)  # Tasks that must complete first
    status: TaskStatus = TaskStatus.PENDING
    priority: TaskPriority = TaskPriority.MEDIUM
    estimated_complexity: int = 1  # 1-10 scale
    actual_complexity: Optional[int] = None
    notes: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TaskTree:
    """Complete task decomposition tree."""
    root_task_id: str
    original_request: str
    nodes: Dict[str, TaskNode] = field(default_factory=dict)
    max_depth: int = 0
    current_depth: int = 0
    created_at: datetime = field(default_factory=datetime.now)
    
    def get_node(self, task_id: str) -> Optional[TaskNode]:
        """Get a task node by ID."""
        return self.nodes.get(task_id)
    
    def get_children(self, task_id: str) -> List[TaskNode]:
        """Get direct children of a task."""
        node = self.get_node(task_id)
        if not node:
            return []
        return [self.nodes[child_id] for child_id in node.children if child_id in self.nodes]
    
    def get_ordered_tasks(self) -> List[str]:
        """Get task IDs in dependency-respecting order."""
        ordered = []
        visited = set()
        
        def visit(task_id: str):
            if task_id in visited:
                return
            
            node = self.get_node(task_id)
            if not node:
                return
            
            # Visit dependencies first
            for dep_id in node.dependencies:
                visit(dep_id)
            
            # Visit parent first
            if node.parent_id:
                visit(node.parent_id)
            
            # Then this task
            visited.add(task_id)
            ordered.append(task_id)
        
        # Start from root
        visit(self.root_task_id)
        
        # Visit all nodes (in case of forest)
        for task_id in self.nodes.keys():
            visit(task_id)
        
        return ordered
    
    def get_pending_tasks(self) -> List[TaskNode]:
        """Get all pending tasks."""
        return [
            node for node in self.nodes.values()
            if node.status == TaskStatus.PENDING
        ]
    
    def get_completed_tasks(self) -> List[TaskNode]:
        """Get all completed tasks."""
        return [
            node for node in self.nodes.values()
            if node.status == TaskStatus.COMPLETED
        ]
    
    def get_completion_percentage(self) -> float:
        """Get overall completion percentage."""
        if not self.nodes:
            return 0.0
        
        completed = len(self.get_completed_tasks())
        total = len(self.nodes)
        return (completed / total) * 100
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'root_task_id': self.root_task_id,
            'original_request': self.original_request,
            'nodes': {k: asdict(v) for k, v in self.nodes.items()},
            'max_depth': self.max_depth,
            'current_depth': self.current_depth,
            'created_at': self.created_at.isoformat(),
            'completion_percentage': self.get_completion_percentage()
        }


class TaskDecomposer:
    """
    Decomposes complex requests into hierarchical task trees.
    
    Features:
    - Creates task hierarchies with parent-child relationships
    - Tracks dependencies between tasks
    - Estimates complexity for each subtask
    - Provides ordered execution plans
    """
    
    def __init__(self, templates_path: Optional[str] = None):
        """
        Initialize task decomposer.
        
        Args:
            templates_path: Path to task decomposition templates
        """
        if templates_path is None:
            templates_path = str(Path(__file__).parent / "task_templates.json")
        self.templates_path = templates_path
        
        # Load decomposition templates
        self.templates = self._load_templates()
        
        # Task counter for unique IDs
        self._task_counter = 0
    
    def _load_templates(self) -> Dict[str, Any]:
        """Load task decomposition templates."""
        default_templates = {
            "feature_addition": {
                "description": "Adding a new feature to the system",
                "pattern": ["add", "create", "implement", "new feature"],
                "decomposition": [
                    {"description": "Analyze existing patterns", "complexity": 2, "dependencies": []},
                    {"description": "Define data models", "complexity": 3, "dependencies": ["Analyze existing patterns"]},
                    {"description": "Define tools/APIs", "complexity": 4, "dependencies": ["Define data models"]},
                    {"description": "Implement core logic", "complexity": 5, "dependencies": ["Define tools/APIs"]},
                    {"description": "Create UI components", "complexity": 4, "dependencies": ["Define data models"]},
                    {"description": "Write tests", "complexity": 3, "dependencies": ["Implement core logic"]},
                    {"description": "Update documentation", "complexity": 2, "dependencies": ["Implement core logic", "Create UI components"]},
                    {"description": "Validate and test", "complexity": 3, "dependencies": ["Write tests"]}
                ]
            },
            "bug_fix": {
                "description": "Fixing a bug or issue",
                "pattern": ["fix", "bug", "error", "issue", "problem"],
                "decomposition": [
                    {"description": "Reproduce the issue", "complexity": 2, "dependencies": []},
                    {"description": "Diagnose root cause", "complexity": 4, "dependencies": ["Reproduce the issue"]},
                    {"description": "Plan the fix", "complexity": 2, "dependencies": ["Diagnose root cause"]},
                    {"description": "Implement the fix", "complexity": 3, "dependencies": ["Plan the fix"]},
                    {"description": "Test the fix", "complexity": 3, "dependencies": ["Implement the fix"]},
                    {"description": "Check for regressions", "complexity": 2, "dependencies": ["Test the fix"]}
                ]
            },
            "analysis": {
                "description": "Analyzing codebase or architecture",
                "pattern": ["analyze", "review", "examine", "audit", "understand"],
                "decomposition": [
                    {"description": "Define analysis scope", "complexity": 1, "dependencies": []},
                    {"description": "Identify relevant files", "complexity": 2, "dependencies": ["Define analysis scope"]},
                    {"description": "Read and analyze files", "complexity": 4, "dependencies": ["Identify relevant files"]},
                    {"description": "Identify patterns and issues", "complexity": 3, "dependencies": ["Read and analyze files"]},
                    {"description": "Document findings", "complexity": 2, "dependencies": ["Identify patterns and issues"]}
                ]
            },
            "refactoring": {
                "description": "Refactoring existing code",
                "pattern": ["refactor", "restructure", "reorganize", "improve"],
                "decomposition": [
                    {"description": "Understand current implementation", "complexity": 3, "dependencies": []},
                    {"description": "Define refactoring goals", "complexity": 2, "dependencies": ["Understand current implementation"]},
                    {"description": "Plan refactoring approach", "complexity": 3, "dependencies": ["Define refactoring goals"]},
                    {"description": "Create backup/safety net", "complexity": 1, "dependencies": ["Plan refactoring approach"]},
                    {"description": "Execute refactoring", "complexity": 5, "dependencies": ["Create backup/safety net"]},
                    {"description": "Run tests to verify", "complexity": 2, "dependencies": ["Execute refactoring"]}
                ]
            },
            "documentation": {
                "description": "Creating or updating documentation",
                "pattern": ["document", "write docs", "update readme", "documentation"],
                "decomposition": [
                    {"description": "Identify documentation gaps", "complexity": 2, "dependencies": []},
                    {"description": "Gather source information", "complexity": 3, "dependencies": ["Identify documentation gaps"]},
                    {"description": "Draft documentation", "complexity": 4, "dependencies": ["Gather source information"]},
                    {"description": "Review and refine", "complexity": 2, "dependencies": ["Draft documentation"]},
                    {"description": "Publish/update docs", "complexity": 1, "dependencies": ["Review and refine"]}
                ]
            }
        }
        
        # Try to load from file
        try:
            if os.path.exists(self.templates_path):
                with open(self.templates_path, 'r', encoding='utf-8') as f:
                    loaded = json.load(f)
                    # Merge with defaults
                    default_templates.update(loaded)
        except Exception as e:
            pass  # Use defaults if loading fails
        
        return default_templates
    
    def _generate_task_id(self) -> str:
        """Generate unique task ID."""
        self._task_counter += 1
        return f"task_{self._task_counter:04d}"
    
    def decompose(self, request: str, max_depth: int = 3,
                 context: Optional[Dict[str, Any]] = None) -> TaskTree:
        """
        Decompose a request into a hierarchical task tree.
        
        Args:
            request: The user's request string
            max_depth: Maximum depth of the task tree
            context: Optional context (e.g., current project state)
            
        Returns:
            TaskTree with decomposed tasks
        """
        # Find matching template
        template = self._find_matching_template(request)
        
        # Create root task
        root_id = self._generate_task_id()
        root_task = TaskNode(
            task_id=root_id,
            description=f"Complete: {request[:100]}",
            priority=TaskPriority.CRITICAL,
            estimated_complexity=10
        )
        
        # Create task tree
        tree = TaskTree(
            root_task_id=root_id,
            original_request=request,
            nodes={root_id: root_task},
            max_depth=max_depth
        )
        
        if template:
            # Use template decomposition
            self._apply_template(tree, root_id, template, request)
        else:
            # Generic decomposition
            self._generic_decompose(tree, root_id, request, current_depth=0, max_depth=max_depth)
        
        return tree
    
    def _find_matching_template(self, request: str) -> Optional[Dict[str, Any]]:
        """Find the best matching template for a request."""
        request_lower = request.lower()
        
        best_match = None
        best_score = 0
        
        for template_name, template in self.templates.items():
            score = 0
            for pattern in template.get('pattern', []):
                if pattern in request_lower:
                    score += 1
            
            if score > best_score:
                best_score = score
                best_match = template
        
        return best_match if best_score > 0 else None
    
    def _apply_template(self, tree: TaskTree, parent_id: str,
                       template: Dict[str, Any], request: str) -> None:
        """Apply a template to decompose a task."""
        decomposition = template.get('decomposition', [])
        
        previous_task_id = None
        
        for item in decomposition:
            task_id = self._generate_task_id()
            
            # Determine dependencies
            dependencies = [parent_id]  # Always depend on parent
            if previous_task_id:
                dependencies.append(previous_task_id)
            
            # Add specified dependencies
            for dep_desc in item.get('dependencies', []):
                # Find task with matching description
                for existing_id, existing_node in tree.nodes.items():
                    if dep_desc.lower() in existing_node.description.lower():
                        dependencies.append(existing_id)
                        break
            
            task = TaskNode(
                task_id=task_id,
                description=item.get('description', 'Task'),
                parent_id=parent_id,
                dependencies=list(set(dependencies)),  # Remove duplicates
                priority=self._estimate_priority(item.get('description', '')),
                estimated_complexity=item.get('complexity', 3)
            )
            
            tree.nodes[task_id] = task
            tree.nodes[parent_id].children.append(task_id)
            
            previous_task_id = task_id
        
        # Update max depth
        tree.max_depth = max(tree.max_depth, 2)  # Root + 1 level
    
    def _generic_decompose(self, tree: TaskTree, parent_id: str,
                          request: str, current_depth: int, max_depth: int) -> None:
        """Generic decomposition when no template matches."""
        if current_depth >= max_depth:
            return
        
        # Create subtasks based on common patterns
        generic_tasks = [
            ("Understand requirements", 2, []),
            ("Plan approach", 2, ["Understand requirements"]),
            ("Implement solution", 5, ["Plan approach"]),
            ("Test and validate", 3, ["Implement solution"]),
        ]
        
        previous_task_id = None
        
        for desc, complexity, deps in generic_tasks:
            task_id = self._generate_task_id()
            
            dependencies = [parent_id]
            if previous_task_id:
                dependencies.append(previous_task_id)
            
            task = TaskNode(
                task_id=task_id,
                description=f"{desc}: {request[:50]}",
                parent_id=parent_id,
                dependencies=list(set(dependencies)),
                priority=TaskPriority.MEDIUM,
                estimated_complexity=complexity
            )
            
            tree.nodes[task_id] = task
            tree.nodes[parent_id].children.append(task_id)
            
            previous_task_id = task_id
        
        tree.max_depth = max(tree.max_depth, current_depth + 1)
    
    def _estimate_priority(self, description: str) -> TaskPriority:
        """Estimate task priority from description."""
        desc_lower = description.lower()
        
        if any(word in desc_lower for word in ['critical', 'must', 'required', 'first']):
            return TaskPriority.CRITICAL
        elif any(word in desc_lower for word in ['important', 'high', 'priority']):
            return TaskPriority.HIGH
        elif any(word in desc_lower for word in ['optional', 'nice to have', 'low']):
            return TaskPriority.LOW
        else:
            return TaskPriority.MEDIUM
    
    def update_task_status(self, tree: TaskTree, task_id: str,
                          status: TaskStatus, notes: str = "") -> None:
        """
        Update the status of a task.
        
        Args:
            tree: TaskTree containing the task
            task_id: ID of the task to update
            status: New status
            notes: Optional notes to add
        """
        node = tree.get_node(task_id)
        if not node:
            return
        
        node.status = status
        
        if status == TaskStatus.IN_PROGRESS:
            node.started_at = datetime.now()
        elif status == TaskStatus.COMPLETED:
            node.completed_at = datetime.now()
        
        if notes:
            node.notes = notes
        
        # Update parent status if all children complete
        if status == TaskStatus.COMPLETED and node.parent_id:
            parent = tree.get_node(node.parent_id)
            if parent:
                all_children_complete = all(
                    tree.nodes[child_id].status == TaskStatus.COMPLETED
                    for child_id in parent.children
                    if child_id in tree.nodes
                )
                if all_children_complete:
                    parent.status = TaskStatus.COMPLETED
                    parent.completed_at = datetime.now()
    
    def get_next_task(self, tree: TaskTree) -> Optional[TaskNode]:
        """
        Get the next task to work on (highest priority, not blocked).
        
        Args:
            tree: TaskTree to search
            
        Returns:
            Next task node or None
        """
        pending = tree.get_pending_tasks()
        
        # Filter out blocked tasks
        available = []
        for task in pending:
            is_blocked = False
            for dep_id in task.dependencies:
                dep_node = tree.get_node(dep_id)
                if dep_node and dep_node.status != TaskStatus.COMPLETED:
                    is_blocked = True
                    break
            
            if not is_blocked:
                available.append(task)
        
        if not available:
            return None
        
        # Sort by priority
        priority_order = {
            TaskPriority.CRITICAL: 0,
            TaskPriority.HIGH: 1,
            TaskPriority.MEDIUM: 2,
            TaskPriority.LOW: 3
        }
        
        available.sort(key=lambda t: priority_order[t.priority])
        
        return available[0]
    
    def get_task_summary(self, tree: TaskTree) -> str:
        """
        Get a human-readable summary of task tree status.
        
        Args:
            tree: TaskTree
            
        Returns:
            Summary string
        """
        lines = [
            f"Task Tree: {tree.original_request[:50]}...",
            f"Completion: {tree.get_completion_percentage():.1f}%",
            f"Total tasks: {len(tree.nodes)}",
            f"Completed: {len(tree.get_completed_tasks())}",
            f"Pending: {len(tree.get_pending_tasks())}",
            ""
        ]
        
        # Add task list
        for task_id in tree.get_ordered_tasks():
            node = tree.get_node(task_id)
            if node:
                indent = "  " * (node.parent_id is not None)
                status_icon = {
                    TaskStatus.PENDING: "⏳",
                    TaskStatus.IN_PROGRESS: "🔄",
                    TaskStatus.COMPLETED: "✅",
                    TaskStatus.BLOCKED: "🚫",
                    TaskStatus.SKIPPED: "⏭️"
                }.get(node.status, "❓")
                
                lines.append(f"{indent}{status_icon} [{node.priority.value}] {node.description}")
        
        return "\n".join(lines)


# Convenience functions
def decompose_request(request: str, max_depth: int = 3) -> TaskTree:
    """Quick task decomposition."""
    decomposer = TaskDecomposer()
    return decomposer.decompose(request, max_depth)


def get_next_task(tree: TaskTree) -> Optional[TaskNode]:
    """Get next task from tree."""
    decomposer = TaskDecomposer()
    return decomposer.get_next_task(tree)


__all__ = [
    "TaskDecomposer",
    "TaskTree",
    "TaskNode",
    "TaskStatus",
    "TaskPriority",
    "decompose_request",
    "get_next_task",
]
