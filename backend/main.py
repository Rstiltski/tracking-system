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

# Configure CORS middleware FIRST - before any other middleware or routes
# This ensures OPTIONS preflight requests are handled properly
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["*", "Authorization", "Content-Type", "X-Requested-With"],
    expose_headers=["X-Request-ID", "Content-Length"],
    max_age=600,  # Cache preflight response for 10 minutes
)


# ============================================================================
# Explicit OPTIONS Handler for All Routes
# This guarantees OPTIONS requests are handled even if CORS middleware has issues
# ============================================================================

@app.options("/{full_path:path}")
async def preflight_handler(full_path: str, request: Request):
    """
    Global OPTIONS handler for CORS preflight requests.

    This endpoint catches all OPTIONS requests and returns the appropriate
    CORS headers without requiring a specific route to exist.
    """
    # Get the origin from the request headers
    origin = request.headers.get("origin", "http://localhost:5173")

    return JSONResponse(
        content="",
        status_code=200,
        headers={
            "Access-Control-Allow-Origin": origin,
            "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, PATCH, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type, Authorization, X-Requested-With",
            "Access-Control-Allow-Credentials": "true",
            "Access-Control-Max-Age": "600",
            "Vary": "Origin",
        }
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
from backend.routes import achievements  # Phase 14
from backend.routes import emotional_health  # Phase 14
from backend.routes import insights  # Phase 14
from backend.routes import diary  # Phase 14
from backend.routes import privacy  # Phase 14
from backend.routes import notifications  # Phase 14
from backend.routes import challenges  # Phase 14
from backend.routes import friends  # Phase 14
from backend.routes import experiments  # Phase 14

app.include_router(habits.router)
app.include_router(tasks.router)
app.include_router(goals.router)
app.include_router(health.router)
app.include_router(time.router)
app.include_router(finances.router)
app.include_router(journal.router)
app.include_router(achievements.router)  # Phase 14
app.include_router(emotional_health.router)  # Phase 14
app.include_router(insights.router)  # Phase 14
app.include_router(diary.router)  # Phase 14
app.include_router(privacy.router)  # Phase 14
app.include_router(notifications.router)  # Phase 14
app.include_router(challenges.router)  # Phase 14
app.include_router(friends.router)  # Phase 14
app.include_router(experiments.router)  # Phase 14


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
