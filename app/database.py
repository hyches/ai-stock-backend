"""
Database configuration and session management for the AI Stock Portfolio Platform Backend.

This module sets up the SQLAlchemy engine, session factory, and base class for models.
It provides utility functions for obtaining a database session and initializing the database schema.
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import Settings
import logging

logger = logging.getLogger(__name__)

# Create database engine
settings = Settings()
SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False}, 
    echo=settings.SQL_ECHO
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