from pydantic import BaseModel
from fastapi import APIRouter, HTTPException
import yfinance as yf
from typing import Optional, List
import pandas as pd
from concurrent.futures import ThreadPoolExecutor
import asyncio

from app.core.config import settings
from app.services.data_providers.provider_router import ProviderRouter
from app.services.data_providers.yfinance_provider import YFinanceProvider
from app.utils.anomaly_detector import AnomalyDetector
from datetime import datetime, timedelta

_executor = ThreadPoolExecutor(max_workers=2)
router = APIRouter()
provider_router = None
anomaly_detector = AnomalyDetector()


class StockInfo(BaseModel):
    symbol: str
    longName: Optional[str] = None
    currency: Optional[str] = None
    dayHigh: Optional[float] = None
    dayLow: Optional[float] = None
    fiftyTwoWeekHigh: Optional[float] = None
    fiftyTwoWeekLow: Optional[float] = None
    marketCap: Optional[float] = None
    volume: Optional[int] = None
    averageVolume: Optional[int] = None
    trailingPE: Optional[float] = None
    forwardPE: Optional[float] = None
    trailingEps: Optional[float] = None
    dividendYield: Optional[float] = None
    priceToSalesTrailing12Months: Optional[float] = None
    beta: Optional[float] = None
    longBusinessSummary: Optional[str] = None
    sector: Optional[str] = None
    industry: Optional[str] = None
    currentPrice: Optional[float] = None
    previousClose: Optional[float] = None


class HistData(BaseModel):
    date: str
    open: Optional[float] = None
    high: Optional[float] = None
    low: Optional[float] = None
    close: Optional[float] = None
    volume: Optional[int] = None
    adjusted_close: Optional[float] = None


class NewsData(BaseModel):
    title: Optional[str] = None
    publisher: Optional[str] = None
    link: Optional[str] = None
    published_at: Optional[int] = None
    summary: Optional[str] = None
    sentiment: Optional[float] = None
    relevance_score: Optional[float] = None
    matched_entities: Optional[dict] = None
    source_provider: Optional[str] = None


class RecommendationData(BaseModel):
    firm: Optional[str] = None
    toGrade: Optional[str] = None
    fromGrade: Optional[str] = None
    action: Optional[str] = None


class FinancialData(BaseModel):
    market_cap: Optional[float] = None
    pe_ratio: Optional[float] = None
    forward_pe: Optional[float] = None
    earnings_per_share: Optional[float] = None
    dividend_yield: Optional[float] = None
    price_to_sales: Optional[float] = None
    debt_to_equity: Optional[float] = None
    current_ratio: Optional[float] = None
    roe: Optional[float] = None
    roa: Optional[float] = None
    profit_margin: Optional[float] = None
    revenue: Optional[float] = None
    net_income: Optional[float] = None


class TechnicalData(BaseModel):
    sma_20: Optional[float] = None
    sma_50: Optional[float] = None
    sma_200: Optional[float] = None
    ema_12: Optional[float] = None
    ema_26: Optional[float] = None
    rsi_14: Optional[float] = None


class ComprehensiveStockData(BaseModel):
    info: StockInfo
    history: List[HistData]
    news: List[NewsData]
    recommendations: List[RecommendationData]
    technicals: Optional[TechnicalData] = None
    ml_predictions: Optional[dict] = None

# ... (StockQuoteLite definition remains)

