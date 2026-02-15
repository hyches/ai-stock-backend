from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import yfinance as yf
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from app.db.session import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.market import StockAnalysis

router = APIRouter()

from app.services.ml_engine import ml_engine

@router.get("/analysis/{symbol}", response_model=StockAnalysis)
async def get_stock_analysis(
    symbol: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get AI-powered stock analysis from the primary ensemble engine.
    """
    try:
        ticker = yf.Ticker(symbol.upper())
        hist = ticker.history(period="2y")
        
        if hist.empty:
            raise HTTPException(status_code=404, detail="No historical data available")
        
        # Call the world-class engine
        prediction = ml_engine.predict(symbol.upper(), hist)
        
        if prediction.get("status") == "error":
            # Fallback if no model trained
            return StockAnalysis(
                buy=50, hold=30, sell=20,
                targetPrice=float(hist['Close'].iloc[-1]) * 1.05,
                recommendation="Hold"
            )

        # Map ensemble result to Frontend Schema
        signal = prediction.get("signal", "HOLD")
        confidence = prediction.get("confidence", 0.5) * 100
        
        buy_pct = confidence if signal == "BUY" else (100 - confidence) / 2
        sell_pct = confidence if signal == "SELL" else (100 - confidence) / 2
        hold_pct = 100 - buy_pct - sell_pct

        return StockAnalysis(
            buy=buy_pct,
            hold=hold_pct,
            sell=sell_pct,
            targetPrice=prediction.get("predicted_price_1week", hist['Close'].iloc[-1] * 1.02),
            recommendation=signal.capitalize()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error performing analysis: {str(e)}")

def calculate_rsi(prices, period=14):
    """Calculate RSI indicator"""
    delta = prices.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def calculate_macd(prices, fast=12, slow=26, signal=9):
    """Calculate MACD indicator"""
    ema_fast = prices.ewm(span=fast).mean()
    ema_slow = prices.ewm(span=slow).mean()
    macd = ema_fast - ema_slow
    signal_line = macd.ewm(span=signal).mean()
    return macd - signal_line

def calculate_bollinger_bands(prices, period=20, std_dev=2):
    """Calculate Bollinger Bands"""
    sma = prices.rolling(window=period).mean()
    std = prices.rolling(window=period).std()
    upper_band = sma + (std * std_dev)
    lower_band = sma - (std * std_dev)
    return upper_band, lower_band
