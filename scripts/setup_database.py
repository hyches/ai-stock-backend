import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.db.base_class import Base
from app.models.trading import User, Portfolio, Strategy, Position, Trade, Signal, BacktestResult, MarketData

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_db() -> None:
    """Initialize database"""
    try:
        # Create database engine
        engine = create_engine(settings.SQLALCHEMY_DATABASE_URI)
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
        
        # Create session
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()
        
        # Create indexes
        logger.info("Creating database indexes...")
        
        # Market data indexes
        db.execute("""
            CREATE INDEX IF NOT EXISTS idx_market_data_symbol_timestamp 
            ON market_data (symbol, timestamp)
        """)
        
        # Trade indexes
        db.execute("""
            CREATE INDEX IF NOT EXISTS idx_trade_portfolio_id 
            ON trades (portfolio_id)
        """)
        db.execute("""
            CREATE INDEX IF NOT EXISTS idx_trade_position_id 
            ON trades (position_id)
        """)
        
        # Position indexes
        db.execute("""
            CREATE INDEX IF NOT EXISTS idx_position_portfolio_id 
            ON positions (portfolio_id)
        """)
        db.execute("""
            CREATE INDEX IF NOT EXISTS idx_position_symbol 
            ON positions (symbol)
        """)
        
        # Signal indexes
        db.execute("""
            CREATE INDEX IF NOT EXISTS idx_signal_strategy_id 
            ON signals (strategy_id)
        """)
        db.execute("""
            CREATE INDEX IF NOT EXISTS idx_signal_symbol 
            ON signals (symbol)
        """)
        
        # Backtest result indexes
        db.execute("""
            CREATE INDEX IF NOT EXISTS idx_backtest_strategy_id 
            ON backtest_results (strategy_id)
        """)
        
        # Commit changes
        db.commit()
        
        logger.info("Database initialized successfully")
        
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    logger.info("Creating initial database setup")
    init_db()
    logger.info("Database setup completed") 