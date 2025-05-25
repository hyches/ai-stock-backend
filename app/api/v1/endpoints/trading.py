from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api import deps
from app.schemas.trading import (
    Strategy, StrategyCreate, StrategyUpdate,
    Signal, SignalCreate,
    Trade, TradeCreate, TradeUpdate,
    Portfolio, PortfolioCreate, PortfolioUpdate,
    Position, PositionCreate, PositionUpdate,
    BacktestResult, BacktestResultCreate
)
from app.services.trading import TradingService

router = APIRouter()

@router.post("/strategies/", response_model=Strategy)
def create_strategy(
    strategy: StrategyCreate,
    db: Session = Depends(deps.get_db)
):
    """
    Create a new trading strategy
    """
    trading_service = TradingService(db)
    return trading_service.create_strategy(strategy)

@router.get("/strategies/", response_model=List[Strategy])
def get_strategies(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(deps.get_db)
):
    """
    Get all trading strategies
    """
    trading_service = TradingService(db)
    return trading_service.get_strategies(skip=skip, limit=limit)

@router.get("/strategies/{strategy_id}", response_model=Strategy)
def get_strategy(
    strategy_id: int,
    db: Session = Depends(deps.get_db)
):
    """
    Get a specific trading strategy
    """
    trading_service = TradingService(db)
    strategy = trading_service.get_strategy(strategy_id)
    if not strategy:
        raise HTTPException(status_code=404, detail="Strategy not found")
    return strategy

@router.put("/strategies/{strategy_id}", response_model=Strategy)
def update_strategy(
    strategy_id: int,
    strategy: StrategyUpdate,
    db: Session = Depends(deps.get_db)
):
    """
    Update a trading strategy
    """
    trading_service = TradingService(db)
    updated_strategy = trading_service.update_strategy(strategy_id, strategy)
    if not updated_strategy:
        raise HTTPException(status_code=404, detail="Strategy not found")
    return updated_strategy

@router.delete("/strategies/{strategy_id}")
def delete_strategy(
    strategy_id: int,
    db: Session = Depends(deps.get_db)
):
    """
    Delete a trading strategy
    """
    trading_service = TradingService(db)
    if not trading_service.delete_strategy(strategy_id):
        raise HTTPException(status_code=404, detail="Strategy not found")
    return {"message": "Strategy deleted successfully"}

@router.post("/strategies/{strategy_id}/signals", response_model=List[Signal])
def generate_signals(
    strategy_id: int,
    symbol: str,
    db: Session = Depends(deps.get_db)
):
    """
    Generate trading signals for a strategy
    """
    trading_service = TradingService(db)
    signals = trading_service.generate_signals(strategy_id, symbol)
    return signals

@router.post("/trades/", response_model=Trade)
def create_trade(
    trade: TradeCreate,
    db: Session = Depends(deps.get_db)
):
    """
    Create a new trade
    """
    trading_service = TradingService(db)
    return trading_service.create_trade(trade)

@router.get("/trades/", response_model=List[Trade])
def get_trades(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(deps.get_db)
):
    """
    Get all trades
    """
    trading_service = TradingService(db)
    return trading_service.get_trades(skip=skip, limit=limit)

@router.get("/trades/{trade_id}", response_model=Trade)
def get_trade(
    trade_id: int,
    db: Session = Depends(deps.get_db)
):
    """
    Get a specific trade
    """
    trading_service = TradingService(db)
    trade = trading_service.get_trade(trade_id)
    if not trade:
        raise HTTPException(status_code=404, detail="Trade not found")
    return trade

@router.put("/trades/{trade_id}", response_model=Trade)
def update_trade(
    trade_id: int,
    trade: TradeUpdate,
    db: Session = Depends(deps.get_db)
):
    """
    Update a trade
    """
    trading_service = TradingService(db)
    updated_trade = trading_service.update_trade(trade_id, trade)
    if not updated_trade:
        raise HTTPException(status_code=404, detail="Trade not found")
    return updated_trade

@router.post("/portfolios/", response_model=Portfolio)
def create_portfolio(
    portfolio: PortfolioCreate,
    db: Session = Depends(deps.get_db)
):
    """
    Create a new portfolio
    """
    trading_service = TradingService(db)
    return trading_service.create_portfolio(portfolio)

@router.get("/portfolios/", response_model=List[Portfolio])
def get_portfolios(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(deps.get_db)
):
    """
    Get all portfolios
    """
    trading_service = TradingService(db)
    return trading_service.get_portfolios(skip=skip, limit=limit)

@router.get("/portfolios/{portfolio_id}", response_model=Portfolio)
def get_portfolio(
    portfolio_id: int,
    db: Session = Depends(deps.get_db)
):
    """
    Get a specific portfolio
    """
    trading_service = TradingService(db)
    portfolio = trading_service.get_portfolio(portfolio_id)
    if not portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not found")
    return portfolio

@router.put("/portfolios/{portfolio_id}", response_model=Portfolio)
def update_portfolio(
    portfolio_id: int,
    portfolio: PortfolioUpdate,
    db: Session = Depends(deps.get_db)
):
    """
    Update a portfolio
    """
    trading_service = TradingService(db)
    updated_portfolio = trading_service.update_portfolio(portfolio_id, portfolio)
    if not updated_portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not found")
    return updated_portfolio

@router.post("/portfolios/{portfolio_id}/positions", response_model=Position)
def create_position(
    portfolio_id: int,
    position: PositionCreate,
    db: Session = Depends(deps.get_db)
):
    """
    Create a new position in a portfolio
    """
    trading_service = TradingService(db)
    return trading_service.create_position(position)

@router.get("/portfolios/{portfolio_id}/positions", response_model=List[Position])
def get_positions(
    portfolio_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(deps.get_db)
):
    """
    Get all positions in a portfolio
    """
    trading_service = TradingService(db)
    return trading_service.get_positions(portfolio_id, skip=skip, limit=limit)

@router.get("/portfolios/{portfolio_id}/positions/{position_id}", response_model=Position)
def get_position(
    portfolio_id: int,
    position_id: int,
    db: Session = Depends(deps.get_db)
):
    """
    Get a specific position in a portfolio
    """
    trading_service = TradingService(db)
    position = trading_service.get_position(position_id)
    if not position or position.portfolio_id != portfolio_id:
        raise HTTPException(status_code=404, detail="Position not found")
    return position

@router.put("/portfolios/{portfolio_id}/positions/{position_id}", response_model=Position)
def update_position(
    portfolio_id: int,
    position_id: int,
    position: PositionUpdate,
    db: Session = Depends(deps.get_db)
):
    """
    Update a position in a portfolio
    """
    trading_service = TradingService(db)
    updated_position = trading_service.update_position(position_id, position)
    if not updated_position or updated_position.portfolio_id != portfolio_id:
        raise HTTPException(status_code=404, detail="Position not found")
    return updated_position

@router.post("/strategies/{strategy_id}/backtest", response_model=BacktestResult)
def run_backtest(
    strategy_id: int,
    backtest: BacktestResultCreate,
    db: Session = Depends(deps.get_db)
):
    """
    Run a backtest for a strategy
    """
    trading_service = TradingService(db)
    return trading_service.run_backtest(backtest)

@router.get("/strategies/{strategy_id}/backtest-results", response_model=List[BacktestResult])
def get_backtest_results(
    strategy_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(deps.get_db)
):
    """
    Get all backtest results for a strategy
    """
    trading_service = TradingService(db)
    return trading_service.get_backtest_results(strategy_id, skip=skip, limit=limit) 