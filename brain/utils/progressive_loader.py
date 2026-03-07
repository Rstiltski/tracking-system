"""
Progressive Loader - Intelligent Content Loading System

Provides progressive loading capabilities with priority-based content delivery.
Uses intelligent loading strategies to optimize perceived performance and user experience.

Features:
- Priority-based content loading
- Skeleton UI components
- Progressive enhancement framework
- Perceived performance optimization
- Integration with existing lazy loading and predictive systems

Usage:
    from brain.utils.progressive_loader import ProgressiveLoader
    
    # Initialize progressive loader
    loader = ProgressiveLoader()
    
    # Progressive loading operations
    loader.load_page_content(page_name, priority="high")
    loader.show_skeleton("dashboard")
    loader.hide_skeleton("dashboard")
    
    # Content prioritization
    loader.prioritize_content(["critical", "important", "nice-to-have"])
"""

import time
import logging
import threading
from typing import Dict, List, Optional, Any, Callable, Union, Tuple
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import json
import asyncio
from concurrent.futures import ThreadPoolExecutor, Future

import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class LoadingTask:
    """Represents a progressive loading task."""
    task_id: str
    content_type: str  # 'critical', 'important', 'nice-to-have'
    priority: int  # 1 (highest) to 10 (lowest)
    load_function: Callable
    dependencies: List[str] = field(default_factory=list)
    estimated_duration: float = 0.0
    actual_duration: Optional[float] = None
    status: str = "pending"  # pending, loading, completed, failed
    retry_count: int = 0
    max_retries: int = 3
    timestamp: float = field(default_factory=time.time)


@dataclass
class SkeletonState:
    """Represents skeleton UI state."""
    component_id: str
    skeleton_type: str  # 'card', 'list', 'chart', 'form'
    placeholder_text: str = "Loading..."
    animation_style: str = "pulse"  # 'pulse', 'wave', 'none'
    estimated_duration: float = 1.0
    start_time: float = field(default_factory=time.time)
    visible: bool = True


