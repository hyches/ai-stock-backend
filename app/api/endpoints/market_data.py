from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
import yfinance as yf
import pandas as pd
from app.db.session import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.market import (
    StockSuggestion,
    StockDetails,
    HistoricalData,
    MarketOverview,
    PopularStock,
    StockNews,
    StockAnalysis,
    StockFinancials,
    StockPeer
)

router = APIRouter()

@router.get("/search", response_model=List[StockSuggestion])
async def search_stocks(
    q: str = Query(..., description="Search query"),
    limit: int = Query(10, description="Maximum number of results")
):
    """
    Search for stocks by symbol or name
    """
    try:
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
        
        # Add some popular stocks that match the query
        popular_stocks = [
            ('AAPL', 'Apple Inc.', 'NASDAQ'),
            ('MSFT', 'Microsoft Corporation', 'NASDAQ'),
            ('GOOGL', 'Alphabet Inc.', 'NASDAQ'),
            ('AMZN', 'Amazon.com Inc.', 'NASDAQ'),
            ('TSLA', 'Tesla Inc.', 'NASDAQ'),
            ('META', 'Meta Platforms Inc.', 'NASDAQ'),
            ('NVDA', 'NVIDIA Corporation', 'NASDAQ'),
            ('NFLX', 'Netflix Inc.', 'NASDAQ'),
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
        
        return suggestions[:limit]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search error: {str(e)}")

@router.get("/data/{symbol}", response_model=StockDetails)
async def get_stock_data(
    symbol: str,
    db: Session = Depends(get_db)
):
    """
    Get detailed stock information
    """
    try:
        ticker = yf.Ticker(symbol.upper())
        info = ticker.info
        
        if not info or 'currentPrice' not in info:
            raise HTTPException(status_code=404, detail="Stock not found")
        
        # Get current price and change
        hist = ticker.history(period="1d")
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

@router.get("/data/{symbol}/historical", response_model=List[HistoricalData])
async def get_historical_data(
    symbol: str,
    period: str = Query("1y", description="Time period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)"),
    interval: str = Query("1d", description="Data interval (1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo)")
):
    """
    Get historical stock data
    """
    try:
        ticker = yf.Ticker(symbol.upper())
        hist = ticker.history(period=period, interval=interval)
        
        if hist.empty:
            raise HTTPException(status_code=404, detail="No historical data available")
        
        historical_data = []
        for date, row in hist.iterrows():
            historical_data.append(HistoricalData(
                date=date.strftime('%Y-%m-%d'),
                open=float(row['Open']),
                high=float(row['High']),
                low=float(row['Low']),
                close=float(row['Close']),
                volume=int(row['Volume'])
            ))
        
        return historical_data
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching historical data: {str(e)}")

@router.get("/overview", response_model=MarketOverview)
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
        
        return MarketOverview(
            totalMarketCap=45000000000000,  # Mock data
            totalVolume=total_volume,
            gainers=gainers,
            losers=losers,
            unchanged=unchanged
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching market overview: {str(e)}")

@router.get("/popular", response_model=List[PopularStock])
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
                    
                    popular_stocks.append(PopularStock(
                        symbol=symbol,
                        name=info.get('longName', info.get('shortName', symbol)),
                        price=float(current_price),
                        change=float(change),
                        changePercent=float(change_percent),
                        volume=int(hist['Volume'].iloc[-1])
                    ))
                    
            except Exception:
                continue
        
        return popular_stocks
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching popular stocks: {str(e)}")

@router.get("/news/{symbol}", response_model=List[StockNews])
async def get_stock_news(symbol: str):
    """
    Get news for a specific stock
    """
    try:
        ticker = yf.Ticker(symbol.upper())
        news = ticker.news
        
        stock_news = []
        for item in news[:10]:  # Limit to 10 news items
            stock_news.append(StockNews(
                title=item.get('title', 'No title'),
                summary=item.get('summary', 'No summary'),
                source=item.get('publisher', 'Unknown'),
                publishedAt=datetime.fromtimestamp(item.get('providerPublishTime', 0)).isoformat(),
                url=item.get('link', '')
            ))
        
        return stock_news
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching news: {str(e)}")

@router.get("/financials/{symbol}", response_model=StockFinancials)
async def get_stock_financials(symbol: str):
    """
    Get financial data for a stock
    """
    try:
        ticker = yf.Ticker(symbol.upper())
        info = ticker.info
        
        return StockFinancials(
            revenue=float(info.get('totalRevenue', 0)) if info.get('totalRevenue') else 0,
            netIncome=float(info.get('netIncomeToCommon', 0)) if info.get('netIncomeToCommon') else 0,
            assets=float(info.get('totalAssets', 0)) if info.get('totalAssets') else 0,
            liabilities=float(info.get('totalLiab', 0)) if info.get('totalLiab') else 0,
            equity=float(info.get('totalStockholderEquity', 0)) if info.get('totalStockholderEquity') else 0,
            cash=float(info.get('totalCash', 0)) if info.get('totalCash') else 0,
            debt=float(info.get('totalDebt', 0)) if info.get('totalDebt') else 0
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching financials: {str(e)}")

@router.get("/peers/{symbol}", response_model=List[StockPeer])
async def get_stock_peers(symbol: str):
    """
    Get peer companies for a stock
    """
    try:
        # This is a simplified implementation
        # In a real application, you would use a more sophisticated peer identification algorithm
        peer_symbols = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'META', 'NVDA', 'NFLX']
        peers = []
        
        for peer_symbol in peer_symbols:
            if peer_symbol != symbol.upper():
                try:
                    ticker = yf.Ticker(peer_symbol)
                    info = ticker.info
                    hist = ticker.history(period="1d")
                    
                    if not hist.empty:
                        current_price = hist['Close'].iloc[-1]
                        prev_close = hist['Open'].iloc[0]
                        change = current_price - prev_close
                        change_percent = (change / prev_close) * 100 if prev_close > 0 else 0
                        
                        peers.append(StockPeer(
                            symbol=peer_symbol,
                            name=info.get('longName', info.get('shortName', peer_symbol)),
                            price=float(current_price),
                            change=float(change),
                            changePercent=float(change_percent),
                            marketCap=float(info.get('marketCap', 0)) if info.get('marketCap') else 0
                        ))
                        
                except Exception:
                    continue
        
        return peers[:5]  # Return top 5 peers
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching peers: {str(e)}")
