from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings(BaseSettings):
    """
    Settings for application configuration using the BaseSettings framework.
    Parameters:
        - API_V1_PREFIX (str): Defines the base URL prefix for API version 1 endpoints.
        - DEBUG (bool): Indicates whether to run the application in debug mode.
        - ENVIRONMENT (str): Specifies the environment the application is running in, e.g., development.
        - ALPHA_VANTAGE_API_KEY (Optional[str]): API key for accessing Alpha Vantage stock data services, if applicable.
        - YAHOO_FINANCE_API_KEY (Optional[str]): API key for accessing Yahoo Finance stock data services, if applicable.
        - DATABASE_URL (str): URL for the database connection.
        - SECRET_KEY (str): Key used for securing certain operations, should be changed in production.
        - ACCESS_TOKEN_EXPIRE_MINUTES (int): Duration for which an access token remains valid.
        - FRONTEND_URL (str): URL for the frontend application, used for CORS settings.
        - BACKEND_CORS_ORIGINS (list[str]): List of origins allowed to make cross-origin requests.
        - REDIS_URL (str): URL for connecting to the Redis server used for caching or other purposes.
    Processing Logic:
        - Retrieves environment variables from a '.env' file if present.
        - Ensures settings are case-sensitive.
        - Intended for use within a development context unless explicitly changed.
    """
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