@router.get("/{symbol}", response_model=ComprehensiveStockData)
async def get_comprehensive_stock_data(symbol: str, period: str = "1y", filter_news: bool = True):
    try:
        # ... (existing period logic)
        period_map = {
            "1month": "1mo", "3months": "3mo", "6months": "6mo", "1year": "1y", "3years": "3y",
            "1mo": "1mo", "3mo": "3mo", "6mo": "6mo", "1y": "1y", "3y": "3y",
        }
        if period not in period_map:
            raise HTTPException(status_code=400, detail=f"Invalid period")
        yf_period = period_map[period]

        global provider_router
        if provider_router is None:
            try:
                provider_router = ProviderRouter(settings)
            except Exception:
                yprov = YFinanceProvider()
                class _SimpleRouter:
                    async def get_info(self, s):
                        return await yprov.get_info(s)
                    async def get_history(self, s, p):
                        return await yprov.get_history(s, p)
                    async def get_news(self, s, limit=10):
                        return await yprov.get_news(s, limit)
                    async def get_financials(self, s):
                        return await yprov.get_financials(s)
                provider_router = _SimpleRouter()

        info = await provider_router.get_info(symbol)
        if not info:
            raise HTTPException(status_code=404, detail="Symbol not found")

        if hasattr(info, 'model_dump'):
            info_dict = info.model_dump()
        elif hasattr(info, '__dict__'):
            info_dict = vars(info)
        else:
            info_dict = info

        # Ensure we provide a current price (frontend expects currentPrice)
        try:
            ticker_for_price = yf.Ticker(symbol)
            if 'currentPrice' not in info_dict or info_dict.get('currentPrice') is None:
                recent = ticker_for_price.history(period='2d')
                if recent is not None and not recent.empty:
                    info_dict['currentPrice'] = float(recent['Close'].iloc[-1])
            if 'previousClose' not in info_dict or info_dict.get('previousClose') is None:
                recent = ticker_for_price.history(period='3d')
                if recent is not None and not recent.empty:
                    if len(recent['Close']) >= 2:
                        info_dict['previousClose'] = float(recent['Close'].iloc[-2])
                    else:
                        info_dict['previousClose'] = float(recent['Close'].iloc[-1])
        except Exception:
            pass

        history = await provider_router.get_history(symbol, yf_period)
        history_data = [{'date': getattr(h, 'date', None), 'open': getattr(h, 'open', None), 'high': getattr(h, 'high', None), 'low': getattr(h, 'low', None), 'close': getattr(h, 'close', None), 'volume': getattr(h, 'volume', None), 'adjusted_close': getattr(h, 'adjusted_close', None)} for h in history if hasattr(h, '__dict__')] if history else []

        news = await provider_router.get_news(symbol, limit=10)
        news_data = []
        if news:
            for n in news:
                if not hasattr(n, '__dict__'):
                    continue
                published = getattr(n, 'published_at', None) or getattr(n, 'providerPublishTime', None) or getattr(n, 'provider_publish_time', None)
                news_data.append({
                    'title': getattr(n, 'title', None),
                    'publisher': getattr(n, 'publisher', None),
                    'link': getattr(n, 'link', None),
                    'published_at': published,
                    'providerPublishTime': published,
                    'summary': getattr(n, 'summary', None),
                    'sentiment': getattr(n, 'sentiment', None),
                    'relevance_score': getattr(n, 'relevance_score', None),
                    'matched_entities': getattr(n, 'matched_entities', None),
                    'source_provider': getattr(n, 'source_provider', None),
                })

        financials = await provider_router.get_financials(symbol)
        financials_data = None
        if financials and hasattr(financials, '__dict__'):
            def _get(fi, *names):
                for n in names:
                    v = getattr(fi, n, None)
                    if v is not None:
                        return v
                return None

            financials_data = {
                'market_cap': _get(financials, 'market_cap', 'marketCap', 'market_capitalization'),
                'pe_ratio': _get(financials, 'pe_ratio', 'peRatio', 'trailingPE'),
                'forward_pe': _get(financials, 'forward_pe', 'forwardPE'),
                'earnings_per_share': _get(financials, 'earnings_per_share', 'eps', 'trailingEps'),
                'dividend_yield': _get(financials, 'dividend_yield', 'dividendYield'),
                'price_to_sales': _get(financials, 'price_to_sales', 'priceToSales', 'priceToSalesTrailing12Months'),
                'debt_to_equity': _get(financials, 'debt_to_equity', 'debtToEquity'),
                'current_ratio': _get(financials, 'current_ratio', 'currentRatio'),
                'roe': _get(financials, 'roe', 'returnOnEquity'),
                'roa': _get(financials, 'roa', 'returnOnAssets'),
                'profit_margin': _get(financials, 'profit_margin', 'netProfitMargin'),
                'revenue': _get(financials, 'revenue', 'totalRevenue'),
                'net_income': _get(financials, 'net_income', 'netIncome'),
            }

        technicals_data = None
        try:
            # We already have history, pandas dataframe preferable for technicals
            # But here history is a list of objects.
            # Let's use yfinance ticker for consistent calculation if needed, 
            # or convert history list to df. Using ticker is safer for consistency.
            ticker = yf.Ticker(symbol)
            hist_df = ticker.history(period=yf_period)
            
            if not hist_df.empty and 'Close' in hist_df:
                close = hist_df['Close']
                technicals_data = {
                    'sma_20': float(close.rolling(20).mean().iloc[-1]) if len(close) >= 20 else None,
                    'sma_50': float(close.rolling(50).mean().iloc[-1]) if len(close) >= 50 else None,
                    'sma_200': float(close.rolling(200).mean().iloc[-1]) if len(close) >= 200 else None,
                    'ema_12': float(close.ewm(span=12, adjust=False).mean().iloc[-1]) if len(close) >= 12 else None,
                    'ema_26': float(close.ewm(span=26, adjust=False).mean().iloc[-1]) if len(close) >= 26 else None,
                    'rsi_14': None,
                }
                if len(close) >= 15:
                    delta = close.diff()
                    gain = delta.clip(lower=0).rolling(14).mean()
                    loss = -delta.clip(upper=0).rolling(14).mean()
                    rs = gain / loss
                    rsi_14 = 100 - (100 / (1 + rs))
                    technicals_data['rsi_14'] = float(rsi_14.iloc[-1]) if not rsi_14.isna().all() else None
        except Exception:
            pass

        # ML Predictions (New "World Class" Integration)
        ml_predictions_data = None
        try:
            from app.services.ml_engine import ml_engine
            # 1. Try Cache First (Fastest)
            cached = ml_engine.get_cached_prediction(symbol)
            if cached:
                ml_predictions_data = cached
            else:
                # 2. Try Live Prediction (if we have data)
                if 'hist_df' in locals() and not hist_df.empty:
                     ml_res = ml_engine.predict(symbol, hist_df)
                     if ml_res.get('status') == 'success':
                         ml_predictions_data = ml_res
        except Exception as e:
            print(f"ML integration error in research: {e}")

        async def _fetch_recommendations():
            loop = asyncio.get_event_loop()
            def _get_recs():
                try:
                    t = yf.Ticker(symbol)
                    if t.recommendations is not None and not t.recommendations.empty:
                        recs_df = t.recommendations.reset_index()
                        return [{'firm': r.get('firm') or r.get('source'), 'toGrade': r.get('tograde'), 'fromGrade': r.get('fromgrade'), 'action': r.get('action')} for r in recs_df.to_dict(orient='records')]
                except Exception:
                    return []
                return []
            return await loop.run_in_executor(_executor, _get_recs)

        recommendations_data = await _fetch_recommendations()

        data = ComprehensiveStockData(
            info=StockInfo(**info_dict),
            history=[HistData(**h) for h in history_data],
            news=[NewsData(**n) for n in news_data],
            recommendations=[RecommendationData(**r) for r in recommendations_data] if recommendations_data else [],
            financials=FinancialData(**financials_data) if financials_data else None,
            technicals=TechnicalData(**technicals_data) if technicals_data else None,
            ml_predictions=ml_predictions_data
        )
        return data

    except HTTPException:
        raise
    except Exception as e:
        print(f"Research endpoint error for {symbol}: {e}")
        raise HTTPException(status_code=500, detail="Error fetching stock data")

