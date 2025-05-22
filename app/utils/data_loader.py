import yfinance as yf
import pandas as pd
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import logging
import asyncio
from functools import lru_cache
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Cache for stock data (expires after 5 minutes)
CACHE_DURATION = 300  # 5 minutes in seconds
stock_cache = {}

# Rate limiting settings
MAX_REQUESTS_PER_MINUTE = 20
REQUEST_INTERVAL = 60 / MAX_REQUESTS_PER_MINUTE  # Time between requests in seconds
last_request_time = 0

@lru_cache(maxsize=100)
def get_cached_stock_data(symbol: str, timestamp: int) -> Optional[Dict]:
    """
    Get cached stock data if available and not expired.
    """
    cache_key = f"{symbol}_{timestamp}"
    if cache_key in stock_cache:
        cache_time, data = stock_cache[cache_key]
        if datetime.now().timestamp() - cache_time < CACHE_DURATION:
            return data
    return None

async def rate_limited_request():
    """
    Ensure we don't exceed Yahoo Finance's rate limits.
    """
    global last_request_time
    current_time = time.time()
    time_since_last_request = current_time - last_request_time
    
    if time_since_last_request < REQUEST_INTERVAL:
        await asyncio.sleep(REQUEST_INTERVAL - time_since_last_request)
    
    last_request_time = time.time()

def safe_get(data: dict, key: str, default=None):
    """
    Safely get a value from a dictionary, handling nested keys.
    """
    try:
        return data.get(key, default)
    except Exception:
        return default

async def fetch_stock_data(symbol: str, max_retries: int = 3) -> Optional[Dict]:
    """
    Fetch stock data for a given symbol using yfinance.
    
    Args:
        symbol: Stock ticker symbol
        max_retries: Maximum number of retry attempts
        
    Returns:
        Dictionary containing stock data or None if data couldn't be fetched
    """
    try:
        # Check cache first
        current_timestamp = int(datetime.now().timestamp() / CACHE_DURATION)
        cached_data = get_cached_stock_data(symbol, current_timestamp)
        if cached_data:
            logger.info(f"Using cached data for {symbol}")
            return cached_data

        logger.info(f"Fetching data for {symbol}")
        
        # Set timeout for the request
        async def fetch_with_timeout():
            try:
                # Apply rate limiting
                await rate_limited_request()
                
                # Fetch stock info
                stock = yf.Ticker(symbol)
                info = stock.info
                
                if not info:
                    logger.error(f"No info found for {symbol}")
                    return None
                
                # Log all available info for debugging
                logger.info(f"Raw data for {symbol}:")
                for key, value in info.items():
                    logger.info(f"{key}: {value}")
                    
                # Get sector information
                sector = safe_get(info, 'sector', '')
                industry = safe_get(info, 'industry', '')
                logger.info(f"Sector for {symbol}: {sector}")
                logger.info(f"Industry for {symbol}: {industry}")
                
                # Apply rate limiting again before historical data
                await rate_limited_request()
                
                # Fetch historical data for moving averages
                end_date = datetime.now()
                start_date = end_date - timedelta(days=200)
                hist = stock.history(start=start_date, end=end_date)
                
                if hist.empty:
                    logger.error(f"No historical data found for {symbol}")
                    return None
                
                logger.info(f"Historical data for {symbol}:")
                logger.info(f"Latest close price: {hist['Close'].iloc[-1]}")
                
                # Calculate moving averages
                ma_50 = hist['Close'].rolling(window=50).mean().iloc[-1]
                ma_200 = hist['Close'].rolling(window=200).mean().iloc[-1]
                
                # Get current price (use close price if current price is not available)
                current_price = safe_get(info, 'currentPrice', hist['Close'].iloc[-1])
                
                # Prepare data with safe gets
                data = {
                    "symbol": symbol,
                    "name": safe_get(info, 'longName', symbol),
                    "sector": sector,
                    "industry": industry,
                    "price": current_price,
                    "volume": safe_get(info, 'volume', 0),
                    "market_cap": safe_get(info, 'marketCap', 0) / 1_000_000,  # Convert to millions
                    "pe_ratio": safe_get(info, 'trailingPE'),
                    "dividend_yield": safe_get(info, 'dividendYield', 0) * 100 if safe_get(info, 'dividendYield') else None,
                    "ma_50": ma_50,
                    "ma_200": ma_200,
                    "last_updated": datetime.utcnow()
                }
                
                logger.info(f"Processed data for {symbol}:")
                for key, value in data.items():
                    logger.info(f"{key}: {value}")
                
                # Cache the data
                cache_key = f"{symbol}_{current_timestamp}"
                stock_cache[cache_key] = (datetime.now().timestamp(), data)
                
                return data
                
            except Exception as e:
                logger.error(f"Error fetching data for {symbol}: {str(e)}")
                return None
        
        # Retry logic with exponential backoff
        for attempt in range(max_retries):
            try:
                # Set timeout of 10 seconds
                data = await asyncio.wait_for(fetch_with_timeout(), timeout=10.0)
                if data:
                    return data
            except asyncio.TimeoutError:
                logger.warning(f"Timeout on attempt {attempt + 1} for {symbol}")
            except Exception as e:
                logger.error(f"Error on attempt {attempt + 1} for {symbol}: {str(e)}")
            
            if attempt < max_retries - 1:
                # Exponential backoff: 2^attempt seconds
                wait_time = 2 ** attempt
                logger.info(f"Retrying {symbol} in {wait_time} seconds...")
                await asyncio.sleep(wait_time)
        
        return None
        
    except Exception as e:
        logger.error(f"Error fetching data for {symbol}: {str(e)}")
        return None 