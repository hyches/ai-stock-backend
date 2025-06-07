from typing import Dict, List, Optional
from datetime import datetime
from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String, JSON, Index, UniqueConstraint
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_superuser = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    portfolios = relationship("Portfolio", back_populates="user", cascade="all, delete-orphan")
    strategies = relationship("Strategy", back_populates="user", cascade="all, delete-orphan")

class Portfolio(Base):
    __tablename__ = "portfolios"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    initial_balance = Column(Float, nullable=False)
    current_balance = Column(Float, nullable=False)
    risk_level = Column(String, nullable=False)  # low, medium, high
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="portfolios")
    positions = relationship("Position", back_populates="portfolio", cascade="all, delete-orphan")
    trades = relationship("Trade", back_populates="portfolio", cascade="all, delete-orphan")

    __table_args__ = (
        Index('idx_portfolio_user_created', 'user_id', 'created_at'),
    )

class Strategy(Base):
    __tablename__ = "strategies"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    name = Column(String, nullable=False)
    type = Column(String, nullable=False)  # trend_following, mean_reversion, breakout
    description = Column(String, nullable=True)
    parameters = Column(JSON, nullable=False)
    symbols = Column(JSON, nullable=False)  # List of symbols
    timeframe = Column(String, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="strategies")
    signals = relationship("Signal", back_populates="strategy", cascade="all, delete-orphan")
    backtests = relationship("BacktestResult", back_populates="strategy", cascade="all, delete-orphan")

    __table_args__ = (
        Index('idx_strategy_user_type', 'user_id', 'type'),
        Index('idx_strategy_active', 'is_active'),
    )

class Position(Base):
    __tablename__ = "positions"

    id = Column(Integer, primary_key=True, index=True)
    portfolio_id = Column(Integer, ForeignKey("portfolios.id", ondelete="CASCADE"), nullable=False)
    symbol = Column(String, nullable=False)
    quantity = Column(Float, nullable=False)
    average_price = Column(Float, nullable=False)
    current_price = Column(Float, nullable=False)
    unrealized_pnl = Column(Float, nullable=False)
    realized_pnl = Column(Float, nullable=False)
    stop_loss = Column(Float, nullable=True)
    take_profit = Column(Float, nullable=True)
    status = Column(String, nullable=False)  # open, closed
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    portfolio = relationship("Portfolio", back_populates="positions")
    trades = relationship("Trade", back_populates="position", cascade="all, delete-orphan")

    __table_args__ = (
        Index('idx_position_portfolio_status', 'portfolio_id', 'status'),
        Index('idx_position_symbol', 'symbol'),
    )

class Trade(Base):
    __tablename__ = "trades"

    id = Column(Integer, primary_key=True, index=True)
    portfolio_id = Column(Integer, ForeignKey("portfolios.id", ondelete="CASCADE"), nullable=False)
    position_id = Column(Integer, ForeignKey("positions.id", ondelete="SET NULL"), nullable=True)
    symbol = Column(String, nullable=False)
    quantity = Column(Float, nullable=False)
    price = Column(Float, nullable=False)
    side = Column(String, nullable=False)  # buy, sell
    pnl = Column(Float, nullable=False)
    fees = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    portfolio = relationship("Portfolio", back_populates="trades")
    position = relationship("Position", back_populates="trades")

    __table_args__ = (
        Index('idx_trade_portfolio_created', 'portfolio_id', 'created_at'),
        Index('idx_trade_symbol', 'symbol'),
    )

class Signal(Base):
    __tablename__ = "signals"

    id = Column(Integer, primary_key=True, index=True)
    strategy_id = Column(Integer, ForeignKey("strategies.id", ondelete="CASCADE"), nullable=False)
    symbol = Column(String, nullable=False)
    signal_type = Column(String, nullable=False)  # buy, sell
    confidence = Column(Float, nullable=False)
    metrics = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    strategy = relationship("Strategy", back_populates="signals")

    __table_args__ = (
        Index('idx_signal_strategy_created', 'strategy_id', 'created_at'),
        Index('idx_signal_symbol', 'symbol'),
    )

class BacktestResult(Base):
    __tablename__ = "backtest_results"

    id = Column(Integer, primary_key=True, index=True)
    strategy_id = Column(Integer, ForeignKey("strategies.id", ondelete="CASCADE"), nullable=False)
    symbol = Column(String, nullable=False)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    initial_balance = Column(Float, nullable=False)
    final_balance = Column(Float, nullable=False)
    total_return = Column(Float, nullable=False)
    sharpe_ratio = Column(Float, nullable=False)
    max_drawdown = Column(Float, nullable=False)
    win_rate = Column(Float, nullable=False)
    metrics = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    strategy = relationship("Strategy", back_populates="backtests")

    __table_args__ = (
        Index('idx_backtest_strategy_dates', 'strategy_id', 'start_date', 'end_date'),
        Index('idx_backtest_symbol', 'symbol'),
    )

class MarketData(Base):
    __tablename__ = "market_data"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, nullable=False)
    timestamp = Column(DateTime, nullable=False)
    open = Column(Float, nullable=False)
    high = Column(Float, nullable=False)
    low = Column(Float, nullable=False)
    close = Column(Float, nullable=False)
    volume = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    __table_args__ = (
        Index('idx_market_data_symbol_timestamp', 'symbol', 'timestamp', unique=True),
        Index('idx_market_data_timestamp', 'timestamp'),
    ) 