@router.get("/{symbol}/anomalies")
async def get_stock_anomalies(symbol: str, period: str = "1y"):
    """
    Detect statistical anomalies in stock price (Z-Score analysis)
    """
    global provider_router
    # Ensure provider is initialized (copying logic from main endpoint or extracting to deep)
    # Ideally should be a dependency injection but for speed sticking to pattern
    if provider_router is None:
        try:
             provider_router = ProviderRouter(settings)
        except:
             yprov = YFinanceProvider()
             class _SimpleRouter:
                 async def get_info(self, s):
                     return await yprov.get_info(s)
                 async def get_history(self, s, p):
                     return await yprov.get_history(s, p)
                 async def get_news(self, s, limit=10):
                     return await yprov.get_news(s, limit)
                 async def get_financials(self, s):
                     return await yprov.get_financials(s)
             provider_router = _SimpleRouter()
             
    yf_period = "1y" # Default
    period_map = {"1month": "1mo", "3months": "3mo", "6months": "6mo", "1year": "1y", "1y": "1y"}
    if period in period_map:
        yf_period = period_map[period]

    try:
        history = await provider_router.get_history(symbol, yf_period)
        if not history:
             return {"anomalies": [], "count": 0}
             
        # Extract closes and dates
        # History objects might be Pydantic or dicts depending on provider
        closes = []
        dates = []
        for h in history:
             val = getattr(h, 'close', None)
             dt = getattr(h, 'date', None)
             if val is not None and dt is not None:
                 closes.append(float(val))
                 dates.append(str(dt))
                 
        anomalies = anomaly_detector.detect_anomalies(closes, dates)
        
        return {
            "symbol": symbol,
            "anomalies": anomalies,
            "count": len(anomalies)
        }
    except Exception as e:
        print(f"Anomaly detection error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/market/weather")
