from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
from datetime import datetime, date
from typing import Any
from sqlalchemy.orm import Session
from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.models.database import Portfolio, Stock
from app.models.trading import Strategy, Trade, Position, Signal
from app.schemas.trading import (
    StrategyCreate, Strategy as StrategySchema, StrategyUpdate,
    TradeCreate, Trade as TradeSchema, TradeUpdate,
    Portfolio as PortfolioSchema, PortfolioCreate,
    Position as PositionSchema, PositionCreate
)

router = APIRouter()

# Strategy endpoints
@router.post("/strategies/", response_model=StrategySchema, status_code=status.HTTP_201_CREATED)
def create_strategy(
    strategy_in: StrategyCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new trading strategy in the DB."""
    strategy = Strategy(
        user_id=current_user.id,
        name=strategy_in.name,
        type=strategy_in.type,
        description=strategy_in.description,
        parameters=strategy_in.parameters,
        is_active=strategy_in.is_active,
        symbols=["NIFTY", "BANKNIFTY"], # Default symbols
        timeframe="1h" # Default timeframe
    )
    db.add(strategy)
    db.commit()
    db.refresh(strategy)
    return strategy

@router.get("/strategies/", response_model=List[StrategySchema])
def get_strategies(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Fetch real strategies from the database."""
    return db.query(Strategy).filter(Strategy.user_id == current_user.id).all()

# Trade endpoints
@router.post("/trades/", response_model=TradeSchema, status_code=status.HTTP_201_CREATED)
def create_trade(
    trade_in: TradeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Log a real trade in the DB."""
    # Find active portfolio
    portfolio = db.query(Portfolio).filter(Portfolio.user_id == current_user.id).first()
    if not portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not found")
        
    trade = Trade(
        portfolio_id=portfolio.id,
        symbol=trade_in.symbol,
        quantity=trade_in.quantity,
        price=trade_in.price,
        side=trade_in.action,
        pnl=trade_in.pnl or 0.0,
        fees=0.1, # Dummy fee
        created_at=datetime.utcnow()
    )
    db.add(trade)
    db.commit()
    db.refresh(trade)
    return trade

@router.get("/trades/", response_model=List[TradeSchema])
def get_trades(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Fetch real trade history from the database."""
    return db.query(Trade).join(Portfolio).filter(Portfolio.user_id == current_user.id).all()

# Portfolio endpoints
@router.get("/portfolios/", response_model=List[PortfolioSchema])
def get_portfolios(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Fetch user portfolios from DB."""
    return db.query(Portfolio).filter(Portfolio.user_id == current_user.id).all()

# Position endpoints
@router.get("/positions/", response_model=List[PositionSchema])
def get_positions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Fetch real open positions from the database."""
    return db.query(Position).join(Portfolio).filter(
        Portfolio.user_id == current_user.id,
        Position.status == "open"
    ).all()

# ... existing endpoints ...

# Paper Trading Models
from pydantic import BaseModel

class PaperOrderRequest(BaseModel):
    symbol: str
    side: str  # BUY or SELL
    quantity: int
    order_type: str = "MARKET"

class GridBotRequest(BaseModel):
    symbol: str
    lower_range: float
    upper_range: float
    grid_count: int
    investment: float

# Paper Trading Endpoints
from app.services.paper_trading import paper_trading_service
from app.strategies.grid import GridStrategy, active_bots
import yfinance as yf

@router.get("/paper/portfolio")
async def get_paper_portfolio():
    """Get current paper trading portfolio and performance."""
    return await paper_trading_service.get_portfolio()

@router.post("/paper/orders")
async def place_paper_order(order: PaperOrderRequest):
    """Place a paper trade."""
    return await paper_trading_service.place_order(
        symbol=order.symbol.upper(),
        quantity=order.quantity,
        side=order.side,
        order_type=order.order_type
    )

@router.get("/paper/orders")
async def get_paper_orders():
    """Get paper trading history."""
    return paper_trading_service.trade_history

@router.post("/paper/reset")
async def reset_paper_balance(amount: float = 1000000.0):
    """Add funds to paper trading account."""
    return await paper_trading_service.reset_balance(amount)

@router.post("/strategies/grid")
async def start_grid_bot(config: GridBotRequest):
    """Start a new Grid Trading Bot."""
    bot_id = f"{config.symbol}_{datetime.now().timestamp()}"
    bot = GridStrategy(
        symbol=config.symbol.upper(),
        lower_range=config.lower_range,
        upper_range=config.upper_range,
        grid_count=config.grid_count,
        investment=config.investment
    )
    
    initial_state = await bot.initialize()
    active_bots[bot_id] = bot
    
    return {
        "bot_id": bot_id,
        "config": config.dict(),
        "state": initial_state
    }

@router.get("/market/option-chain/{symbol}")
async def get_option_chain(symbol: str):
    """
    Get option chain data for a symbol.
    Logic:
    1. If US Symbol (e.g. AAPL) -> Fetch from yfinance (Works).
    2. If Indian Symbol (e.g. NIFTY) ->
       - Fetch SPOT PRICE from yfinance (Works using proper mapping).
       - Fetch CHAIN from Zerodha (if configured).
       - If Zerodha not configured, return empty chain + warning.
    """
    try:
        # 1. Symbol Mapping for yfinance Spot Price
        # NIFTY -> ^NSEI
        # BANKNIFTY -> ^NSEBANK
        # RELIANCE -> RELIANCE.NS
        yf_symbol = symbol
        is_indian = False
        
        if symbol.upper() == "NIFTY":
            yf_symbol = "^NSEI"
            is_indian = True
        elif symbol.upper() == "BANKNIFTY":
            yf_symbol = "^NSEBANK"
            is_indian = True
        elif not symbol.endswith(".NS") and symbol.isupper() and not symbol.startswith("^"):
            # Heuristic: If it's just 'RELIANCE' assume Indian stock
            # But let's check if it exists in YF as is (US stock) or needs .NS
            # For now, simplistic heuristic:
            if symbol.upper() in ["AAPL", "GOOGL", "MSFT", "TSLA", "SPY"]:
                is_indian = False
            else:
                yf_symbol = f"{symbol}.NS"
                is_indian = True

        # 2. Fetch Spot Price (Fast Info)
        ticker = yf.Ticker(yf_symbol)
        try:
            # fast_info is faster than history
            spot_price = ticker.fast_info.last_price
            if spot_price is None:
                 # Fallback to history
                 hist = ticker.history(period="1d")
                 if not hist.empty:
                     spot_price = hist["Close"].iloc[-1]
        except Exception:
            spot_price = 0.0

        # 3. Fetch Option Chain
        calls = []
        puts = []
        expiry = ""
        expirations = []
        warning = None

        # STRATEGY: Try Zerodha first if Indian, else YFinance
        if is_indian:
            from app.core.config import settings
            if settings.ZERODHA_API_KEY:
                # Try Zerodha
                from app.services.zerodha_service import ZerodhaService
                zs = ZerodhaService()
                chain_data = await zs.get_option_chain(symbol)
                # Parse if valid (mocked for now in service as 'not implemented' fully)
                if chain_data.get("status") == "error":
                     warning = "Broker Error: " + chain_data.get("message", "Unknown")
                else:
                     warning = "Option Chain requires Broker Data (Coming Soon)"
            else:
                warning = "Connect Zerodha for Indian Option Chain"
        else:
            # US Stock -> Try yfinance
            try:
                expirations = ticker.options
                if expirations:
                    expiry = expirations[0]
                    chain = ticker.option_chain(expiry)
                    
                    def process_df(df, type_):
                        # Filter for near-the-money to reduce payload? 
                        # For now send all
                        return df[['strike', 'lastPrice', 'bid', 'ask', 'volume', 'openInterest', 'impliedVolatility']].fillna(0).to_dict('records')
                    
                    calls = process_df(chain.calls, 'call')
                    puts = process_df(chain.puts, 'put')
                else:
                    warning = "No options data found in yfinance"
            except Exception as e:
                warning = f"yfinance error: {str(e)}"

        return {
            "symbol": symbol,
            "spot_price": spot_price,
            "currency": "INR" if is_indian else "USD",
            "expiry": expiry,
            "all_expiries": expirations,
            "calls": calls,
            "puts": puts,
            "warning": warning
        }

    except Exception as e:
        print(f"Option Chain Logic Error: {e}")
        return {
            "symbol": symbol, 
            "error": str(e),
            "spot_price": 0,
            "calls": [], "puts": [] 
        } 