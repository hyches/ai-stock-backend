from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
from app.models.trading import Strategy, Signal, Trade, Portfolio, Position, BacktestResult
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

class TradingService:
    def __init__(self, db: Session):
        self.db = db
        self.technical_analysis = TechnicalAnalysis()
        self.risk_manager = RiskManager()
        self.portfolio_manager = PortfolioManager()
        self.backtester = Backtester()

    # Strategy Management
    def create_strategy(self, strategy: StrategyCreate) -> Strategy:
        db_strategy = Strategy(**strategy.dict())
        self.db.add(db_strategy)
        self.db.commit()
        self.db.refresh(db_strategy)
        return db_strategy

    def get_strategy(self, strategy_id: int) -> Optional[Strategy]:
        return self.db.query(Strategy).filter(Strategy.id == strategy_id).first()

    def get_strategies(self, skip: int = 0, limit: int = 100) -> List[Strategy]:
        return self.db.query(Strategy).offset(skip).limit(limit).all()

    def update_strategy(self, strategy_id: int, strategy: StrategyUpdate) -> Optional[Strategy]:
        db_strategy = self.get_strategy(strategy_id)
        if db_strategy:
            for key, value in strategy.dict().items():
                setattr(db_strategy, key, value)
            self.db.commit()
            self.db.refresh(db_strategy)
        return db_strategy

    def delete_strategy(self, strategy_id: int) -> bool:
        db_strategy = self.get_strategy(strategy_id)
        if db_strategy:
            self.db.delete(db_strategy)
            self.db.commit()
            return True
        return False

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
    def create_trade(self, trade: TradeCreate) -> Trade:
        db_trade = Trade(**trade.dict())
        self.db.add(db_trade)
        self.db.commit()
        self.db.refresh(db_trade)
        return db_trade

    def get_trade(self, trade_id: int) -> Optional[Trade]:
        return self.db.query(Trade).filter(Trade.id == trade_id).first()

    def get_trades(self, skip: int = 0, limit: int = 100) -> List[Trade]:
        return self.db.query(Trade).offset(skip).limit(limit).all()

    def update_trade(self, trade_id: int, trade: TradeUpdate) -> Optional[Trade]:
        db_trade = self.get_trade(trade_id)
        if db_trade:
            for key, value in trade.dict().items():
                setattr(db_trade, key, value)
            self.db.commit()
            self.db.refresh(db_trade)
        return db_trade

    # Portfolio Management
    def create_portfolio(self, portfolio: PortfolioCreate) -> Portfolio:
        db_portfolio = Portfolio(**portfolio.dict())
        self.db.add(db_portfolio)
        self.db.commit()
        self.db.refresh(db_portfolio)
        return db_portfolio

    def get_portfolio(self, portfolio_id: int) -> Optional[Portfolio]:
        return self.db.query(Portfolio).filter(Portfolio.id == portfolio_id).first()

    def get_portfolios(self, skip: int = 0, limit: int = 100) -> List[Portfolio]:
        return self.db.query(Portfolio).offset(skip).limit(limit).all()

    def update_portfolio(self, portfolio_id: int, portfolio: PortfolioUpdate) -> Optional[Portfolio]:
        db_portfolio = self.get_portfolio(portfolio_id)
        if db_portfolio:
            for key, value in portfolio.dict().items():
                setattr(db_portfolio, key, value)
            self.db.commit()
            self.db.refresh(db_portfolio)
        return db_portfolio

    # Position Management
    def create_position(self, position: PositionCreate) -> Position:
        db_position = Position(**position.dict())
        self.db.add(db_position)
        self.db.commit()
        self.db.refresh(db_position)
        return db_position

    def get_position(self, position_id: int) -> Optional[Position]:
        return self.db.query(Position).filter(Position.id == position_id).first()

    def get_positions(self, portfolio_id: int, skip: int = 0, limit: int = 100) -> List[Position]:
        return self.db.query(Position).filter(Position.portfolio_id == portfolio_id).offset(skip).limit(limit).all()

    def update_position(self, position_id: int, position: PositionUpdate) -> Optional[Position]:
        db_position = self.get_position(position_id)
        if db_position:
            for key, value in position.dict().items():
                setattr(db_position, key, value)
            self.db.commit()
            self.db.refresh(db_position)
        return db_position

    # Backtesting
    def run_backtest(self, backtest: BacktestResultCreate) -> BacktestResult:
        # Run backtest
        results = self.backtester.run(
            strategy_id=backtest.strategy_id,
            symbol=backtest.symbol,
            start_date=backtest.start_date,
            end_date=backtest.end_date,
            initial_balance=backtest.initial_balance
        )

        # Create backtest result record
        db_backtest = BacktestResult(
            strategy_id=backtest.strategy_id,
            symbol=backtest.symbol,
            start_date=backtest.start_date,
            end_date=backtest.end_date,
            initial_balance=backtest.initial_balance,
            final_balance=results["final_balance"],
            total_return=results["total_return"],
            sharpe_ratio=results["sharpe_ratio"],
            max_drawdown=results["max_drawdown"],
            win_rate=results["win_rate"],
            metrics=results["metrics"]
        )

        self.db.add(db_backtest)
        self.db.commit()
        self.db.refresh(db_backtest)
        return db_backtest

    def get_backtest_results(self, strategy_id: int, skip: int = 0, limit: int = 100) -> List[BacktestResult]:
        return self.db.query(BacktestResult).filter(BacktestResult.strategy_id == strategy_id).offset(skip).limit(limit).all() 