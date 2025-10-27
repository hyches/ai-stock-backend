from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.trading import Strategy, Signal, Trade, Position, BacktestResult
from app.models.database import Portfolio
from app.schemas.trading import (
    StrategyCreate, StrategyUpdate,
    SignalCreate, TradeCreate, TradeUpdate,
    PortfolioCreate, PortfolioUpdate,
    PositionCreate, PositionUpdate,
    BacktestResultCreate
)
from app.core.config import settings
from app.utils.technical_analysis import TechnicalAnalysis
from app.utils.risk_management import RiskManager
from app.utils.portfolio_management import PortfolioManager
from app.utils.backtesting import Backtester
from app.core.cache import cache_response, cache

class TradingService:
    def __init__(self, db: Session):
        self.db = db
        self.technical_analysis = TechnicalAnalysis()
        self.risk_manager = RiskManager()
        self.portfolio_manager = PortfolioManager()
        self.backtester = Backtester()

    # Strategy Management
    @cache_response(ttl=300, key_prefix="strategy")
    async def get_strategy(self, strategy_id: int) -> Optional[Strategy]:
        """Get strategy by ID with caching"""
        return self.db.query(Strategy).filter(Strategy.id == strategy_id).first()

    @cache_response(ttl=60, key_prefix="strategies")
    async def get_strategies(self, skip: int = 0, limit: int = 100) -> List[Strategy]:
        """Get strategies with pagination and caching"""
        return self.db.query(Strategy).options(lazyload(Strategy.signals)).offset(skip).limit(limit).all()

    async def create_strategy(self, strategy: StrategyCreate) -> Strategy:
        """Create new strategy and invalidate cache"""
        db_strategy = Strategy(**strategy.dict())
        self.db.add(db_strategy)
        self.db.commit()
        self.db.refresh(db_strategy)
        await cache.clear_pattern("strategy:*")
        await cache.clear_pattern("strategies:*")
        return db_strategy

    async def update_strategy(self, strategy_id: int, strategy: StrategyUpdate) -> Optional[Strategy]:
        """Update strategy and invalidate cache"""
        db_strategy = await self.get_strategy(strategy_id)
        if not db_strategy:
            return None
        
        for field, value in strategy.dict(exclude_unset=True).items():
            setattr(db_strategy, field, value)
        
        self.db.commit()
        self.db.refresh(db_strategy)
        await cache.clear_pattern(f"strategy:{strategy_id}")
        await cache.clear_pattern("strategies:*")
        return db_strategy

    async def delete_strategy(self, strategy_id: int) -> bool:
        """Delete strategy and invalidate cache"""
        db_strategy = await self.get_strategy(strategy_id)
        if not db_strategy:
            return False
        
        self.db.delete(db_strategy)
        self.db.commit()
        await cache.clear_pattern(f"strategy:{strategy_id}")
        await cache.clear_pattern("strategies:*")
        return True

    # Signal Generation
    def generate_signals(self, strategy_id: int, symbol: str) -> List[Signal]:
        strategy = self.get_strategy(strategy_id)
        if not strategy:
            return []

        # Get technical analysis signals
        signals = self.technical_analysis.analyze(
            symbol=symbol,
            strategy_type=strategy.type,
            parameters=strategy.parameters
        )

        # Create signal records
        db_signals = []
        for signal in signals:
            db_signal = Signal(
                strategy_id=strategy_id,
                symbol=symbol,
                signal_type=signal["type"],
                confidence=signal["confidence"],
                metrics=signal["metrics"]
            )
            self.db.add(db_signal)
            db_signals.append(db_signal)

        self.db.commit()
        for signal in db_signals:
            self.db.refresh(signal)

        return db_signals

    # Trade Management
    @cache_response(ttl=60, key_prefix="trades")
    async def get_trades(self, skip: int = 0, limit: int = 100) -> List[Trade]:
        """Get trades with pagination and caching"""
        return self.db.query(Trade).options(lazyload(Trade.position)).offset(skip).limit(limit).all()

    async def create_trade(self, trade: TradeCreate) -> Trade:
        """Create new trade and invalidate cache"""
        db_trade = Trade(**trade.dict())
        self.db.add(db_trade)
        self.db.commit()
        self.db.refresh(db_trade)
        await cache.clear_pattern("trades:*")
        return db_trade

    def get_trade(self, trade_id: int) -> Optional[Trade]:
        return self.db.query(Trade).filter(Trade.id == trade_id).first()

    def update_trade(self, trade_id: int, trade: TradeUpdate) -> Optional[Trade]:
        db_trade = self.get_trade(trade_id)
        if db_trade:
            for key, value in trade.dict().items():
                setattr(db_trade, key, value)
            self.db.commit()
            self.db.refresh(db_trade)
        return db_trade

    # Portfolio Management
    @cache_response(ttl=300, key_prefix="portfolio")
    async def get_portfolio(self, portfolio_id: int) -> Optional[Portfolio]:
        """Get portfolio by ID with caching"""
        return self.db.query(Portfolio).filter(Portfolio.id == portfolio_id).first()

    @cache_response(ttl=60, key_prefix="portfolios")
    async def get_portfolios(self, skip: int = 0, limit: int = 100) -> List[Portfolio]:
        """Get portfolios with pagination and caching"""
        return self.db.query(Portfolio).options(lazyload(Portfolio.positions)).offset(skip).limit(limit).all()

    async def create_portfolio(self, portfolio: PortfolioCreate) -> Portfolio:
        """Create new portfolio and invalidate cache"""
        db_portfolio = Portfolio(**portfolio.dict())
        self.db.add(db_portfolio)
        self.db.commit()
        self.db.refresh(db_portfolio)
        await cache.clear_pattern("portfolio:*")
        await cache.clear_pattern("portfolios:*")
        return db_portfolio

    async def update_portfolio(self, portfolio_id: int, portfolio: PortfolioUpdate) -> Optional[Portfolio]:
        """Update portfolio and invalidate cache"""
        db_portfolio = await self.get_portfolio(portfolio_id)
        if not db_portfolio:
            return None
        
        for field, value in portfolio.dict(exclude_unset=True).items():
            setattr(db_portfolio, field, value)
        
        self.db.commit()
        self.db.refresh(db_portfolio)
        await cache.clear_pattern(f"portfolio:{portfolio_id}")
        await cache.clear_pattern("portfolios:*")
        return db_portfolio

    # Position Management
    @cache_response(ttl=60, key_prefix="positions")
    async def get_positions(self, portfolio_id: int, skip: int = 0, limit: int = 100) -> List[Position]:
        """Get positions with pagination and caching"""
        return self.db.query(Position).filter(
            Position.portfolio_id == portfolio_id
        ).offset(skip).limit(limit).all()

    async def create_position(self, position: PositionCreate) -> Position:
        """Create new position and invalidate cache"""
        db_position = Position(**position.dict())
        self.db.add(db_position)
        self.db.commit()
        self.db.refresh(db_position)
        await cache.clear_pattern(f"positions:{db_position.portfolio_id}:*")
        return db_position

    async def get_position(self, position_id: int) -> Optional[Position]:
        return self.db.query(Position).filter(Position.id == position_id).first()

    async def update_position(self, position_id: int, position: PositionUpdate) -> Optional[Position]:
        """Update position and invalidate cache"""
        db_position = self.db.query(Position).filter(Position.id == position_id).first()
        if not db_position:
            return None
        
        for field, value in position.dict(exclude_unset=True).items():
            setattr(db_position, field, value)
        
        self.db.commit()
        self.db.refresh(db_position)
        await cache.clear_pattern(f"positions:{db_position.portfolio_id}:*")
        return db_position

    # Backtesting
    @cache_response(ttl=300, key_prefix="backtest")
    async def get_backtest_results(self, strategy_id: int, skip: int = 0, limit: int = 100) -> List[BacktestResult]:
        """Get backtest results with pagination and caching"""
        return self.db.query(BacktestResult).filter(
            BacktestResult.strategy_id == strategy_id
        ).offset(skip).limit(limit).all()

    async def run_backtest(self, backtest: BacktestResultCreate) -> BacktestResult:
        """Run backtest and invalidate cache"""
        db_backtest = BacktestResult(**backtest.dict())
        self.db.add(db_backtest)
        self.db.commit()
        self.db.refresh(db_backtest)
        await cache.clear_pattern(f"backtest:{db_backtest.strategy_id}:*")
        return db_backtest

    # Count methods for pagination
    async def count_strategies(self) -> int:
        """Count total strategies"""
        return self.db.query(func.count(Strategy.id)).scalar()

    async def count_trades(self) -> int:
        """Count total trades"""
        return self.db.query(func.count(Trade.id)).scalar()

    async def count_portfolios(self) -> int:
        """Count total portfolios"""
        return self.db.query(func.count(Portfolio.id)).scalar()

    async def count_positions(self, portfolio_id: int) -> int:
        """Count positions in portfolio"""
        return self.db.query(func.count(Position.id)).filter(
            Position.portfolio_id == portfolio_id
        ).scalar()

    async def count_backtest_results(self, strategy_id: int) -> int:
        """Count backtest results for strategy"""
        return self.db.query(func.count(BacktestResult.id)).filter(
            BacktestResult.strategy_id == strategy_id
        ).scalar() 