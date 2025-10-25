from typing import List, Dict
import yfinance as yf

def get_stock_data(symbol: str) -> Dict:
    """
    Get stock data using yfinance
    """
    try:
        ticker = yf.Ticker(symbol.upper())
        info = ticker.info
        
        if not info or 'currentPrice' not in info:
            return {"error": "Stock not found"}
        
        # Get current price and change
        hist = ticker.history(period="1d")
        if hist.empty:
            return {"error": "No price data available"}
        
        current_price = hist['Close'].iloc[-1]
        prev_close = info.get('previousClose', current_price)
        change = current_price - prev_close
        change_percent = (change / prev_close) * 100 if prev_close > 0 else 0
        
        return {
            "symbol": symbol.upper(),
            "name": info.get('longName', info.get('shortName', symbol.upper())),
            "price": float(current_price),
            "change": float(change),
            "changePercent": float(change_percent),
            "volume": int(info.get('volume', 0)),
            "marketCap": float(info.get('marketCap', 0)),
            "pe": float(info.get('trailingPE', 0)) if info.get('trailingPE') else 0,
            "eps": float(info.get('trailingEps', 0)) if info.get('trailingEps') else 0,
            "dividend": float(info.get('dividendRate', 0)) if info.get('dividendRate') else 0,
            "dividendYield": float(info.get('dividendYield', 0)) if info.get('dividendYield') else 0,
            "high52Week": float(info.get('fiftyTwoWeekHigh', 0)) if info.get('fiftyTwoWeekHigh') else 0,
            "low52Week": float(info.get('fiftyTwoWeekLow', 0)) if info.get('fiftyTwoWeekLow') else 0,
            "avgVolume": float(info.get('averageVolume', 0)) if info.get('averageVolume') else 0,
            "beta": float(info.get('beta', 0)) if info.get('beta') else 0,
            "sector": info.get('sector', 'Unknown'),
            "industry": info.get('industry', 'Unknown'),
            "description": info.get('longBusinessSummary', 'No description available'),
            "website": info.get('website', ''),
            "employees": int(info.get('fullTimeEmployees', 0)) if info.get('fullTimeEmployees') else 0,
            "founded": int(info.get('founded', 0)) if info.get('founded') else 0,
            "headquarters": info.get('city', '') + ', ' + info.get('state', '') + ', ' + info.get('country', '')
        }
    except Exception as e:
        return {"error": f"Error fetching stock data: {str(e)}"}

def search_symbols(query: str) -> List[Dict]:
    """
    Search for stocks by symbol or name
    """
    try:
        if len(query) < 2:
            return []
        
        # Use yfinance to get stock info
        ticker = yf.Ticker(query.upper())
        info = ticker.info
        
        if not info or 'symbol' not in info:
            return []
        
        suggestions = []
        
        # Add the exact match if found
        if info.get('symbol'):
            suggestions.append({
                "symbol": info.get('symbol', query.upper()),
                "name": info.get('longName', info.get('shortName', query.upper())),
                "exchange": info.get('exchange', 'Unknown'),
                "type": info.get('quoteType', 'Stock')
            })
        
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
            if (query.upper() in symbol.upper() or 
                query.lower() in name.lower()) and len(suggestions) < 10:
                suggestions.append({
                    "symbol": symbol,
                    "name": name,
                    "exchange": exchange,
                    "type": 'Stock'
                })
        
        return suggestions[:10]
        
    except Exception as e:
        return [{"error": f"Search error: {str(e)}"}] 