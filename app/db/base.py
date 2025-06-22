"""
SQLAlchemy engine, session, and custom query class for the AI Stock Portfolio Platform Backend.

This module configures the engine and session factory with performance optimizations and provides a custom Query class for advanced ORM operations.
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# Create SQLAlchemy engine with optimized settings
engine = create_engine(
    settings.DATABASE_URL, 
    connect_args={"check_same_thread": False}
)

# Create session factory with optimized settings
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base class for models
Base = declarative_base() 