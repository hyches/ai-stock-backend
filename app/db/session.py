"""
Database session and engine management for the AI Stock Portfolio Platform Backend.

This module configures the SQLAlchemy engine, session factory, and provides utilities for session management, health checks, and query optimization.
"""
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

# Configure database engine with connection pooling
engine = create_engine(
    settings.DATABASE_URL,
    poolclass=QueuePool,
    pool_size=20,
    max_overflow=10,
    pool_timeout=30,
    pool_recycle=1800,  # Recycle connections after 30 minutes
    pool_pre_ping=True,  # Enable connection health checks
    echo=settings.SQL_ECHO
)

# Create session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

def get_db() -> Generator[Session, None, None]:
    """
    Get a database session with automatic cleanup.

    Yields:
        Session: SQLAlchemy session object.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Database health check
def check_db_health() -> bool:
    """
    Check database connection health.

    Returns:
        bool: True if the database connection is healthy, False otherwise.
    """
    try:
        db = SessionLocal()
        db.execute("SELECT 1")
        db.close()
        return True
    except Exception as e:
        logger.error(f"Database health check failed: {str(e)}")
        return False

# Query optimization settings
def optimize_query(query):
    """
    Apply query optimizations for large result sets.

    Args:
        query: SQLAlchemy query object.
    Returns:
        Query: Optimized SQLAlchemy query object.
    """
    return query.execution_options(
        stream_results=True,  # Stream large result sets
        max_row_buffer=1000,  # Buffer size for streaming
        yield_per=100  # Yield results in batches
    ) 