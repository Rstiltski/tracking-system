import sys
import os

print(f"Python version: {sys.version}")
print(f"Current working directory: {os.getcwd()}")

modules_to_test = [
    'fastapi',
    'backend.config',
    'tracking_app.database',
    'backend.routes.habits',
]

for mod in modules_to_test:
    try:
        __import__(mod)
        print(f"SUCCESS: Imported {mod}")
    except ImportError as e:
        print(f"FAILURE: Failed to import {mod}: {e}")
    except Exception as e:
        print(f"ERROR: Unexpected error importing {mod}: {e}")
