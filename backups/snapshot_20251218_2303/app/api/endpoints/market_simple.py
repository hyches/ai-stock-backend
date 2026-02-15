from fastapi import APIRouter, Depends, HTTPException, Query, Response
from app.core.security import get_current_user
from app.schemas.market import StockDetails, StockSuggestion
from typing import List
import yfinance as yf
from functools import lru_cache
import time

router = APIRouter()

@router.get("/search", response_model=List[StockSuggestion])
async def search_stocks(
    q: str = Query(..., description="Search query"),
    limit: int = Query(10, description="Maximum number of results"),
    response: Response = None
):
    """
    Search for stocks by symbol or name
    """
    try:
        start_time = time.time()
        
        if len(q) < 2:
            return []
        
        # Use yfinance to get stock info
        ticker = yf.Ticker(q.upper())
        info = ticker.info
        
        if not info or 'symbol' not in info:
            return []
        
        suggestions = []
        
        # Add the exact match if found
        if info.get('symbol'):
            suggestions.append(StockSuggestion(
                symbol=info.get('symbol', q.upper()),
                name=info.get('longName', info.get('shortName', q.upper())),
                exchange=info.get('exchange', 'Unknown'),
                type=info.get('quoteType', 'Stock')
            ))
        
        # Add popular stocks from various exchanges
        popular_stocks = [
            # US Stocks
            ('AAPL', 'Apple Inc.', 'NASDAQ'),
            ('MSFT', 'Microsoft Corporation', 'NASDAQ'),
            ('GOOGL', 'Alphabet Inc.', 'NASDAQ'),
            ('AMZN', 'Amazon.com Inc.', 'NASDAQ'),
            ('TSLA', 'Tesla Inc.', 'NASDAQ'),
            ('META', 'Meta Platforms Inc.', 'NASDAQ'),
            ('NVDA', 'NVIDIA Corporation', 'NASDAQ'),
            ('NFLX', 'Netflix Inc.', 'NASDAQ'),
            # International Stocks
            ('ASML', 'ASML Holding N.V.', 'AMS'),
            ('SAP', 'SAP SE', 'FRA'),
            ('NOVN', 'Novartis AG', 'SWX'),
            ('ROG', 'Roche Holding AG', 'SWX'),
            ('NESN', 'Nestlé S.A.', 'SWX'),
            ('TSM', 'Taiwan Semiconductor', 'TPE'),
            ('BABA', 'Alibaba Group', 'NYSE'),
            ('JD', 'JD.com Inc.', 'NASDAQ'),
            ('PDD', 'Pinduoduo Inc.', 'NASDAQ'),
            ('NIO', 'NIO Inc.', 'NYSE'),
            ('XPEV', 'XPeng Inc.', 'NYSE'),
            ('LI', 'Li Auto Inc.', 'NASDAQ'),
            # European Stocks
            ('SHEL', 'Shell plc', 'LSE'),
            ('UL', 'Unilever plc', 'LSE'),
            ('AZN', 'AstraZeneca plc', 'LSE'),
            ('GSK', 'GSK plc', 'LSE'),
            ('BP', 'BP p.l.c.', 'LSE'),
            ('VOD', 'Vodafone Group plc', 'LSE'),
            ('TSCO', 'Tesco plc', 'LSE'),
            ('PRU', 'Prudential plc', 'LSE'),
            # Asian Stocks
            ('TM', 'Toyota Motor Corporation', 'TYO'),
            ('HMC', 'Honda Motor Co., Ltd.', 'TYO'),
            ('SONY', 'Sony Group Corporation', 'TYO'),
            ('MUFG', 'Mitsubishi UFJ Financial Group', 'TYO'),
            ('SMFG', 'Sumitomo Mitsui Financial Group', 'TYO'),
            ('MFG', 'Mizuho Financial Group', 'TYO'),
            ('7203', 'Toyota Motor Corp', 'TYO'),
            ('6758', 'Sony Group Corp', 'TYO'),
            ('9984', 'SoftBank Group Corp', 'TYO'),
            # Indian Stocks (NSE/BSE)
            ('RELIANCE', 'Reliance Industries Ltd', 'NSE'),
            ('TCS', 'Tata Consultancy Services Ltd', 'NSE'),
            ('HDFCBANK', 'HDFC Bank Ltd', 'NSE'),
            ('INFY', 'Infosys Ltd', 'NSE'),
            ('HINDUNILVR', 'Hindustan Unilever Ltd', 'NSE'),
            ('ITC', 'ITC Ltd', 'NSE'),
            ('SBIN', 'State Bank of India', 'NSE'),
            ('BHARTIARTL', 'Bharti Airtel Ltd', 'NSE'),
            ('KOTAKBANK', 'Kotak Mahindra Bank Ltd', 'NSE'),
            ('LT', 'Larsen & Toubro Ltd', 'NSE'),
            ('ASIANPAINT', 'Asian Paints Ltd', 'NSE'),
            ('MARUTI', 'Maruti Suzuki India Ltd', 'NSE'),
            ('AXISBANK', 'Axis Bank Ltd', 'NSE'),
            ('TITAN', 'Titan Company Ltd', 'NSE'),
            ('NESTLEIND', 'Nestle India Ltd', 'NSE'),
            ('ULTRACEMCO', 'UltraTech Cement Ltd', 'NSE'),
            ('WIPRO', 'Wipro Ltd', 'NSE'),
            ('POWERGRID', 'Power Grid Corporation of India Ltd', 'NSE'),
            ('NTPC', 'NTPC Ltd', 'NSE'),
            ('ONGC', 'Oil and Natural Gas Corporation Ltd', 'NSE'),
            ('COALINDIA', 'Coal India Ltd', 'NSE'),
            ('TECHM', 'Tech Mahindra Ltd', 'NSE'),
            ('SUNPHARMA', 'Sun Pharmaceutical Industries Ltd', 'NSE'),
            ('DRREDDY', 'Dr. Reddy\'s Laboratories Ltd', 'NSE'),
            ('CIPLA', 'Cipla Ltd', 'NSE'),
            ('BAJFINANCE', 'Bajaj Finance Ltd', 'NSE'),
            ('BAJAJFINSV', 'Bajaj Finserv Ltd', 'NSE'),
            ('HCLTECH', 'HCL Technologies Ltd', 'NSE'),
            ('TATAMOTORS', 'Tata Motors Ltd', 'NSE'),
            ('TATASTEEL', 'Tata Steel Ltd', 'NSE'),
            ('JSWSTEEL', 'JSW Steel Ltd', 'NSE'),
            ('ADANIPORTS', 'Adani Ports and Special Economic Zone Ltd', 'NSE'),
            ('ADANIENT', 'Adani Enterprises Ltd', 'NSE'),
            ('ADANIGREEN', 'Adani Green Energy Ltd', 'NSE'),
            ('ADANITRANS', 'Adani Transmission Ltd', 'NSE'),
            ('ADANIPOWER', 'Adani Power Ltd', 'NSE'),
            ('ADANITOTAL', 'Adani Total Gas Ltd', 'NSE'),
            ('IRCTC', 'Indian Railway Catering and Tourism Corporation Ltd', 'NSE'),
            ('ZOMATO', 'Zomato Ltd', 'NSE'),
            ('PAYTM', 'One97 Communications Ltd', 'NSE'),
            ('NYKAA', 'FSN E-Commerce Ventures Ltd', 'NSE'),
            ('POLICYBZR', 'PB Fintech Ltd', 'NSE'),
        ]
        
        for symbol, name, exchange in popular_stocks:
            if (q.upper() in symbol.upper() or 
                q.lower() in name.lower()) and len(suggestions) < limit:
                suggestions.append(StockSuggestion(
                    symbol=symbol,
                    name=name,
                    exchange=exchange,
                    type='Stock'
                ))
        
        result = suggestions[:limit]
        
        # Add performance headers
        end_time = time.time()
        response.headers["X-Response-Time"] = f"{end_time - start_time:.3f}s"
        response.headers["X-Cache-Status"] = "MISS"  # Could implement actual caching later
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search error: {str(e)}")