class ProgressiveLoader:
    """
    Main progressive loading system.
    
    Features:
    - Priority-based content loading
    - Skeleton UI management
    - Progressive enhancement
    - Performance optimization
    - Integration with predictive loading
    """
    
    def __init__(self, predictive_loader=None, lazy_loader=None):
        """
        Initialize progressive loader.
        
        Args:
            predictive_loader: Predictive loader instance for integration
            lazy_loader: Lazy loader instance for integration
        """
        self.predictive_loader = predictive_loader
        self.lazy_loader = lazy_loader
        
        # Loading management
        self.tasks: Dict[str, LoadingTask] = {}
        self.task_queue: List[LoadingTask] = []
        self.active_tasks: Dict[str, Future] = {}
        self.completed_tasks: List[str] = []
        
        # Skeleton management
        self.skeletons: Dict[str, SkeletonState] = {}
        self.skeleton_animations: Dict[str, threading.Timer] = {}
        
        # Performance tracking
        self.loading_metrics: Dict[str, List[float]] = defaultdict(list)
        self.performance_history: List[Dict[str, Any]] = []
        
        # Configuration
        self.max_concurrent_loads = 5
        self.retry_delay = 1.0
        self.skeleton_timeout = 10.0  # seconds
        self.progressive_timeout = 30.0  # seconds
        
        # Thread management
        self.executor = ThreadPoolExecutor(max_workers=10)
        self.loading_thread: Optional[threading.Thread] = None
        self.is_running = False
        
        # Event callbacks
        self.on_task_start: Optional[Callable] = None
        self.on_task_complete: Optional[Callable] = None
        self.on_task_fail: Optional[Callable] = None
        self.on_skeleton_show: Optional[Callable] = None
        self.on_skeleton_hide: Optional[Callable] = None
        
        logger.info("Progressive loader initialized")
    
    def add_task(self, task_id: str, content_type: str, priority: int, 
                load_function: Callable, dependencies: List[str] = None,
                estimated_duration: float = 0.0) -> None:
        """
        Add a loading task to the queue.
        
        Args:
            task_id: Unique task identifier
            content_type: Content type category
            priority: Loading priority (1-10, 1 is highest)
            load_function: Function to execute for loading
            dependencies: List of task IDs this task depends on
            estimated_duration: Estimated loading time in seconds
        """
        task = LoadingTask(
            task_id=task_id,
            content_type=content_type,
            priority=priority,
            load_function=load_function,
            dependencies=dependencies or [],
            estimated_duration=estimated_duration
        )
        
        self.tasks[task_id] = task
        self.task_queue.append(task)
        
        # Sort queue by priority
        self.task_queue.sort(key=lambda t: t.priority)
        
        logger.debug(f"Added task: {task_id} (priority: {priority})")
    
    def load_page_content(self, page_name: str, priority: str = "high") -> Dict[str, Any]:
        """
        Load page content progressively.
        
        Args:
            page_name: Name of the page to load
            priority: Loading priority level
            
        Returns:
            Loading results and status
        """
        start_time = time.time()
        
        # Determine priority level
        priority_map = {
            "high": 1, "medium": 5, "low": 8,
            "critical": 1, "important": 3, "nice-to-have": 7
        }
        priority_level = priority_map.get(priority, 5)
        
        # Create loading plan
        loading_plan = self._create_loading_plan(page_name, priority_level)
        
        # Execute loading plan
        results = self._execute_loading_plan(loading_plan)
        
        # Track performance
        duration = time.time() - start_time
        self._record_performance(page_name, duration, results)
        
        return {
            "page": page_name,
            "priority": priority,
            "duration": duration,
            "results": results,
            "completed_tasks": len([t for t in results.values() if t.get('status') == 'completed']),
            "failed_tasks": len([t for t in results.values() if t.get('status') == 'failed'])
        }
    
    def _create_loading_plan(self, page_name: str, priority_level: int) -> List[LoadingTask]:
        """
        Create a loading plan for a page.
        
        Args:
            page_name: Name of the page
            priority_level: Priority level
            
        Returns:
            List of tasks to execute
        """
        # Get predictive loading suggestions
        if self.predictive_loader:
            predictions = self.predictive_loader.predict_next_pages(page_name, limit=5)
            predicted_pages = [p[0] for p in predictions]
        else:
            predicted_pages = []
        
        # Create tasks based on page type
        tasks = []
        
        if page_name == "dashboard":
            tasks.extend([
                LoadingTask(
                    task_id=f"dashboard_critical_{int(time.time())}",
                    content_type="critical",
                    priority=1,
                    load_function=self._load_dashboard_critical_data,
                    estimated_duration=0.5
                ),
                LoadingTask(
                    task_id=f"dashboard_charts_{int(time.time())}",
                    content_type="important",
                    priority=3,
                    load_function=self._load_dashboard_charts,
                    dependencies=[tasks[0].task_id if tasks else None],
                    estimated_duration=1.0
                ),
                LoadingTask(
                    task_id=f"dashboard_analytics_{int(time.time())}",
                    content_type="nice-to-have",
                    priority=7,
                    load_function=self._load_dashboard_analytics,
                    dependencies=[tasks[1].task_id if len(tasks) > 1 else None],
                    estimated_duration=2.0
                )
            ])
        
        elif page_name == "habits":
            tasks.extend([
                LoadingTask(
                    task_id=f"habits_list_{int(time.time())}",
                    content_type="critical",
                    priority=1,
                    load_function=self._load_habits_list,
                    estimated_duration=0.3
                ),
                LoadingTask(
                    task_id=f"habits_stats_{int(time.time())}",
                    content_type="important",
                    priority=4,
                    load_function=self._load_habits_stats,
                    dependencies=[tasks[0].task_id],
                    estimated_duration=0.8
                )
            ])
        
        # Sort by priority and add to queue
        tasks.sort(key=lambda t: t.priority)
        for task in tasks:
            self.add_task(
                task.task_id, task.content_type, task.priority,
                task.load_function, task.dependencies, task.estimated_duration
            )
        
        return tasks
    
    def _execute_loading_plan(self, tasks: List[LoadingTask]) -> Dict[str, Dict[str, Any]]:
        """
        Execute a loading plan.
        
        Args:
            tasks: List of tasks to execute
            
        Returns:
            Execution results
        """
        results = {}
        
        # Start loading thread if not running
        if not self.is_running:
            self.start_loading()
        
        # Submit tasks to executor
        futures = {}
        for task in tasks:
            if not task.dependencies or all(dep in self.completed_tasks for dep in task.dependencies):
                future = self.executor.submit(self._execute_task, task)
                futures[task.task_id] = future
        
        # Wait for completion with timeout
        try:
            for task_id, future in futures.items():
                try:
                    result = future.result(timeout=self.progressive_timeout)
                    results[task_id] = result
                except Exception as e:
                    results[task_id] = {
                        "status": "failed",
                        "error": str(e),
                        "task_id": task_id
                    }
        except Exception as e:
            logger.error(f"Loading plan execution failed: {e}")
        
        return results
    
    def _execute_task(self, task: LoadingTask) -> Dict[str, Any]:
        """
        Execute a single loading task.
        
        Args:
            task: Task to execute
            
        Returns:
            Task execution result
        """
        start_time = time.time()
        task.status = "loading"
        
        # Notify task start
        if self.on_task_start:
            self.on_task_start(task)
        
        try:
            # Execute the loading function
            result = task.load_function()
            
            # Record completion
            task.status = "completed"
            task.actual_duration = time.time() - start_time
            self.completed_tasks.append(task.task_id)
            
            # Notify completion
            if self.on_task_complete:
                self.on_task_complete(task, result)
            
            logger.info(f"Task completed: {task.task_id} in {task.actual_duration:.3f}s")
            
            return {
                "status": "completed",
                "task_id": task.task_id,
                "content_type": task.content_type,
                "duration": task.actual_duration,
                "result": result
            }
            
        except Exception as e:
            # Handle task failure
            task.status = "failed"
            task.retry_count += 1
            
            if task.retry_count < task.max_retries:
                # Retry after delay
                time.sleep(self.retry_delay * task.retry_count)
                return self._execute_task(task)
            else:
                # Task failed permanently
                task.actual_duration = time.time() - start_time
                
                if self.on_task_fail:
                    self.on_task_fail(task, e)
                
                logger.error(f"Task failed: {task.task_id} after {task.retry_count} retries")
                
                return {
                    "status": "failed",
                    "task_id": task.task_id,
                    "content_type": task.content_type,
                    "error": str(e),
                    "retry_count": task.retry_count
                }
    
    def show_skeleton(self, component_id: str, skeleton_type: str = "card",
                     placeholder_text: str = "Loading...", 
                     estimated_duration: float = 1.0) -> None:
        """
        Show skeleton UI for a component.
        
        Args:
            component_id: Component identifier
            skeleton_type: Type of skeleton to show
            placeholder_text: Text to display in skeleton
            estimated_duration: Estimated loading duration
        """
        skeleton = SkeletonState(
            component_id=component_id,
            skeleton_type=skeleton_type,
            placeholder_text=placeholder_text,
            estimated_duration=estimated_duration
        )
        
        self.skeletons[component_id] = skeleton
        
        # Start skeleton animation
        if skeleton.animation_style != "none":
            self._start_skeleton_animation(component_id)
        
        # Auto-hide skeleton after timeout
        timer = threading.Timer(
            estimated_duration + 2.0,  # Add buffer time
            self.hide_skeleton,
            args=[component_id]
        )
        timer.start()
        self.skeleton_animations[component_id] = timer
        
        # Notify skeleton show
        if self.on_skeleton_show:
            self.on_skeleton_show(component_id, skeleton)
        
        logger.debug(f"Showing skeleton: {component_id} ({skeleton_type})")
    
    def hide_skeleton(self, component_id: str) -> None:
        """
        Hide skeleton UI for a component.
        
        Args:
            component_id: Component identifier
        """
        if component_id in self.skeletons:
            skeleton = self.skeletons[component_id]
            skeleton.visible = False
            
            # Stop animation
            if component_id in self.skeleton_animations:
                self.skeleton_animations[component_id].cancel()
                del self.skeleton_animations[component_id]
            
            # Notify skeleton hide
            if self.on_skeleton_hide:
                self.on_skeleton_hide(component_id, skeleton)
            
            logger.debug(f"Hiding skeleton: {component_id}")
    
    def _start_skeleton_animation(self, component_id: str) -> None:
        """
        Start skeleton animation for a component.
        
        Args:
            component_id: Component identifier
        """
        def animate():
            if component_id in self.skeletons:
                skeleton = self.skeletons[component_id]
                if skeleton.visible:
                    # Simulate animation by updating state
                    skeleton.animation_style = "wave" if skeleton.animation_style == "pulse" else "pulse"
                    
                    # Continue animation
                    if skeleton.visible:
                        timer = threading.Timer(0.5, animate)
                        timer.start()
                        self.skeleton_animations[component_id] = timer
        
        animate()
    
    def prioritize_content(self, content_priorities: List[str]) -> Dict[str, int]:
        """
        Prioritize content loading based on importance.
        
        Args:
            content_priorities: List of content types in priority order
            
        Returns:
            Priority mapping
        """
        priority_map = {}
        for i, content_type in enumerate(content_priorities):
            # Assign priority (lower number = higher priority)
            priority_map[content_type] = i + 1
        
        logger.info(f"Content priorities set: {priority_map}")
        return priority_map
    
    def get_loading_status(self) -> Dict[str, Any]:
        """
        Get current loading status.
        
        Returns:
            Loading status information
        """
        return {
            "active_tasks": len(self.active_tasks),
            "pending_tasks": len([t for t in self.task_queue if t.status == "pending"]),
            "completed_tasks": len(self.completed_tasks),
            "failed_tasks": len([t for t in self.tasks.values() if t.status == "failed"]),
            "skeletons_visible": len([s for s in self.skeletons.values() if s.visible]),
            "queue_size": len(self.task_queue)
        }
    
    def start_loading(self) -> None:
        """Start the loading system."""
        if self.is_running:
            return
        
        self.is_running = True
        self.loading_thread = threading.Thread(target=self._loading_loop, daemon=True)
        self.loading_thread.start()
        
        logger.info("Progressive loading system started")
    
    def stop_loading(self) -> None:
        """Stop the loading system."""
        self.is_running = False
        
        # Cancel all skeleton animations
        for timer in self.skeleton_animations.values():
            timer.cancel()
        self.skeleton_animations.clear()
        
        # Shutdown executor
        self.executor.shutdown(wait=True)
        
        logger.info("Progressive loading system stopped")
    
    def _loading_loop(self) -> None:
        """Main loading loop."""
        while self.is_running:
            try:
                # Process task queue
                self._process_task_queue()
                
                # Clean up completed tasks
                self._cleanup_completed_tasks()
                
                # Sleep briefly
                time.sleep(0.1)
                
            except Exception as e:
                logger.error(f"Loading loop error: {e}")
                time.sleep(1.0)
    
    def _process_task_queue(self) -> None:
        """Process the task queue."""
        # Remove completed tasks from queue
        self.task_queue = [t for t in self.task_queue if t.status != "completed"]
        
        # Start new tasks if capacity allows
        active_count = len([f for f in self.active_tasks.values() if not f.done()])
        
        while (self.task_queue and 
               active_count < self.max_concurrent_loads and
               len(self.active_tasks) < self.max_concurrent_loads):
            
            task = self.task_queue.pop(0)
            
            # Check dependencies
            if task.dependencies and not all(dep in self.completed_tasks for dep in task.dependencies):
                # Re-add to queue if dependencies not met
                self.task_queue.append(task)
                continue
            
            # Submit task
            future = self.executor.submit(self._execute_task, task)
            self.active_tasks[task.task_id] = future
            active_count += 1
    
    def _cleanup_completed_tasks(self) -> None:
        """Clean up completed tasks."""
        completed_task_ids = []
        
        for task_id, future in self.active_tasks.items():
            if future.done():
                try:
                    result = future.result()
                    if result.get("status") == "completed":
                        self.completed_tasks.append(task_id)
                except:
                    pass  # Task failed
                
                completed_task_ids.append(task_id)
        
        # Remove completed tasks
        for task_id in completed_task_ids:
            if task_id in self.active_tasks:
                del self.active_tasks[task_id]
    
    def _record_performance(self, page_name: str, duration: float, results: Dict[str, Any]) -> None:
        """
        Record performance metrics.
        
        Args:
            page_name: Name of the page
            duration: Total loading duration
            results: Loading results
        """
        metrics = {
            "page": page_name,
            "duration": duration,
            "timestamp": time.time(),
            "completed_tasks": len([r for r in results.values() if r.get("status") == "completed"]),
            "failed_tasks": len([r for r in results.values() if r.get("status") == "failed"]),
            "task_breakdown": results
        }
        
        self.performance_history.append(metrics)
        self.loading_metrics[page_name].append(duration)
        
        # Keep only last 100 entries
        if len(self.performance_history) > 100:
            self.performance_history.pop(0)
        
        logger.info(f"Performance recorded: {page_name} - {duration:.3f}s")
    
    # Content loading functions
    def _load_dashboard_critical_data(self) -> Dict[str, Any]:
        """Load critical dashboard data."""
        # Simulate API call
        time.sleep(0.3)
        return {
            "user_stats": {"level": 5, "xp": 1250, "streak": 15},
            "today_habits": ["Exercise", "Meditation", "Reading"],
            "active_goals": ["Read 12 books", "Exercise 3x/week"]
        }
    
    def _load_dashboard_charts(self) -> Dict[str, Any]:
        """Load dashboard charts."""
        # Simulate chart data loading
        time.sleep(0.8)
        return {
            "habit_chart": {"labels": ["Mon", "Tue", "Wed"], "data": [80, 90, 85]},
            "mood_chart": {"labels": ["Mon", "Tue", "Wed"], "data": [7, 8, 6]}
        }
    
    def _load_dashboard_analytics(self) -> Dict[str, Any]:
        """Load dashboard analytics."""
        # Simulate analytics loading
        time.sleep(1.5)
        return {
            "insights": ["You're most productive on Tuesdays", "Habit completion rate: 85%"],
            "predictions": {"next_habit": "Exercise", "confidence": 0.8}
        }
    
    def _load_habits_list(self) -> Dict[str, Any]:
        """Load habits list."""
        time.sleep(0.3)
        return {
            "habits": [
                {"name": "Exercise", "streak": 15, "completed_today": True},
                {"name": "Meditation", "streak": 8, "completed_today": False}
            ]
        }
    
    def _load_habits_stats(self) -> Dict[str, Any]:
        """Load habits statistics."""
        time.sleep(0.8)
        return {
            "completion_rate": 0.85,
            "avg_streak": 12,
            "most_consistent": "Exercise"
        }


# Global progressive loader instance
_progressive_loader: Optional[ProgressiveLoader] = None


def get_progressive_loader() -> Optional[ProgressiveLoader]:
    """Get the global progressive loader instance."""
    return _progressive_loader


def initialize_progressive_loader(predictive_loader=None, lazy_loader=None) -> ProgressiveLoader:
    """Initialize and return a progressive loader instance."""
    global _progressive_loader
    _progressive_loader = ProgressiveLoader(predictive_loader, lazy_loader)
    return _progressive_loader


# Export
__all__ = [
    'ProgressiveLoader',
    'LoadingTask',
    'SkeletonState',
    'get_progressive_loader',
    'initialize_progressive_loader'
]