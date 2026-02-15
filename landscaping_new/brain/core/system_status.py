"""
System Status Monitor for Brain System

Monitors the health and status of the brain system and related components.
"""
from __future__ import annotations
import logging
import psutil
import time
from datetime import datetime
from typing import Dict, Any, List
from dataclasses import dataclass

# Initialize logger
logger = logging.getLogger(__name__)

@dataclass
class ComponentStatus:
    """Represents the status of a system component."""
    name: str
    status: str  # 'healthy', 'warning', 'error', 'unknown'
    message: str
    timestamp: datetime
    details: Dict[str, Any] = None

class SystemStatusMonitor:
    """
    Monitors the health and status of the brain system and related components.
    
    Tracks various system metrics and component health to ensure the brain system
    operates reliably.
    """
    
    def __init__(self):
        self.start_time = time.time()
        self.components: Dict[str, ComponentStatus] = {}
        logger.info("SystemStatusMonitor initialized")
    
    def check_system_health(self) -> Dict[str, Any]:
        """
        Perform a comprehensive system health check.
        
        Returns:
            Dictionary containing system health information
        """
        health_info = {
            'timestamp': datetime.now().isoformat(),
            'uptime_seconds': time.time() - self.start_time,
            'cpu_percent': psutil.cpu_percent(interval=1),
            'memory_percent': psutil.virtual_memory().percent,
            'disk_percent': psutil.disk_usage('/').percent,
            'components': {},
            'overall_status': 'healthy'
        }
        
        # Check individual components
        component_statuses = self.check_component_health()
        health_info['components'] = {name: {
            'status': status.status,
            'message': status.message,
            'timestamp': status.timestamp.isoformat(),
            'details': status.details
        } for name, status in component_statuses.items()}
        
        # Determine overall status based on components
        for status in component_statuses.values():
            if status.status == 'error':
                health_info['overall_status'] = 'error'
                break
            elif status.status == 'warning' and health_info['overall_status'] != 'error':
                health_info['overall_status'] = 'warning'
        
        return health_info
    
    def check_component_health(self) -> Dict[str, ComponentStatus]:
        """
        Check the health of individual system components.
        
        Returns:
            Dictionary mapping component names to their status
        """
        # Check database connection
        db_status = self._check_database_health()
        self.components['database'] = db_status
        
        # Check memory usage
        memory_status = self._check_memory_health()
        self.components['memory'] = memory_status
        
        # Check disk space
        disk_status = self._check_disk_health()
        self.components['disk'] = disk_status
        
        # Check CPU usage
        cpu_status = self._check_cpu_health()
        self.components['cpu'] = cpu_status
        
        return self.components
    
    def _check_database_health(self) -> ComponentStatus:
        """Check database connection health."""
        try:
            # Try to connect to the database
            from database.connection import get_conn
            conn = get_conn()
            cursor = conn.execute("SELECT 1 as test")
            result = cursor.fetchone()
            conn.close()
            
            if result and result['test'] == 1:
                return ComponentStatus(
                    name='database',
                    status='healthy',
                    message='Database connection successful',
                    timestamp=datetime.now(),
                    details={'connection_successful': True}
                )
            else:
                return ComponentStatus(
                    name='database',
                    status='error',
                    message='Database connection test failed',
                    timestamp=datetime.now(),
                    details={'connection_successful': False}
                )
        except Exception as e:
            return ComponentStatus(
                name='database',
                status='error',
                message=f'Database connection failed: {str(e)}',
                timestamp=datetime.now(),
                details={'error': str(e)}
            )
    
    def _check_memory_health(self) -> ComponentStatus:
        """Check memory usage health."""
        memory = psutil.virtual_memory()
        usage_percent = memory.percent
        
        if usage_percent > 90:
            status = 'error'
            message = f'High memory usage: {usage_percent}%'
        elif usage_percent > 75:
            status = 'warning'
            message = f'Elevated memory usage: {usage_percent}%'
        else:
            status = 'healthy'
            message = f'Memory usage normal: {usage_percent}%'
        
        return ComponentStatus(
            name='memory',
            status=status,
            message=message,
            timestamp=datetime.now(),
            details={
                'usage_percent': usage_percent,
                'available_gb': round(memory.available / (1024**3), 2),
                'total_gb': round(memory.total / (1024**3), 2)
            }
        )
    
    def _check_disk_health(self) -> ComponentStatus:
        """Check disk space health."""
        disk = psutil.disk_usage('/')
        usage_percent = disk.percent
        
        if usage_percent > 95:
            status = 'error'
            message = f'Critical disk space: {usage_percent}% used'
        elif usage_percent > 85:
            status = 'warning'
            message = f'Low disk space: {usage_percent}% used'
        else:
            status = 'healthy'
            message = f'Disk space normal: {usage_percent}% used'
        
        return ComponentStatus(
            name='disk',
            status=status,
            message=message,
            timestamp=datetime.now(),
            details={
                'usage_percent': usage_percent,
                'free_gb': round(disk.free / (1024**3), 2),
                'total_gb': round(disk.total / (1024**3), 2)
            }
        )
    
    def _check_cpu_health(self) -> ComponentStatus:
        """Check CPU usage health."""
        cpu_percent = psutil.cpu_percent(interval=1)
        
        if cpu_percent > 95:
            status = 'error'
            message = f'Critical CPU usage: {cpu_percent}%'
        elif cpu_percent > 80:
            status = 'warning'
            message = f'High CPU usage: {cpu_percent}%'
        else:
            status = 'healthy'
            message = f'CPU usage normal: {cpu_percent}%'
        
        return ComponentStatus(
            name='cpu',
            status=status,
            message=message,
            timestamp=datetime.now(),
            details={'usage_percent': cpu_percent}
        )
    
    def get_component_status(self, component_name: str) -> ComponentStatus:
        """
        Get the status of a specific component.
        
        Args:
            component_name: Name of the component to check
            
        Returns:
            ComponentStatus for the specified component
        """
        if component_name in self.components:
            return self.components[component_name]
        
        # If component hasn't been checked yet, check it now
        if component_name == 'database':
            return self._check_database_health()
        elif component_name == 'memory':
            return self._check_memory_health()
        elif component_name == 'disk':
            return self._check_disk_health()
        elif component_name == 'cpu':
            return self._check_cpu_health()
        else:
            return ComponentStatus(
                name=component_name,
                status='unknown',
                message=f'Component {component_name} not recognized',
                timestamp=datetime.now()
            )
    
    def get_overall_status(self) -> str:
        """
        Get the overall system status.
        
        Returns:
            Overall status string ('healthy', 'warning', 'error', 'unknown')
        """
        if not self.components:
            return 'unknown'
        
        statuses = [comp.status for comp in self.components.values()]
        
        if 'error' in statuses:
            return 'error'
        elif 'warning' in statuses:
            return 'warning'
        elif all(status == 'healthy' for status in statuses):
            return 'healthy'
        else:
            return 'unknown'
    
    def refresh_status(self) -> Dict[str, Any]:
        """
        Refresh the status of all components and return health info.
        
        Returns:
            Dictionary containing refreshed system health information
        """
        return self.check_system_health()