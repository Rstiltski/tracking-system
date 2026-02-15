"""
Debug Test for Brain System

This test provides more detailed debugging information for the brain system.
"""
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent / "landscaping_new"
sys.path.insert(0, str(project_root))

def debug_brain_system():
    """Debug the brain system step by step."""
    print("=== Debugging Brain System ===\n")
    
    # Step 1: Import brain module
    print("1. Importing brain module...")
    try:
        import brain
        print("   ✓ Brain module imported successfully")
    except Exception as e:
        print(f"   ✗ Failed to import brain: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Step 2: Access brain instance
    print("\n2. Accessing brain instance...")
    try:
        from brain import brain_instance
        print("   ✓ Brain instance accessed successfully")
        print(f"   Brain ID: {brain_instance.id[:8]}...")
    except Exception as e:
        print(f"   ✗ Failed to access brain_instance: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Step 3: Create and register a tool
    print("\n3. Creating and registering a tool...")
    try:
        from brain.core.tool import HealthCheckTool
        health_tool = HealthCheckTool()
        print(f"   ✓ HealthCheckTool created: {health_tool.name}")
        
        brain_instance.register_tool(health_tool)
        print("   ✓ Tool registered successfully")
    except Exception as e:
        print(f"   ✗ Failed to create/register tool: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Step 4: Execute the tool
    print("\n4. Executing the tool...")
    try:
        result = brain_instance.execute_command("health_check", {})
        print(f"   Tool execution result: success={result.success}")
        print(f"   Result data: {result.data}")
        print(f"   Result error: {result.error_message}")
        
        if result.success:
            print("   ✓ Tool executed successfully")
            return True
        else:
            print("   ✗ Tool execution failed")
            return False
    except Exception as e:
        print(f"   ✗ Tool execution error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = debug_brain_system()
    print(f"\n=== Debug Result: {'SUCCESS' if success else 'FAILED'} ===")
    sys.exit(0 if success else 1)