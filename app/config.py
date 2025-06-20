"""
Application configuration for the AI Stock Portfolio Platform Backend.

Defines the Settings class for environment variables, API keys, database, security, CORS, and Redis settings.
Provides a cached global settings instance for use throughout the application.
"""
from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings(BaseSettings):
    # API Settings
    API_V1_PREFIX: str = "/api/v1"
    DEBUG: bool = True
    ENVIRONMENT: str = "development"

    # Stock Data API Keys
    ALPHA_VANTAGE_API_KEY: Optional[str] = None
    YAHOO_FINANCE_API_KEY: Optional[str] = None

    # Database Settings (for future use)
    DATABASE_URL: str = "sqlite:///./stock_portfolio.db"

    # Security
    SECRET_KEY: str = "your-secret-key-here"  # Change in production
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # CORS Settings
    FRONTEND_URL: str = "https://preview--alpha-ai-portfolio-pro.lovable.app"
    BACKEND_CORS_ORIGINS: list[str] = ["http://localhost:3000"]

    # Redis Settings
    REDIS_URL: str = "redis://localhost:6379/0"

    class Config:
        env_file = ".env"
        case_sensitive = True

@lru_cache()
def get_settings() -> Settings:
    """
    Returns cached settings instance.
    """
    return Settings()

# Create a global settings instance
settings = get_settings() 