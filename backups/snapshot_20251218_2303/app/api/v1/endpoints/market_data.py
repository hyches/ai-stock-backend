from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
from app.db.session import get_db
from app.models.trading import MarketData
from app.models.user import User
from app.api.deps import get_current_user

router = APIRouter()

@router.get("/", response_model=List[dict])
def get_market_data(
    symbol: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    limit: int = 1000,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get market data for a symbol"""
    query = db.query(MarketData).filter(MarketData.symbol == symbol)
    
    if start_date:
        start_dt = datetime.fromisoformat(start_date)
        query = query.filter(MarketData.timestamp >= start_dt)
    
    if end_date:
        end_dt = datetime.fromisoformat(end_date)
        query = query.filter(MarketData.timestamp <= end_dt)
    
    market_data = query.order_by(MarketData.timestamp.desc()).limit(limit).all()
    
    return [
        {
            "id": md.id,
            "symbol": md.symbol,
            "timestamp": md.timestamp,
            "open": md.open,
            "high": md.high,
            "low": md.low,
            "close": md.close,
            "volume": md.volume,
            "created_at": md.created_at
        }
        for md in market_data
    ]

@router.get("/{data_id}", response_model=dict)
def get_market_data_by_id(
    data_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get market data by ID"""
    market_data = db.query(MarketData).filter(MarketData.id == data_id).first()
    
    if not market_data:
        raise HTTPException(status_code=404, detail="Market data not found")
    
    return {
        "id": market_data.id,
        "symbol": market_data.symbol,
        "timestamp": market_data.timestamp,
        "open": market_data.open,
        "high": market_data.high,
        "low": market_data.low,
        "close": market_data.close,
        "volume": market_data.volume,
        "created_at": market_data.created_at
    }

@router.post("/", response_model=dict)
def create_market_data(
    symbol: str,
    timestamp: str,
    open_price: float,
    high: float,
    low: float,
    close: float,
    volume: float,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create new market data entry"""
    timestamp_dt = datetime.fromisoformat(timestamp)
    
    # Check if data already exists for this symbol and timestamp
    existing = db.query(MarketData).filter(
        MarketData.symbol == symbol,
        MarketData.timestamp == timestamp_dt
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="Market data already exists for this symbol and timestamp")
    
    market_data = MarketData(
        symbol=symbol,
        timestamp=timestamp_dt,
        open=open_price,
        high=high,
        low=low,
        close=close,
        volume=volume
    )
    
    db.add(market_data)
    db.commit()
    db.refresh(market_data)
    
    return {
        "id": market_data.id,
        "symbol": market_data.symbol,
        "timestamp": market_data.timestamp,
        "open": market_data.open,
        "high": market_data.high,
        "low": market_data.low,
        "close": market_data.close,
        "volume": market_data.volume,
        "created_at": market_data.created_at
    }

@router.get("/symbols/", response_model=List[str])
def get_available_symbols(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get list of available symbols"""
    symbols = db.query(MarketData.symbol).distinct().all()
    return [symbol[0] for symbol in symbols]

@router.get("/{symbol}/latest", response_model=dict)
def get_latest_market_data(
    symbol: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get latest market data for a symbol"""
    market_data = db.query(MarketData).filter(
        MarketData.symbol == symbol
    ).order_by(MarketData.timestamp.desc()).first()
    
    if not market_data:
        raise HTTPException(status_code=404, detail="No market data found for symbol")
    
    return {
        "id": market_data.id,
        "symbol": market_data.symbol,
        "timestamp": market_data.timestamp,
        "open": market_data.open,
        "high": market_data.high,
        "low": market_data.low,
        "close": market_data.close,
        "volume": market_data.volume,
        "created_at": market_data.created_at
    }

@router.get("/watchlist", response_model=List[dict])
def get_watchlist(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get user's watchlist"""
    # For now, return mock watchlist data
    return [
        {
            "symbol": "AAPL",
            "name": "Apple Inc.",
            "price": 179.50,
            "change": 2.50,
            "changePercent": 1.41,
            "volume": 50000000,
            "marketCap": 3000000000000
        },
        {
            "symbol": "MSFT", 
            "name": "Microsoft Corporation",
            "price": 408.75,
            "change": -1.25,
            "changePercent": -0.30,
            "volume": 25000000,
            "marketCap": 2800000000000
        },
        {
            "symbol": "GOOGL",
            "name": "Alphabet Inc.",
            "price": 176.45,
            "change": 3.20,
            "changePercent": 1.85,
            "volume": 30000000,
            "marketCap": 1800000000000
        }
    ]

