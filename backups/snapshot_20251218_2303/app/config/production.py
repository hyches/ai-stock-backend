from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache
import os
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="allow"  # Allow extra fields from .env
    )
    
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
    
    # Redis and Celery
    REDIS_URL: str = "redis://localhost:6379/0"
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    
    # API Keys
    ALPHA_VANTAGE_API_KEY: str = "7XA85INCTINU5XMT"
    FINNHUB_API_KEY: str = ""
    FMP_API_KEY: str = ""
    YAHOO_FINANCE_API_KEY: str = ""
    NEWS_API_KEY: str = "3d037655056b4eb7bacde041d1c5bd12"
    
    # Config Flags
    DEBUG: bool = True
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    CACHE_ENABLED: bool = True
    RATE_LIMIT_ENABLED: bool = True
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Monitoring
    ENABLE_METRICS: bool = True
    METRICS_PORT: int = 9090

@lru_cache()
def get_settings() -> Settings:
    return Settings()

# settings = get_settings()  # Commented out to avoid module-level instantiation issues 