@router.get("/data/{symbol}", response_model=StockDetails)
async def get_stock_data(
    symbol: str,
    db = None  # Remove dependency for now
):
    """
    Get detailed stock information
    """
    try:
        import asyncio
        import concurrent.futures
        
        def fetch_stock_data(symbol):
            ticker = yf.Ticker(symbol.upper())
            info = ticker.info
            hist = ticker.history(period="1d")
            return info, hist
        
        # Use timeout to prevent hanging
        loop = asyncio.get_event_loop()
        with concurrent.futures.ThreadPoolExecutor() as executor:
            try:
                info, hist = await asyncio.wait_for(
                    loop.run_in_executor(executor, fetch_stock_data, symbol.upper()),
                    timeout=10.0  # 10 second timeout
                )
            except asyncio.TimeoutError:
                raise HTTPException(status_code=408, detail="Request timeout - stock data service is slow")
        
        if not info or 'currentPrice' not in info:
            raise HTTPException(status_code=404, detail="Stock not found")
        
        if hist.empty:
            raise HTTPException(status_code=404, detail="No price data available")
        
        current_price = hist['Close'].iloc[-1]
        prev_close = info.get('previousClose', current_price)
        change = current_price - prev_close
        change_percent = (change / prev_close) * 100 if prev_close > 0 else 0
        
        return StockDetails(
            symbol=symbol.upper(),
            name=info.get('longName', info.get('shortName', symbol.upper())),
            price=float(current_price),
            change=float(change),
            changePercent=float(change_percent),
            volume=int(info.get('volume', 0)),
            marketCap=float(info.get('marketCap', 0)),
            pe=float(info.get('trailingPE', 0)) if info.get('trailingPE') else 0,
            eps=float(info.get('trailingEps', 0)) if info.get('trailingEps') else 0,
            dividend=float(info.get('dividendRate', 0)) if info.get('dividendRate') else 0,
            dividendYield=float(info.get('dividendYield', 0)) if info.get('dividendYield') else 0,
            high52Week=float(info.get('fiftyTwoWeekHigh', 0)) if info.get('fiftyTwoWeekHigh') else 0,
            low52Week=float(info.get('fiftyTwoWeekLow', 0)) if info.get('fiftyTwoWeekLow') else 0,
            avgVolume=float(info.get('averageVolume', 0)) if info.get('averageVolume') else 0,
            beta=float(info.get('beta', 0)) if info.get('beta') else 0,
            sector=info.get('sector', 'Unknown'),
            industry=info.get('industry', 'Unknown'),
            description=info.get('longBusinessSummary', 'No description available'),
            website=info.get('website', ''),
            employees=int(info.get('fullTimeEmployees', 0)) if info.get('fullTimeEmployees') else 0,
            founded=int(info.get('founded', 0)) if info.get('founded') else 0,
            headquarters=info.get('city', '') + ', ' + info.get('state', '') + ', ' + info.get('country', '')
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching stock data: {str(e)}")

@router.get("/overview")
async def get_market_overview():
    """
    Get market overview statistics
    """
    try:
        # Get major indices
        indices = ['^GSPC', '^DJI', '^IXIC', '^VIX']
        total_market_cap = 0
        total_volume = 0
        gainers = 0
        losers = 0
        unchanged = 0
        
        for index in indices:
            try:
                ticker = yf.Ticker(index)
                info = ticker.info
                hist = ticker.history(period="1d")
                
                if not hist.empty:
                    current = hist['Close'].iloc[-1]
                    prev = hist['Open'].iloc[0]
                    change = current - prev
                    
                    if change > 0:
                        gainers += 1
                    elif change < 0:
                        losers += 1
                    else:
                        unchanged += 1
                    
                    total_volume += int(hist['Volume'].iloc[-1])
                    
            except Exception:
                continue
        
        return {
            "totalMarketCap": 45000000000000,  # Mock data
            "totalVolume": total_volume,
            "gainers": gainers,
            "losers": losers,
            "unchanged": unchanged
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching market overview: {str(e)}")

@router.get("/popular")
async def get_popular_stocks():
    """
    Get popular/most traded stocks
    """
    try:
        popular_symbols = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'META', 'NVDA', 'NFLX']
        popular_stocks = []
        
        for symbol in popular_symbols:
            try:
                ticker = yf.Ticker(symbol)
                info = ticker.info
                hist = ticker.history(period="1d")
                
                if not hist.empty:
                    current_price = hist['Close'].iloc[-1]
                    prev_close = hist['Open'].iloc[0]
                    change = current_price - prev_close
                    change_percent = (change / prev_close) * 100 if prev_close > 0 else 0
                    
                    popular_stocks.append({
                        "symbol": symbol,
                        "name": info.get('longName', info.get('shortName', symbol)),
                        "price": float(current_price),
                        "change": float(change),
                        "changePercent": float(change_percent),
                        "volume": int(hist['Volume'].iloc[-1])
                    })
                    
            except Exception:
                continue
        
        return popular_stocks
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching popular stocks: {str(e)}")

