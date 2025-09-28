#!/usr/bin/env python3
"""
Database seeding script for AI Stock Trading Platform.

This script creates sample data for testing and development.
"""

import sys
import os
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.user import User
from app.models.database import Portfolio, Stock, PortfolioWeight
from app.models.trading import Strategy, Position, Trade, Signal
from app.core.security import get_password_hash
from datetime import datetime, timedelta
import random

def create_sample_users(db: Session):
    """Create sample users for testing."""
    print("Creating sample users...")
    
    users = []
    
    # Check if admin user exists
    admin_user = db.query(User).filter(User.email == "admin@trading.com").first()
    if not admin_user:
        admin_user = User(
            email="admin@trading.com",
            hashed_password=get_password_hash("admin123"),
            full_name="Admin User",
            is_active=True,
            is_superuser=True,
            permissions=["admin", "trader", "analyst"],
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.add(admin_user)
        users.append(admin_user)
    
    # Check if regular user exists
    regular_user = db.query(User).filter(User.email == "user@trading.com").first()
    if not regular_user:
        regular_user = User(
            email="user@trading.com",
            hashed_password=get_password_hash("user123"),
            full_name="Regular User",
            is_active=True,
            is_superuser=False,
            permissions=["trader", "analyst"],
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.add(regular_user)
        users.append(regular_user)
    
    # Check if demo user exists
    demo_user = db.query(User).filter(User.email == "demo@trading.com").first()
    if not demo_user:
        demo_user = User(
            email="demo@trading.com",
            hashed_password=get_password_hash("demo123"),
            full_name="Demo User",
            is_active=True,
            is_superuser=False,
            permissions=["trader"],
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.add(demo_user)
        users.append(demo_user)
    
    if users:
        db.commit()
        print(f"Created {len(users)} new sample users")
    else:
        print("All sample users already exist")
    
    # Return all users (existing + new)
    all_users = db.query(User).all()
    return all_users

def create_sample_stocks(db: Session):
    """Create sample stocks for testing."""
    print("Creating sample stocks...")
    
    sample_stocks = [
        {"symbol": "AAPL", "name": "Apple Inc.", "sector": "Technology", "industry": "Consumer Electronics", "market_cap": 3000000000000, "last_price": 179.50},
        {"symbol": "MSFT", "name": "Microsoft Corporation", "sector": "Technology", "industry": "Software", "market_cap": 2800000000000, "last_price": 408.75},
        {"symbol": "GOOGL", "name": "Alphabet Inc.", "sector": "Technology", "industry": "Internet", "market_cap": 1800000000000, "last_price": 176.45},
        {"symbol": "AMZN", "name": "Amazon.com Inc.", "sector": "Consumer Discretionary", "industry": "E-commerce", "market_cap": 1500000000000, "last_price": 182.30},
        {"symbol": "META", "name": "Meta Platforms Inc.", "sector": "Technology", "industry": "Social Media", "market_cap": 800000000000, "last_price": 350.20},
        {"symbol": "TSLA", "name": "Tesla Inc.", "sector": "Consumer Discretionary", "industry": "Automotive", "market_cap": 600000000000, "last_price": 178.80},
        {"symbol": "NVDA", "name": "NVIDIA Corporation", "sector": "Technology", "industry": "Semiconductors", "market_cap": 1200000000000, "last_price": 450.30},
        {"symbol": "JPM", "name": "JPMorgan Chase & Co.", "sector": "Financial Services", "industry": "Banking", "market_cap": 400000000000, "last_price": 150.25},
        {"symbol": "JNJ", "name": "Johnson & Johnson", "sector": "Healthcare", "industry": "Pharmaceuticals", "market_cap": 450000000000, "last_price": 165.80},
        {"symbol": "V", "name": "Visa Inc.", "sector": "Financial Services", "industry": "Payment Processing", "market_cap": 500000000000, "last_price": 280.50},
    ]
    
    stocks = []
    for stock_data in sample_stocks:
        # Check if stock already exists
        existing_stock = db.query(Stock).filter(Stock.symbol == stock_data["symbol"]).first()
        if not existing_stock:
            stock = Stock(
                symbol=stock_data["symbol"],
                name=stock_data["name"],
                sector=stock_data["sector"],
                industry=stock_data["industry"],
                market_cap=stock_data["market_cap"],
                last_price=stock_data["last_price"],
                last_updated=datetime.utcnow()
            )
            db.add(stock)
            stocks.append(stock)
        else:
            stocks.append(existing_stock)
    
    if stocks:
        db.commit()
        print(f"Created/retrieved {len(stocks)} sample stocks")
    else:
        print("All sample stocks already exist")
    
    return stocks

def create_sample_portfolios(db: Session, users, stocks):
    """Create sample portfolios for users."""
    print("Creating sample portfolios...")
    
    portfolios = []
    for user in users:
        # Create main portfolio
        portfolio = Portfolio(
            name=f"{user.full_name}'s Main Portfolio",
            user_id=user.id,
            created_at=datetime.utcnow(),
            last_updated=datetime.utcnow()
        )
        db.add(portfolio)
        portfolios.append(portfolio)
        
        # Create watchlist portfolio
        watchlist = Portfolio(
            name=f"{user.full_name}'s Watchlist",
            user_id=user.id,
            created_at=datetime.utcnow(),
            last_updated=datetime.utcnow()
        )
        db.add(watchlist)
        portfolios.append(watchlist)
    
    db.commit()
    print(f"Created {len(portfolios)} sample portfolios")
    return portfolios

def create_sample_portfolio_weights(db: Session, portfolios, stocks):
    """Create sample portfolio weights."""
    print("Creating sample portfolio weights...")
    
    # Only add weights to main portfolios (not watchlists)
    main_portfolios = [p for p in portfolios if "Main Portfolio" in p.name]
    
    for portfolio in main_portfolios:
        # Select 3-5 random stocks for each portfolio
        selected_stocks = random.sample(stocks, random.randint(3, 5))
        total_weight = 0
        
        for i, stock in enumerate(selected_stocks):
            # Last stock gets remaining weight to ensure total = 1.0
            if i == len(selected_stocks) - 1:
                weight = 1.0 - total_weight
            else:
                weight = random.uniform(0.1, 0.4)
                total_weight += weight
            
            portfolio_weight = PortfolioWeight(
                portfolio_id=portfolio.id,
                stock_id=stock.id,
                weight=weight,
                last_updated=datetime.utcnow()
            )
            db.add(portfolio_weight)
    
    db.commit()
    print("Created sample portfolio weights")

def create_sample_strategies(db: Session, users):
    """Create sample trading strategies."""
    print("Creating sample strategies...")
    
    strategies = []
    for user in users:
        # Trend following strategy
        trend_strategy = Strategy(
            user_id=user.id,
            name="Trend Following Strategy",
            type="trend_following",
            description="Follows price trends using moving averages",
            parameters={
                "fast_period": 12,
                "slow_period": 26,
                "signal_period": 9,
                "atr_period": 14,
                "atr_multiplier": 2.0,
                "risk_reward_ratio": 2.0
            },
            symbols=["AAPL", "MSFT", "GOOGL", "AMZN", "META"],
            timeframe="1d",
            is_active=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.add(trend_strategy)
        strategies.append(trend_strategy)
        
        # Mean reversion strategy
        mean_reversion_strategy = Strategy(
            user_id=user.id,
            name="Mean Reversion Strategy",
            type="mean_reversion",
            description="Trades against price extremes",
            parameters={
                "lookback_period": 20,
                "entry_std": 2.0,
                "exit_std": 0.5,
                "max_holding_period": 10
            },
            symbols=["TSLA", "NVDA", "JPM", "JNJ", "V"],
            timeframe="1d",
            is_active=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.add(mean_reversion_strategy)
        strategies.append(mean_reversion_strategy)
    
    db.commit()
    print(f"Created {len(strategies)} sample strategies")
    return strategies

def create_sample_trades(db: Session, portfolios, stocks):
    """Create sample trades."""
    print("Creating sample trades...")
    
    trades = []
    for portfolio in portfolios:
        if "Main Portfolio" in portfolio.name:
            # Create 5-10 random trades for each main portfolio
            num_trades = random.randint(5, 10)
            for _ in range(num_trades):
                stock = random.choice(stocks)
                side = random.choice(["buy", "sell"])
                quantity = random.randint(1, 100)
                price = random.uniform(50, 500)
                pnl = random.uniform(-1000, 1000)
                fees = random.uniform(1, 10)
                
                trade = Trade(
                    portfolio_id=portfolio.id,
                    symbol=stock.symbol,
                    quantity=quantity,
                    price=price,
                    side=side,
                    pnl=pnl,
                    fees=fees,
                    created_at=datetime.utcnow() - timedelta(days=random.randint(1, 30))
                )
                db.add(trade)
                trades.append(trade)
    
    db.commit()
    print(f"Created {len(trades)} sample trades")
    return trades

def create_sample_signals(db: Session, strategies, stocks):
    """Create sample trading signals."""
    print("Creating sample signals...")
    
    signals = []
    for strategy in strategies:
        # Create 3-5 signals for each strategy
        num_signals = random.randint(3, 5)
        for _ in range(num_signals):
            stock = random.choice(stocks)
            signal_type = random.choice(["buy", "sell"])
            confidence = random.uniform(0.6, 0.95)
            
            signal = Signal(
                strategy_id=strategy.id,
                symbol=stock.symbol,
                signal_type=signal_type,
                confidence=confidence,
                metrics={"is_executed": random.choice([True, False])},
                created_at=datetime.utcnow() - timedelta(hours=random.randint(1, 24))
            )
            db.add(signal)
            signals.append(signal)
    
    db.commit()
    print(f"Created {len(signals)} sample signals")
    return signals

def main():
    """Main seeding function."""
    print("Starting database seeding...")
    
    # Create database session
    db = SessionLocal()
    
    try:
        # Create sample data
        users = create_sample_users(db)
        stocks = create_sample_stocks(db)
        portfolios = create_sample_portfolios(db, users, stocks)
        create_sample_portfolio_weights(db, portfolios, stocks)
        strategies = create_sample_strategies(db, users)
        trades = create_sample_trades(db, portfolios, stocks)
        signals = create_sample_signals(db, strategies, stocks)
        
        print("\n✅ Database seeding completed successfully!")
        print(f"Created:")
        print(f"  - {len(users)} users")
        print(f"  - {len(stocks)} stocks")
        print(f"  - {len(portfolios)} portfolios")
        print(f"  - {len(strategies)} strategies")
        print(f"  - {len(trades)} trades")
        print(f"  - {len(signals)} signals")
        
        print("\n🔑 Login credentials:")
        print("  Admin: admin@trading.com / admin123")
        print("  User: user@trading.com / user123")
        print("  Demo: demo@trading.com / demo123")
        
    except Exception as e:
        print(f"❌ Error during seeding: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    main()
