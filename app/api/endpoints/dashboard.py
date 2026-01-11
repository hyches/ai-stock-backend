"""
Dashboard API Endpoint - Unified dashboard data using Feature Store
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import logging

from app.db.session import get_db
from app.services.feature_store_service import FeatureStoreService
import yfinance as yf
import pandas as pd

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/summary")
async def get_dashboard_summary(
    symbols: Optional[str] = "RELIANCE.NS,TCS.NS,HDFCBANK.NS,INFY.NS,ITC.NS",
    db: Session = Depends(get_db)
):
    """
    Get comprehensive dashboard summary with market overview, portfolio stats, and key metrics
    Uses Feature Store for efficient data retrieval with caching
    """
    try:
        logger.info("Starting dashboard summary generation")
        feature_store = FeatureStoreService(db)
        logger.info("FeatureStoreService initialized successfully")
        
        # Try to get cached dashboard data
        cache_key = f"dashboard:summary:{symbols}"
        logger.info(f"Checking cache for key: {cache_key}")
        cached_data = feature_store.get_cached_data(cache_key)
        
        if cached_data:
            logger.info(f"Dashboard summary cache hit: {cache_key}")
            return cached_data
        
        # Parse symbols
        symbol_list = [s.strip() for s in symbols.split(",")]
        
        # Fetch market data for each symbol
        market_data = []
        portfolio_value = 0
        total_change = 0
        
        for symbol in symbol_list:
            try:
                # Get latest features from Feature Store
                features = feature_store.get_features_bulk(symbol)
                
                if not features:
                    # Fetch fresh data if not in feature store
                    ticker = yf.Ticker(symbol)
                    hist = ticker.history(period="5d")
                    
                    if not hist.empty:
                        current_price = float(hist['Close'].iloc[-1])
                        prev_price = float(hist['Close'].iloc[-2]) if len(hist) > 1 else current_price
                        change_pct = ((current_price - prev_price) / prev_price) * 100 if prev_price > 0 else 0
                        
                        # Store in feature store for future use
                        feature_store.store_features_bulk(
                            symbol=symbol,
                            features={
                                "current_price": current_price,
                                "change_percent": change_pct,
                                "volume": float(hist['Volume'].iloc[-1]) if 'Volume' in hist else 0
                            },
                            source="yfinance"
                        )
                        
                        features = {
                            "current_price": current_price,
                            "change_percent": change_pct,
                            "volume": float(hist['Volume'].iloc[-1]) if 'Volume' in hist else 0
                        }
                    else:
                        continue
                
                # Assume equal weighting for demo (10 lakh per stock)
                quantity = 1000000 / features.get("current_price", 1)
                position_value = quantity * features.get("current_price", 0)
                
                market_data.append({
                    "symbol": symbol,
                    "price": features.get("current_price", 0),
                    "change": features.get("change_percent", 0),
                    "volume": features.get("volume", 0),
                    "quantity": quantity,
                    "value": position_value
                })
                
                portfolio_value += position_value
                total_change += position_value * (features.get("change_percent", 0) / 100)
                
            except Exception as e:
                logger.error(f"Error fetching data for {symbol}: {e}")
                continue
        
        # Calculate summary metrics
        portfolio_change_pct = (total_change / portfolio_value * 100) if portfolio_value > 0 else 0
        
        # Get historical performance (last 30 days)
        performance_data = []
        for i in range(30, 0, -1):
            date = datetime.now() - timedelta(days=i)
            # Simulate portfolio value (in production, fetch from database)
            value = portfolio_value * (1 - (i * 0.001))  # Mock data
            performance_data.append({
                "date": date.strftime("%Y-%m-%d"),
                "value": value
            })
        
        # Market indices (Nifty 50, Bank Nifty)
        indices = []
        for index_symbol in ["^NSEI", "^NSEBANK"]:
            try:
                ticker = yf.Ticker(index_symbol)
                hist = ticker.history(period="2d")
                if not hist.empty:
                    current = float(hist['Close'].iloc[-1])
                    prev = float(hist['Close'].iloc[-2]) if len(hist) > 1 else current
                    change = ((current - prev) / prev * 100) if prev > 0 else 0
                    
                    indices.append({
                        "name": "Nifty 50" if "NSEI" in index_symbol else "Bank Nifty",
                        "value": current,
                        "change": change
                    })
            except Exception as e:
                logger.error(f"Error fetching index {index_symbol}: {e}")
        
        # Prepare dashboard data
        dashboard_data = {
            "portfolio": {
                "total_value": portfolio_value,
                "total_change": total_change,
                "change_percent": portfolio_change_pct,
                "positions": market_data,
                "cash_available": 10000000  # 1 crore virtual cash
            },
            "performance": performance_data,
            "market_indices": indices,
            "top_gainers": sorted(market_data, key=lambda x: x['change'], reverse=True)[:3],
            "top_losers": sorted(market_data, key=lambda x: x['change'])[:3],
            "timestamp": datetime.utcnow().isoformat(),
            "data_source": "feature_store_with_yfinance"
        }
        
        # Cache for 5 minutes
        feature_store.cache_data(
            cache_key=cache_key,
            cache_type="dashboard",
            data=dashboard_data,
            ttl_seconds=300
        )
        
        logger.info(f"Dashboard summary generated for {len(symbol_list)} symbols")
        return dashboard_data
        
    except Exception as e:
        logger.error(f"Error generating dashboard summary: {e}", exc_info=True)
        
        # Return a basic fallback response
        return {
            "portfolio": {
                "total_value": 0,
                "total_change": 0,
                "change_percent": 0,
                "positions": [],
                "cash_available": 10000000
            },
            "performance": [],
            "market_indices": [],
            "top_gainers": [],
            "top_losers": [],
            "timestamp": datetime.utcnow().isoformat(),
            "data_source": "error_fallback",
            "error": str(e)
        }


@router.get("/portfolio")
async def get_portfolio_data(db: Session = Depends(get_db)):
    """
    Get detailed portfolio data with holdings, performance, and analytics
    """
    try:
        feature_store = FeatureStoreService(db)
        
        cache_key = "dashboard:portfolio:detailed"
        cached_data = feature_store.get_cached_data(cache_key)
        
        if cached_data:
            return cached_data
        
        # TODO: Implement actual portfolio management when user system is added
        # For now, return mock data structure
        portfolio_data = {
            "holdings": [],
            "total_value": 0,
            "total_cost": 0,
            "total_pnl": 0,
            "pnl_percent": 0,
            "cash_balance": 10000000,
            "message": "Portfolio management will be available after user authentication is implemented"
        }
        
        feature_store.cache_data(
            cache_key=cache_key,
            cache_type="portfolio",
            data=portfolio_data,
            ttl_seconds=60  # Cache for 1 minute
        )
        
        return portfolio_data
        
    except Exception as e:
        logger.error(f"Error getting portfolio data: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get portfolio data: {str(e)}"
        )


@router.get("/watchlist")
async def get_watchlist(
    symbols: Optional[str] = "RELIANCE.NS,TCS.NS,INFY.NS",
    db: Session = Depends(get_db)
):
    """
    Get watchlist with real-time quotes
    """
    try:
        feature_store = FeatureStoreService(db)
        symbol_list = [s.strip() for s in symbols.split(",")]
        
        cache_key = f"dashboard:watchlist:{symbols}"
        cached_data = feature_store.get_cached_data(cache_key)
        
        if cached_data:
            return cached_data
        
        watchlist = []
        for symbol in symbol_list:
            features = feature_store.get_features_bulk(symbol)
            
            if not features:
                # Fetch fresh data
                try:
                    ticker = yf.Ticker(symbol)
                    hist = ticker.history(period="2d")
                    if not hist.empty:
                        current = float(hist['Close'].iloc[-1])
                        prev = float(hist['Close'].iloc[-2]) if len(hist) > 1 else current
                        change = ((current - prev) / prev * 100) if prev > 0 else 0
                        
                        features = {
                            "current_price": current,
                            "change_percent": change
                        }
                        
                        feature_store.store_features_bulk(symbol, features, source="yfinance")
                except:
                    continue
            
            watchlist.append({
                "symbol": symbol,
                "price": features.get("current_price", 0),
                "change": features.get("change_percent", 0)
            })
        
        watchlist_data = {"items": watchlist}
        
        feature_store.cache_data(
            cache_key=cache_key,
            cache_type="watchlist",
            data=watchlist_data,
            ttl_seconds=60  # 1 minute cache
        )
        
        return watchlist_data
        
    except Exception as e:
        logger.error(f"Error getting watchlist: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get watchlist: {str(e)}"
        )
