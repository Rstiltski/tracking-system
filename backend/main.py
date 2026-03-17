"""
FastAPI Main Application

The main FastAPI application that provides REST API endpoints
for the decoupled architecture.

Phase 13: Decoupled Architecture Migration
Step 1: Extract Backend Logic into REST API

Run with:
    uvicorn backend.main:app --reload --port 8000
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from datetime import datetime
from typing import Dict, Any

from backend.config import settings


# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="REST API for Veryfyn Tracking System",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure CORS middleware
# Allows React frontend to communicate with FastAPI backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# Health Check Endpoint
# ============================================================================

@app.get("/health")
async def health_check() -> Dict[str, Any]:
    """
    Health check endpoint to verify the API is running.
    
    Returns:
        Dict with status, timestamp, and version info
    """
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": settings.app_version,
        "app_name": settings.app_name,
    }


# ============================================================================
# Root Endpoint
# ============================================================================

@app.get("/")
async def root() -> Dict[str, Any]:
    """
    Root endpoint with API information.
    
    Returns:
        Dict with welcome message and links to documentation
    """
    return {
        "message": f"Welcome to {settings.app_name}",
        "version": settings.app_version,
        "docs": "/docs",
        "health": "/health",
    }


# ============================================================================
# Database Test Endpoint
# ============================================================================

@app.get("/api/db/test")
async def db_test() -> Dict[str, Any]:
    """
    Database connection test endpoint.
    
    Returns:
        Dict with connection status and database info
    """
    try:
        # Use the get_db() function from tracking_app.database
        from tracking_app.database import get_db
        
        # Get database instance
        db = get_db()
        
        # Test database connection
        conn = db.get_connection()
        cursor = conn.cursor()
        
        # Try a simple query
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
        
        # Get database info
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        # Don't close the connection - it's managed by the class
        
        return {
            "status": "connected",
            "message": "SQLite database connected successfully",
            "tables": tables,
            "test_query": "SELECT 1" if result else None,
        }
    except Exception as e:
        return {
            "status": "disconnected",
            "message": str(e),
            "tables": [],
        }


# ============================================================================
# API Status Endpoint
# ============================================================================

@app.get("/api/status")
async def api_status() -> Dict[str, Any]:
    """
    API status endpoint - provides overall system status.
    
    Returns:
        Dict with API version and status
    """
    return {
        "status": "ok",
        "version": settings.app_version,
        "message": "Veryfyn API is running",
    }


# ============================================================================
# Error Handlers
# ============================================================================

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler for unhandled errors."""
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "message": str(exc),
            "path": str(request.url),
        },
    )


# ============================================================================
# Import existing tracking_app modules
# These will be wrapped with API endpoints in subsequent steps
# ============================================================================

# Import existing database and models from tracking_app
# NOTE: These are the EXISTING files - unchanged
# We will create API routes that call these functions
try:
    from tracking_app import database
    from tracking_app import models
    from tracking_app import storage
    EXISTING_MODULES_LOADED = True
except ImportError as e:
    # If tracking_app is not available, continue without it
    # Endpoints will return appropriate errors
    database = None
    models = None
    storage = None
    EXISTING_MODULES_LOADED = False


# ============================================================================
# API Routes
# ============================================================================

# Import and include API route modules
from backend.routes import habits
from backend.routes import tasks
from backend.routes import goals
from backend.routes import health
from backend.routes import time
from backend.routes import finances
from backend.routes import journal

app.include_router(habits.router)
app.include_router(tasks.router)
app.include_router(goals.router)
app.include_router(health.router)
app.include_router(time.router)
app.include_router(finances.router)
app.include_router(journal.router)


# ============================================================================
# Database Connection Endpoint (for testing)
# ============================================================================

@app.get("/api/db/test")
async def test_database_connection() -> Dict[str, Any]:
    """
    Test the database connection.
    
    Returns:
        Dict with connection status and database path
    """
    if not EXISTING_MODULES_LOADED:
        return {
            "status": "error",
            "message": "tracking_app modules not loaded",
        }
    
    try:
        # Test simple database query
        db = database.Database()
        with db.get_connection() as conn:
            cursor = conn.execute("SELECT 1")
            result = cursor.fetchone()
        
        return {
            "status": "connected",
            "database_path": settings.database_path,
            "query_result": result[0] if result else None,
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "database_path": settings.database_path,
        }


# ============================================================================
# TODO: Add API routes in subsequent steps
# ============================================================================
# 
# Step 2: Define API Contract
# - GET /api/habits
# - POST /api/habits
# - GET /api/tasks
# - POST /api/tasks
# - etc.
#
# Each route will wrap existing tracking_app functions
# ============================================================================
