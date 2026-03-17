"""
Backend Configuration

Configuration settings for the FastAPI backend.
Includes database path, CORS settings, and environment variables.

Phase 13: Decoupled Architecture Migration
"""

from pathlib import Path
from typing import List
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Application
    app_name: str = "Veryfyn Tracking System API"
    app_version: str = "1.0.0"
    debug: bool = False
    
    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    
    # Database
    # Points to the existing SQLite database in tracking_app
    database_path: str = str(Path(__file__).parent.parent / "tracking.db")
    
    # CORS - Allow React dev server
    cors_origins: List[str] = [
        "http://localhost:5173",  # Vite default
        "http://localhost:5174",  # Vite alt
        "http://localhost:5175",  # Vite alt
        "http://localhost:3000",  # CRA default
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
        "http://127.0.0.1:5175",
        "http://127.0.0.1:3000",
    ]
    
    # API Key (simple authentication for personal app)
    api_key: str = ""  # Set via API_KEY environment variable
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Create settings instance
settings = Settings()
