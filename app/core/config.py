from typing import Any, Dict, List, Optional, Union
from pydantic_settings import BaseSettings
from pydantic import PostgresDsn, validator
import secrets
from pathlib import Path
from app.core.roles import UserRole

class Settings(BaseSettings):
    # API Settings
    API_V1_STR: str = "/api/v1"
    SERVER_NAME: str = "AI Trading System"
    SERVER_HOST: str = "0.0.0.0"
    SERVER_PORT: int = 8000
    DEBUG: bool = False
    ENVIRONMENT: str = "development"
    
    # Security
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    API_KEY: str = secrets.token_urlsafe(32)
    MAX_REQUEST_SIZE: int = 10 * 1024 * 1024  # 10MB
    SESSION_TTL: int = 3600  # 1 hour
    PASSWORD_MIN_LENGTH: int = 8
    PASSWORD_MAX_LENGTH: int = 64
    PASSWORD_REQUIRE_SPECIAL: bool = True
    PASSWORD_REQUIRE_NUMBERS: bool = True
    PASSWORD_REQUIRE_UPPERCASE: bool = True
    PASSWORD_REQUIRE_LOWERCASE: bool = True
    
    # Database
    DATABASE_URL: str = "sqlite:///./test.db"
    SQL_ECHO: bool = False
    
    # Redis
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: Optional[str] = None
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = ["*"]
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    LOG_FILE: Optional[Path] = None
    
    # Monitoring
    ENABLE_METRICS: bool = True
    PROMETHEUS_MULTIPROC_DIR: Optional[Path] = None
    
    # Trading Settings
    ZERODHA_API_KEY: Optional[str] = None
    ZERODHA_API_SECRET: Optional[str] = None
    TRADING_ENABLED: bool = False
    MAX_POSITION_SIZE: float = 100000.0
    RISK_FREE_RATE: float = 0.02
    
    # Cache Settings
    CACHE_TTL: int = 300  # 5 minutes
    CACHE_PREFIX: str = "trading"
    
    # Rate Limiting
    RATE_LIMIT_WINDOW: int = 60  # 1 minute
    RATE_LIMIT_MAX_REQUESTS: int = 100
    RATE_LIMIT_BY_IP: bool = True
    RATE_LIMIT_BY_USER: bool = True

    # Trading settings
    DEFAULT_TIMEFRAME: str = "1d"
    DEFAULT_SYMBOLS: List[str] = ["AAPL", "MSFT", "GOOGL", "AMZN", "META"]
    MAX_POSITIONS: int = 10
    MAX_LEVERAGE: float = 3.0
    DEFAULT_RISK_PER_TRADE: float = 0.02
    MAX_DRAWDOWN_LIMIT: float = 0.20
    POSITION_SIZE_LIMIT: float = 0.10

    # Exchange settings
    EXCHANGE_API_KEY: Optional[str] = None
    EXCHANGE_API_SECRET: Optional[str] = None
    EXCHANGE_TESTNET: bool = True

    # Data settings
    DATA_DIR: Path = Path("data")
    HISTORICAL_DATA_DAYS: int = 365
    CACHE_EXPIRY: int = 3600  # 1 hour

    # Strategy settings
    STRATEGY_PARAMETERS: Dict[str, Dict[str, Any]] = {
        "trend_following": {
            "fast_period": 12,
            "slow_period": 26,
            "signal_period": 9,
            "atr_period": 14,
            "atr_multiplier": 2.0,
            "risk_reward_ratio": 2.0
        },
        "mean_reversion": {
            "lookback_period": 20,
            "entry_std": 2.0,
            "exit_std": 0.5,
            "max_holding_period": 10
        },
        "breakout": {
            "lookback_period": 20,
            "breakout_threshold": 0.02,
            "stop_loss_atr": 2.0,
            "take_profit_atr": 4.0
        }
    }

    # Security validators
    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    @validator("DATABASE_URL", pre=True)
    def validate_database_url(cls, v: Optional[str]) -> Optional[str]:
        if not v:
            return v
        return v

    @validator("REDIS_PASSWORD", pre=True)
    def validate_redis_password(cls, v: Optional[str]) -> Optional[str]:
        if not v:
            return v
        return v

    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings() 