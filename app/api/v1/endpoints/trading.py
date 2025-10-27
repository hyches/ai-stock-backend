from typing import List, Optional, Dict, Any, Set
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse
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
from app.core.config import settings
from app.core.security import check_permissions, get_current_user
from app.utils.pagination import PaginatedResponse

router = APIRouter()

def create_response(data: Any = None, message: str = None, status_code: int = 200) -> Dict:
    """Create a standardized API response"""
    response = {"status": "success" if status_code < 400 else "error"}
    if data is not None:
        response["data"] = data
    if message is not None:
        response["message"] = message
    return response

@router.post("/strategies/", response_model=Dict)
async def create_strategy(
    strategy: StrategyCreate,
    db: Session = Depends(deps.get_db),
    user: Dict = Depends(check_permissions({"manage_strategies"}))
):
    """
    Create a new trading strategy
    """
    try:
        trading_service = TradingService(db)
        result = trading_service.create_strategy(strategy)
        return create_response(data=result, message="Strategy created successfully")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/strategies/", response_model=Dict)
async def get_strategies(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(deps.get_db),
    user: Dict = Depends(check_permissions({"view_strategies"}))
):
    """
    Get all trading strategies with pagination
    """
    try:
        trading_service = TradingService(db)
        total = trading_service.count_strategies()
        items = trading_service.get_strategies(skip=skip, limit=limit)
        
        pagination = PaginatedResponse(
            items=items,
            total=total,
            skip=skip,
            limit=limit
        )
        
        return create_response(data=pagination.dict())
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/strategies/{strategy_id}", response_model=Dict)
async def get_strategy(
    strategy_id: int,
    db: Session = Depends(deps.get_db),
    user: Dict = Depends(check_permissions({"view_strategies"}))
):
    """
    Get a specific trading strategy
    """
    try:
        trading_service = TradingService(db)
        strategy = trading_service.get_strategy(strategy_id)
        if not strategy:
            raise HTTPException(status_code=404, detail="Strategy not found")
        return create_response(data=strategy)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/strategies/{strategy_id}", response_model=Dict)
async def update_strategy(
    strategy_id: int,
    strategy: StrategyUpdate,
    db: Session = Depends(deps.get_db),
    user: Dict = Depends(check_permissions({"manage_strategies"}))
):
    """
    Update a trading strategy
    """
    try:
        trading_service = TradingService(db)
        updated_strategy = trading_service.update_strategy(strategy_id, strategy)
        if not updated_strategy:
            raise HTTPException(status_code=404, detail="Strategy not found")
        return create_response(data=updated_strategy, message="Strategy updated successfully")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/strategies/{strategy_id}", response_model=Dict)
async def delete_strategy(
    strategy_id: int,
    db: Session = Depends(deps.get_db),
    user: Dict = Depends(check_permissions({"manage_strategies"}))
):
    """
    Delete a trading strategy
    """
    try:
        trading_service = TradingService(db)
        if not trading_service.delete_strategy(strategy_id):
            raise HTTPException(status_code=404, detail="Strategy not found")
        return create_response(message="Strategy deleted successfully")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/strategies/{strategy_id}/signals", response_model=Dict)
async def generate_signals(
    strategy_id: int,
    symbol: str,
    db: Session = Depends(deps.get_db),
    user: Dict = Depends(check_permissions({"execute_trades"}))
):
    """
    Generate trading signals for a strategy
    """
    try:
        trading_service = TradingService(db)
        signals = trading_service.generate_signals(strategy_id, symbol)
        return create_response(data=signals, message="Signals generated successfully")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/trades/", response_model=Dict)
async def create_trade(
    trade: TradeCreate,
    db: Session = Depends(deps.get_db),
    user: Dict = Depends(check_permissions({"execute_trades"}))
):
    """
    Create a new trade
    """
    try:
        trading_service = TradingService(db)
        result = trading_service.create_trade(trade)
        return create_response(data=result, message="Trade created successfully")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/trades/", response_model=Dict)
async def get_trades(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(deps.get_db),
    user: Dict = Depends(check_permissions({"view_reports"}))
):
    """
    Get all trades with pagination
    """
    try:
        trading_service = TradingService(db)
        total = trading_service.count_trades()
        items = trading_service.get_trades(skip=skip, limit=limit)
        
        pagination = PaginatedResponse(
            items=items,
            total=total,
            skip=skip,
            limit=limit
        )
        
        return create_response(data=pagination.dict())
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/portfolios/", response_model=Dict)
async def create_portfolio(
    portfolio: PortfolioCreate,
    db: Session = Depends(deps.get_db),
    user: Dict = Depends(check_permissions({"manage_portfolios"}))
):
    """
    Create a new portfolio
    """
    try:
        trading_service = TradingService(db)
        result = trading_service.create_portfolio(portfolio)
        return create_response(data=result, message="Portfolio created successfully")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/portfolios/", response_model=Dict)
