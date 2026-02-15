"""
Basic Test for Brain System

This test verifies that the brain system is properly initialized and can execute basic operations.
"""
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent / "landscaping_new"
sys.path.insert(0, str(project_root))

def test_brain_initialization():
    """Test that the brain system initializes correctly."""
    try:
        from brain import brain_instance
        print("✓ Brain instance imported successfully")
        
        # Check that basic attributes exist
        assert hasattr(brain_instance, 'tools'), "Brain should have tools attribute"
        assert hasattr(brain_instance, 'router'), "Brain should have router attribute"
        print("✓ Brain instance has required attributes")
        
        # Check that tools can be registered
        from brain.core.tool import HealthCheckTool
        health_tool = HealthCheckTool()
        brain_instance.register_tool(health_tool)
        print("✓ Tool registered successfully")
        
        # Check that the tool can be executed
        result = brain_instance.execute_command("health_check", {})
        assert result.success, "Health check should succeed"
        print("✓ Tool execution successful")
        
        print("\n✓ All brain system tests passed!")
        return True
        
    except Exception as e:
        print(f"\n✗ Brain system test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_database_connection():
    """Test that the database connection works."""
    try:
        from database.connection import get_conn
        conn = get_conn()
        cursor = conn.execute("SELECT 1 as test")
        result = cursor.fetchone()
        assert result['test'] == 1, "Database connection should work"
        print("✓ Database connection test passed")
        return True
    except Exception as e:
        print(f"✗ Database connection test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_basic_modules():
    """Test that basic modules can be imported."""
    try:
        from db import init_db
        print("✓ db module imported successfully")
        
        from brand import get_global_css
        css = get_global_css()
        assert "primary-color" in css, "CSS should contain brand colors"
        print("✓ brand module imported and working")
        
        print("✓ All basic module tests passed!")
        return True
    except Exception as e:
        print(f"✗ Basic module test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Running basic tests for the Landscaping Management System...\n")
    
    all_passed = True
    all_passed &= test_brain_initialization()
    print()
    all_passed &= test_database_connection()
    print()
    all_passed &= test_basic_modules()
    
    print(f"\nOverall result: {'✓ All tests passed!' if all_passed else '✗ Some tests failed'}")
    sys.exit(0 if all_passed else 1)