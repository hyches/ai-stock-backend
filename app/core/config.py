from typing import Any, Dict, List, Optional, Union
from pydantic import BaseSettings, PostgresDsn, validator
import secrets
from pathlib import Path

class Settings(BaseSettings):
    # API settings
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    
    # Server settings
    SERVER_NAME: str = "Trading System"
    SERVER_HOST: str = "0.0.0.0"
    SERVER_PORT: int = 8000
    BACKEND_CORS_ORIGINS: List[str] = ["*"]
    
    # Database settings
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "trading_system"
    SQLALCHEMY_DATABASE_URI: Optional[PostgresDsn] = None

    @validator("SQLALCHEMY_DATABASE_URI", pre=True)
    def assemble_db_connection(cls, v: Optional[str], values: Dict[str, Any]) -> Any:
        if isinstance(v, str):
            return v
        return PostgresDsn.build(
            scheme="postgresql",
            user=values.get("POSTGRES_USER"),
            password=values.get("POSTGRES_PASSWORD"),
            host=values.get("POSTGRES_SERVER"),
            path=f"/{values.get('POSTGRES_DB') or ''}",
        )

    # Redis settings
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: Optional[str] = None

    # Trading settings
    DEFAULT_TIMEFRAME: str = "1d"
    DEFAULT_SYMBOLS: List[str] = ["AAPL", "MSFT", "GOOGL", "AMZN", "META"]
    MAX_POSITIONS: int = 10
    MAX_LEVERAGE: float = 3.0
    RISK_FREE_RATE: float = 0.02
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

    # Logging settings
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    LOG_FILE: Optional[str] = "trading_system.log"

    # Monitoring settings
    ENABLE_METRICS: bool = True
    METRICS_PORT: int = 9090
    SENTRY_DSN: Optional[str] = None

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

    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings() 