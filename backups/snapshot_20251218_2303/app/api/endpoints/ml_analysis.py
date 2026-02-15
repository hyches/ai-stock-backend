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

@router.get("/analysis/{symbol}", response_model=StockAnalysis)
async def get_stock_analysis(
    symbol: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get AI-powered stock analysis
    """
    try:
        ticker = yf.Ticker(symbol.upper())
        
        # Get historical data for analysis
        hist = ticker.history(period="2y")
        
        if hist.empty:
            raise HTTPException(status_code=404, detail="No historical data available")
        
        # Calculate technical indicators
        df = hist.copy()
        df['SMA_20'] = df['Close'].rolling(window=20).mean()
        df['SMA_50'] = df['Close'].rolling(window=50).mean()
        df['RSI'] = calculate_rsi(df['Close'])
        df['MACD'] = calculate_macd(df['Close'])
        df['BB_Upper'], df['BB_Lower'] = calculate_bollinger_bands(df['Close'])
        
        # Calculate price change
        df['Price_Change'] = df['Close'].pct_change()
        df['Volume_Change'] = df['Volume'].pct_change()
        
        # Create features for ML model
        features = ['SMA_20', 'SMA_50', 'RSI', 'MACD', 'BB_Upper', 'BB_Lower', 'Price_Change', 'Volume_Change']
        df_features = df[features].dropna()
        
        # Create target variable (1 if price goes up next day, 0 if down)
        df_features['Target'] = (df_features['Price_Change'].shift(-1) > 0).astype(int)
        df_features = df_features.dropna()
        
        if len(df_features) < 100:
            # Not enough data for reliable analysis
            return StockAnalysis(
                buy=50,
                hold=30,
                sell=20,
                targetPrice=float(df['Close'].iloc[-1]) * 1.1,
                recommendation="Hold"
            )
        
        # Prepare features and target
        X = df_features[features]
        y = df_features['Target']
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Train model
        model = RandomForestClassifier(n_estimators=100, random_state=42)
        model.fit(X_train, y_train)
        
        # Get predictions
        y_pred = model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        
        # Get feature importance
        feature_importance = model.feature_importances_
        
        # Get latest features for prediction
        latest_features = X.iloc[-1:].values
        
        # Predict next day direction
        prediction = model.predict(latest_features)[0]
        probability = model.predict_proba(latest_features)[0]
        
        # Calculate target price based on analysis
        current_price = float(df['Close'].iloc[-1])
        
        # Simple target price calculation based on technical indicators
        sma_20 = df['SMA_20'].iloc[-1]
        sma_50 = df['SMA_50'].iloc[-1]
        rsi = df['RSI'].iloc[-1]
        
        target_multiplier = 1.0
        
        if sma_20 > sma_50:  # Uptrend
            target_multiplier += 0.1
        if rsi < 30:  # Oversold
            target_multiplier += 0.05
        elif rsi > 70:  # Overbought
            target_multiplier -= 0.05
            
        target_price = current_price * target_multiplier
        
        # Determine recommendation
        if prediction == 1 and probability[1] > 0.6:
            recommendation = "Buy"
            buy_pct = 70
            hold_pct = 20
            sell_pct = 10
        elif prediction == 0 and probability[0] > 0.6:
            recommendation = "Sell"
            buy_pct = 10
            hold_pct = 20
            sell_pct = 70
        else:
            recommendation = "Hold"
            buy_pct = 30
            hold_pct = 50
            sell_pct = 20
        
        return StockAnalysis(
            buy=buy_pct,
            hold=hold_pct,
            sell=sell_pct,
            targetPrice=target_price,
            recommendation=recommendation
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
