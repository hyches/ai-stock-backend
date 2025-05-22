from pydantic_settings import BaseSettings
from functools import lru_cache
import os
from dotenv import load_dotenv

load_dotenv()

class ProductionSettings(BaseSettings):
    # API Settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "AI Stock Analysis"
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-here")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./app.db")
    
    # External APIs
    ALPHA_VANTAGE_API_KEY: str = os.getenv("ALPHA_VANTAGE_API_KEY")
    FINNHUB_API_KEY: str = os.getenv("FINNHUB_API_KEY")
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Monitoring
    ENABLE_METRICS: bool = True
    METRICS_PORT: int = 9090
    
    # CORS
    BACKEND_CORS_ORIGINS: list = ["https://your-frontend-domain.com"]
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    
    class Config:
        case_sensitive = True

@lru_cache()
def get_settings() -> ProductionSettings:
    return ProductionSettings()

settings = get_settings() 