async def get_portfolios(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(deps.get_db),
    user: Dict = Depends(check_permissions({"view_portfolios"}))
):
    """
    Get all portfolios with pagination
    """
    try:
        trading_service = TradingService(db)
        total = trading_service.count_portfolios()
        items = trading_service.get_portfolios(skip=skip, limit=limit)
        
        pagination = PaginatedResponse(
            items=items,
            total=total,
            skip=skip,
            limit=limit
        )
        
        return create_response(data=pagination.dict())
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/portfolios/{portfolio_id}", response_model=Dict)
async def get_portfolio(
    portfolio_id: int,
    db: Session = Depends(deps.get_db),
    user: Dict = Depends(check_permissions({"view_portfolios"}))
):
    """
    Get a specific portfolio
    """
    try:
        trading_service = TradingService(db)
        portfolio = trading_service.get_portfolio(portfolio_id)
        if not portfolio:
            raise HTTPException(status_code=404, detail="Portfolio not found")
        return create_response(data=portfolio)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/portfolios/{portfolio_id}", response_model=Dict)
async def update_portfolio(
    portfolio_id: int,
    portfolio: PortfolioUpdate,
    db: Session = Depends(deps.get_db),
    user: Dict = Depends(check_permissions({"manage_portfolios"}))
):
    """
    Update a portfolio
    """
    try:
        trading_service = TradingService(db)
        updated_portfolio = trading_service.update_portfolio(portfolio_id, portfolio)
        if not updated_portfolio:
            raise HTTPException(status_code=404, detail="Portfolio not found")
        return create_response(data=updated_portfolio, message="Portfolio updated successfully")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/portfolios/{portfolio_id}/positions", response_model=Dict)
async def create_position(
    portfolio_id: int,
    position: PositionCreate,
    db: Session = Depends(deps.get_db),
    user: Dict = Depends(check_permissions({"execute_trades"}))
):
    """
    Create a new position in a portfolio
    """
    try:
        trading_service = TradingService(db)
        result = trading_service.create_position(position)
        return create_response(data=result, message="Position created successfully")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/portfolios/{portfolio_id}/positions", response_model=Dict)
async def get_positions(
    portfolio_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(deps.get_db),
    user: Dict = Depends(check_permissions({"view_portfolios"}))
):
    """
    Get all positions in a portfolio with pagination
    """
    try:
        trading_service = TradingService(db)
        total = trading_service.count_positions(portfolio_id)
        items = trading_service.get_positions(portfolio_id, skip=skip, limit=limit)
        
        pagination = PaginatedResponse(
            items=items,
            total=total,
            skip=skip,
            limit=limit
        )
        
        return create_response(data=pagination.dict())
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/portfolios/{portfolio_id}/positions/{position_id}", response_model=Dict)
async def get_position(
    portfolio_id: int,
    position_id: int,
    db: Session = Depends(deps.get_db),
    user: Dict = Depends(check_permissions({"view_portfolios"}))
):
    """
    Get a specific position in a portfolio
    """
    try:
        trading_service = TradingService(db)
        position = trading_service.get_position(position_id)
        if not position or position.portfolio_id != portfolio_id:
            raise HTTPException(status_code=404, detail="Position not found")
        return create_response(data=position)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/portfolios/{portfolio_id}/positions/{position_id}", response_model=Dict)
async def update_position(
    portfolio_id: int,
    position_id: int,
    position: PositionUpdate,
    db: Session = Depends(deps.get_db),
    user: Dict = Depends(check_permissions({"execute_trades"}))
):
    """
    Update a position in a portfolio
    """
    try:
        trading_service = TradingService(db)
        updated_position = trading_service.update_position(position_id, position)
        if not updated_position or updated_position.portfolio_id != portfolio_id:
            raise HTTPException(status_code=404, detail="Position not found")
        return create_response(data=updated_position, message="Position updated successfully")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/strategies/{strategy_id}/backtest", response_model=Dict)
async def run_backtest(
    strategy_id: int,
    backtest: BacktestResultCreate,
    db: Session = Depends(deps.get_db),
    user: Dict = Depends(check_permissions({"manage_strategies"}))
):
    """
    Run a backtest for a strategy
    """
    try:
        trading_service = TradingService(db)
        result = trading_service.run_backtest(backtest)
        return create_response(data=result, message="Backtest run successfully")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/strategies/{strategy_id}/backtest-results", response_model=Dict)
async def get_backtest_results(
    strategy_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(deps.get_db),
    user: Dict = Depends(check_permissions({"view_reports"}))
):
    """
    Get all backtest results for a strategy with pagination
    """
    try:
        trading_service = TradingService(db)
        total = trading_service.count_backtest_results(strategy_id)
        items = trading_service.get_backtest_results(strategy_id, skip=skip, limit=limit)
        
        pagination = PaginatedResponse(
            items=items,
            total=total,
            skip=skip,
            limit=limit
        )
        
        return create_response(data=pagination.dict())
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) 