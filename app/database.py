"""
Database configuration and session management for the AI Stock Portfolio Platform Backend.

This module sets up the SQLAlchemy engine, session factory, and base class for models.
It provides utility functions for obtaining a database session and initializing the database schema.
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import Settings
import logging

logger = logging.getLogger(__name__)

# Create database engine
settings = Settings()
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base class for models
Base = declarative_base()

def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Initialize database"""
    try:
        # Import all models here
        from app.models.database import User, Stock, Portfolio, PortfolioWeight, Report, Backup
        
        # Create tables
        Base.metadata.create_all(bind=engine)
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing database: {str(e)}")
        raise 