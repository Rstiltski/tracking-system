"""
Routes Module

Handles page routing and navigation for the application.
Following the architecture rules, this provides centralized routing management
and prevents ghost imports by maintaining a single point of registration.
"""
from __future__ import annotations
import streamlit as st
from typing import Dict, Callable, Any
from app.auth.session import has_permission

# Define the route registry
_ROUTE_REGISTRY: Dict[str, Callable[[], Any]] = {}

def register_route(route_name: str, handler: Callable[[], Any], required_permission: str = "read") -> None:
    """
    Register a route with its handler function.
    
    Args:
        route_name: The name of the route (displayed in navigation)
        handler: The function to call when this route is accessed
        required_permission: The permission required to access this route
    """
    _ROUTE_REGISTRY[route_name] = {
        'handler': handler,
        'permission': required_permission
    }

def get_route_handler(route_name: str) -> Callable[[], Any] | None:
    """
    Get the handler function for a route.
    
    Args:
        route_name: The name of the route
        
    Returns:
        Handler function if route exists and user has permission, None otherwise
    """
    route_info = _ROUTE_REGISTRY.get(route_name)
    if not route_info:
        return None
    
    # Check if user has required permission
    if not has_permission(route_info['permission']):
        st.error(f"You don't have permission to access {route_name}")
        return None
    
    return route_info['handler']

def route_exists(route_name: str) -> bool:
    """
    Check if a route exists in the registry.
    
    Args:
        route_name: The name of the route
        
    Returns:
        True if route exists, False otherwise
    """
    return route_name in _ROUTE_REGISTRY

def get_all_routes() -> list[str]:
    """
    Get a list of all registered routes.
    
    Returns:
        List of route names
    """
    return list(_ROUTE_REGISTRY.keys())

def render_current_page() -> bool:
    """
    Render the current page based on session state.
    
    Returns:
        True if page was rendered successfully, False otherwise
    """
    current_page = st.session_state.get('current_page', 'Dashboard')
    handler = get_route_handler(current_page)
    
    if handler:
        handler()
        return True
    else:
        # If no handler is found, return False to indicate page not found
        return False

# Register default routes
def _register_default_routes() -> None:
    """Register default routes for the application."""
    # Import page handlers here to avoid circular imports
    from app.pages.dashboard import render_dashboard_page
    from app.pages.customers import render_customers_page
    from app.pages.jobs import render_jobs_page
    from app.pages.staff import render_staff_page
    from app.pages.schedule import render_schedule_page
    from app.pages.invoices import render_invoices_page
    from app.pages.reports import render_reports_page
    from app.pages.ai_assistant import render_ai_assistant_page
    from app.pages.admin_settings import render_admin_settings_page
    from app.pages.my_jobs import render_my_jobs_page
    from app.pages.time_tracking import render_time_tracking_page
    from app.pages.my_schedule import render_my_schedule_page
    from app.pages.customer_home import render_customer_home_page
    from app.pages.customer_jobs import render_customer_jobs_page
    from app.pages.customer_invoices import render_customer_invoices_page
    from app.pages.customer_messages import render_customer_messages_page
    
    # Register routes with appropriate permissions
    register_route("Dashboard", render_dashboard_page, "read")
    register_route("Customers", render_customers_page, "read")
    register_route("Jobs", render_jobs_page, "read")
    register_route("Staff", render_staff_page, "read")
    register_route("Schedule", render_schedule_page, "read")
    register_route("Invoices", render_invoices_page, "read")
    register_route("Reports", render_reports_page, "read")
    register_route("AI Assistant", render_ai_assistant_page, "read")
    register_route("Admin Settings", render_admin_settings_page, "admin")
    register_route("My Jobs", render_my_jobs_page, "read")
    register_route("Time Tracking", render_time_tracking_page, "read")
    register_route("My Schedule", render_my_schedule_page, "read")
    register_route("Customer Home", render_customer_home_page, "read")
    register_route("Customer Jobs", render_customer_jobs_page, "read")
    register_route("Customer Invoices", render_customer_invoices_page, "read")
    register_route("Customer Messages", render_customer_messages_page, "read")

# Initialize routes when module is imported
_register_default_routes()