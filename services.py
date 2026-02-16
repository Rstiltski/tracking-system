"""
Services Module - Compatibility Layer

This module provides compatibility for imports like 'import services'
by providing mock implementations.
"""

# Mock services module to satisfy imports
class MockService:
    def __init__(self, name):
        self.name = name

def get_service(service_name):
    """Get a mock service by name"""
    return MockService(service_name)

# Common services that might be imported
debug_console = MockService("debug_console")

# Additional services that may be imported
notifications = MockService("notifications")