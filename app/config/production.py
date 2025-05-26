from typing import List
from pydantic_settings import BaseSettings
from functools import lru_cache
import os
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    """
    Settings class for configuring application parameters.
    Parameters:
        - PROJECT_NAME (str): Name of the project.
        - VERSION (str): Version of the project.
        - API_V1_STR (str): Base API URL path for version 1.
        - ENVIRONMENT (str): Application environment setting, default is 'production'.
        - SECRET_KEY (str): Secret key for security purposes; replace with a secure key in production.
        - ACCESS_TOKEN_EXPIRE_MINUTES (int): Duration before access token expires, set to 7 days (in minutes).
        - ALGORITHM (str): Algorithm used for token encoding.
        - BACKEND_CORS_ORIGINS (List[str]): List of allowed origins for CORS.
        - DATABASE_URL (str): URL connection string for the database.
        - RATE_LIMIT_PER_MINUTE (int): Number of allowed operations per minute for rate limiting.
        - ALPHA_VANTAGE_API_KEY (str): API key for Alpha Vantage service.
        - NEWS_API_KEY (str): API key for News service.
        - LOG_LEVEL (str): Logging level setting.
        - LOG_FORMAT (str): Format for logging messages.
        - ENABLE_METRICS (bool): Flag to enable metrics collection.
        - METRICS_PORT (int): Port on which metrics are exposed.
    Processing Logic:
        - Sensitive data like SECRET_KEY should be updated in production for security.
        - CORS origins list should include the correct domain in production.
        - ACCESS_TOKEN_EXPIRE_MINUTES should be set according to security policies.
        - Using environment variables is supported for configuration via an .env file.
    """
    PROJECT_NAME: str = "ML Trading Dashboard"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: str = "production"
    
    # Security
    SECRET_KEY: str = "your-secret-key-here"  # Change in production
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    ALGORITHM: str = "HS256"
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000",  # React dev server
        "http://localhost:8000",  # FastAPI dev server
        "https://your-production-domain.com"  # Add your production domain
    ]
    
    # Database
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/dbname"
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    
    # API Keys
    ALPHA_VANTAGE_API_KEY: str = ""
    NEWS_API_KEY: str = ""
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Monitoring
    ENABLE_METRICS: bool = True
    METRICS_PORT: int = 9090
    
    class Config:
        case_sensitive = True
        env_file = ".env"

@lru_cache()
def get_settings() -> Settings:
    return Settings()

settings = get_settings() 