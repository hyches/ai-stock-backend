#!/usr/bin/env python3
"""
Create database tables script for AI Stock Trading Platform.
"""

import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.db.base_class import Base
from app.db.session import engine
from app.models.user import User
from app.models.database import Stock, Portfolio, PortfolioWeight, Report, Backup
from app.models.trading import Strategy, Position, Trade, Signal, BacktestResult, MarketData
from app.models.alert import Alert
from app.models.zerodha import ZerodhaToken, PaperTrade

def create_tables():
    """Create all database tables."""
    print("Creating database tables...")
    
    try:
        # Create all tables
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables created successfully!")
        
        # List created tables
        tables = Base.metadata.tables.keys()
        print(f"Created {len(tables)} tables:")
        for table in sorted(tables):
            print(f"  - {table}")
            
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        raise

if __name__ == "__main__":
    create_tables()
