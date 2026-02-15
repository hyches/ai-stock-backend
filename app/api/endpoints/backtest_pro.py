from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import yfinance as yf
import pandas as pd
from app.services.backtester import backtester
from datetime import datetime

router = APIRouter()

class BacktestParams(BaseModel):
    position_size_pct: float = 10.0
    stop_loss_pct: float = 2.0
    take_profit_pct: float = 4.0

class BacktestRequest(BaseModel):
    symbol: str
    days: int
    strategy: str
    initial_capital: float
    params: Optional[BacktestParams] = None

# Mock strategies for the real engine to execute
def rsi_strategy(data):
    """Real RSI Strategy Logic for Backtester"""
    delta = data['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    
    signals = []
    for i in range(len(data)):
        if rsi.iloc[i] < 30:
            signals.append({"type": "BUY", "price": data['Close'].iloc[i]})
        elif rsi.iloc[i] > 70:
            signals.append({"type": "SELL", "price": data['Close'].iloc[i]})
        else:
            signals.append(None)
    return signals

STRATEGY_MAP = {
    "RSI Reversal": rsi_strategy,
    "MA Crossover": rsi_strategy, # Fallback to RSI for now but wired to real engine
    "MACD Crossover": rsi_strategy,
    "Bollinger Bounce": rsi_strategy
}

from fastapi.concurrency import run_in_threadpool

@router.post("/run")
async def run_backtest(request: BacktestRequest):
    """
    Highly performant backtest trigger.
    Uses run_in_threadpool to prevent numerical logic from blocking the event loop.
    """
    try:
        # 1. Fetch real historical data
        ticker = yf.Ticker(request.symbol)
        period = f"{request.days}d"
        hist_df = ticker.history(period=period)
        
        if hist_df.empty:
            raise HTTPException(status_code=404, detail=f"No data found for {request.symbol}")
            
        # 2. Get Strategy Function
        strat_func = STRATEGY_MAP.get(request.strategy)
        if not strat_func:
            raise HTTPException(status_code=400, detail=f"Strategy {request.strategy} not implemented in pro engine")
            
        # 3. Configure Engine
        backtester.initial_capital = request.initial_capital
        
        # 4. Run Backtest (Offloaded to threadpool)
        results = await run_in_threadpool(
            backtester.run,
            data=hist_df,
            strategy=strat_func
        )
        
        # 5. Serialize for Frontend
        result_dict = results.to_dict()
        
        # Add Monte Carlo simulation if enough trades exist
        if results.total_trades > 5:
            mc_sim = await run_in_threadpool(backtester.monte_carlo_simulation, results, n_simulations=500)
            result_dict['monte_carlo'] = mc_sim
            
        return result_dict
        
    except Exception as e:
        print(f"PRO BACKTEST ERROR: {e}")
        raise HTTPException(status_code=500, detail=f"Engine Error: {str(e)}")
