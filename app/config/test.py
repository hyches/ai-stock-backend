from pydantic_settings import BaseSettings
from typing import Optional

class TestSettings(BaseSettings):
    """Test environment settings"""
    
    # Database
    DATABASE_URL: str = "sqlite:///./test.db"
    
    # Security
    SECRET_KEY: str = "test_secret_key"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    
    # API Keys
    NEWS_API_KEY: str = "test_news_api_key"
    ALPHA_VANTAGE_API_KEY: str = "test_alpha_vantage_api_key"
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    
    # File Upload
    MAX_UPLOAD_SIZE: int = 5 * 1024 * 1024  # 5MB
    ALLOWED_EXTENSIONS: set = {"pdf", "doc", "docx"}
    
    # Cache
    REDIS_URL: str = "redis://localhost:6379/1"
    CACHE_TTL: int = 300  # 5 minutes
    
    # Logging
    LOG_LEVEL: str = "DEBUG"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Testing
    TEST_USER_EMAIL: str = "test@example.com"
    TEST_USER_PASSWORD: str = "password123"
    TEST_USER_FULL_NAME: str = "Test User"
    
    class Config:
        env_file = ".env.test"
        case_sensitive = True

settings = TestSettings() 