async def get_market_weather():
    """
    Get overall market sentiment/weather based on volatility and anomalies of key indices
    """
    indices = ["^NSEI", "^NSEBANK"] # Nifty 50, Bank Nifty
    weather_report = {}
    
    global provider_router
    if provider_router is None:
         yprov = YFinanceProvider()
         class _SimpleRouter:
             async def get_info(self, s):
                 return await yprov.get_info(s)
             async def get_history(self, s, p):
                 return await yprov.get_history(s, p)
             async def get_news(self, s, limit=10):
                 return await yprov.get_news(s, limit)
             async def get_financials(self, s):
                 return await yprov.get_financials(s)
         provider_router = _SimpleRouter()
    
    try:
        total_volatility = 0
        total_anomalies = 0
        
        for index in indices:
            history = await provider_router.get_history(index, "6mo")
            if history:
                 closes = [float(getattr(h, 'close')) for h in history if getattr(h, 'close', None)]
                 dates = [str(getattr(h, 'date')) for h in history if getattr(h, 'date', None)]
                 
                 # Analyze
                 market_data = [{"close": c, "date": d} for c, d in zip(closes, dates)]
                 analysis = anomaly_detector.analyze_market_behavior(market_data)
                 
                 weather_report[index] = analysis
                 total_volatility += analysis.get("current_volatility", 0)
                 total_anomalies += analysis.get("anomalies_count", 0)
        
        avg_vol = total_volatility / len(indices) if indices else 0
        
        # Determine overall state
        status = "Sunny"
        if avg_vol > 0.20 or total_anomalies > 10:
             status = "Stormy"
        elif avg_vol > 0.12 or total_anomalies > 5:
             status = "Cloudy"
             
        return {
            "status": status,
            "volatility_index": avg_vol,
            "details": weather_report
        }
    except Exception as e:
        print(f"Weather error: {e}")
        # Fallback
        return {"status": "Unknown", "error": str(e)}