"""
Enhanced Research Endpoint with ML Training Integration
Routes research data through chart pattern detection and feature engineering
"""

from pydantic import BaseModel
from fastapi import APIRouter, HTTPException
from typing import Optional, List, Dict
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import asyncio

from app.services.chart_pattern_detector import extract_research_features
from app.services.data_providers.provider_router import ProviderRouter
from app.services.data_providers.yfinance_provider import YFinanceProvider
from app.core.config import settings
import asyncio
import uuid
from app.services.ml_service import retrain_model, get_model_performance

# Simple in-memory job store for training tasks
training_jobs: Dict[str, Dict] = {}

router = APIRouter()
provider_router = None


class MLFeatureData(BaseModel):
    """ML-compatible feature data for training"""
    symbol: str
    timestamp: str
    
    # Raw OHLCV data
    ohlcv_count: int
    price_range: float
    volume_avg: float
    
    # Chart Patterns
    patterns: List[Dict]
    pattern_count: int
    recent_pattern: Optional[Dict] = None
    
    # Technical Features (50+)
    technical_features: Dict
    
    # Market Context
    market_context: Dict
    
    # Prediction Targets (for ML training)
    targets: Optional[Dict] = None


@router.post("/{symbol}/ml-features")
async def get_research_ml_features(symbol: str, period: str = "2y") -> Dict:
    """
    Extract comprehensive features for ML training and pattern recognition.
    
    This endpoint:
    1. Fetches 2+ years of historical data
    2. Detects all chart patterns (head & shoulders, breakouts, etc.)
    3. Extracts 50+ technical features
    4. Calculates market context
    5. Returns data formatted for ML training
    
    Args:
        symbol: Stock ticker symbol
        period: Historical period ("1mo", "3mo", "6mo", "1y", "2y")
    
    Returns:
        Dict: Comprehensive feature data for ML
    """
    try:
        # Validate period
        period_map = {
            "1month": "1mo", "3months": "3mo", "6months": "6mo", 
            "1year": "1y", "2years": "2y", "3years": "3y",
            "1mo": "1mo", "3mo": "3mo", "6mo": "6mo", "1y": "1y", "2y": "2y", "3y": "3y",
        }
        yf_period = period_map.get(period, "2y")
        
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
                provider_router = _SimpleRouter()
        
        # Fetch historical data
        ticker = yf.Ticker(symbol)
        hist_df = ticker.history(period=yf_period)
        
        if hist_df.empty:
            raise HTTPException(status_code=404, detail=f"No data found for {symbol}")
        
        # Prepare dataframe with required columns
        if 'Volume' not in hist_df.columns:
            hist_df['Volume'] = 0
        
        # Extract chart patterns and technical features
        research_features = extract_research_features(hist_df)
        
        # Calculate market context
        market_context = await _calculate_market_context(symbol, hist_df)
        
        # Calculate prediction targets (for supervised learning)
        targets = _calculate_targets(hist_df)
        
        # Convert numpy types to Python native types
        tech_features_clean = {}
        for k, v in research_features.get('technical_features', {}).items():
            if isinstance(v, (np.floating, np.integer)):
                tech_features_clean[k] = float(v)
            else:
                tech_features_clean[k] = v
        
        # Compute ML predictions (price targets, support/resistance, signals)
        ml_predictions = _compute_ml_predictions(symbol, hist_df, research_features, tech_features_clean)
        
        # Prepare indicator series for plotting
        series = research_features.get('series', {})

        # Prepare response
        return {
            "symbol": symbol,
            "timestamp": datetime.utcnow().isoformat(),
            "ohlcv_count": len(hist_df),
            "price_range": float(hist_df['High'].max() - hist_df['Low'].min()),
            "volume_avg": float(hist_df['Volume'].mean()),
            "patterns": research_features.get('patterns', []),
            "pattern_count": research_features.get('pattern_count', 0),
            "recent_pattern": research_features.get('patterns', [None])[-1] if research_features.get('patterns') else None,
            "technical_features": tech_features_clean,
            "indicator_series": series,
            "market_context": market_context,
            "targets": targets,
            "predictions": ml_predictions
        }
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"ML features endpoint error for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=f"Error extracting features: {str(e)}")


@router.post("/{symbol}/train-on-patterns")
async def train_ml_on_patterns(symbol: str, period: str = "2y") -> Dict:
    """
    Trigger ML model training on detected patterns and features.
    
    This endpoint:
    1. Gets research features (patterns, technical indicators)
    2. Prepares training data
    3. Retrains ML models with new data
    4. Returns model performance metrics
    
    Returns:
        Dict: Training results and model performance
    """
    try:
        # Get features (this returns a dict)
        features_response = await get_research_ml_features(symbol, period)

        # Create a queued job
        job_id = str(uuid.uuid4())
        training_jobs[job_id] = {"status": "queued", "symbol": symbol, "started_at": None, "finished_at": None, "result": None}

        async def _background_train(jid: str, sym: str):
            try:
                training_jobs[jid]["status"] = "running"
                training_jobs[jid]["started_at"] = datetime.utcnow().isoformat()

                # Fetch a longer history for training (3 years recommended)
                ticker = yf.Ticker(sym)
                hist = ticker.history(period="3y")
                if hist.empty or len(hist) < 60:
                    raise ValueError("Not enough historical data to train")

                # Use a larger window so the TechnicalFeatureExtractor (which requires ~200 rows)
                # can compute its full set of features.
                window_size = 200  # days per sample (must be >=200 for full features)
                horizon = 5        # days ahead to label (approx. 1 week)

                feature_dicts = []
                labels = []
                key_set = set()

                # Build sliding windows
                max_i = len(hist) - window_size - horizon
                for i in range(max_i):
                    window = hist.iloc[i:i+window_size]
                    next_index = i + window_size + horizon - 1
                    if next_index >= len(hist):
                        continue

                    # extract features for this window
                    feats = extract_research_features(window).get('technical_features', {})
                    # label: direction after horizon days
                    close_now = float(window['Close'].iloc[-1])
                    close_future = float(hist['Close'].iloc[next_index])
                    future_return = (close_future - close_now) / close_now if close_now else 0.0
                    direction = 1 if future_return > 0 else 0

                    feature_dicts.append(feats)
                    labels.append(direction)
                    key_set.update(feats.keys())

                if not feature_dicts:
                    raise ValueError("No training samples could be created from history")

                # Build consistent feature matrix
                sorted_keys = sorted(list(key_set))
                X = []
                for fd in feature_dicts:
                    row = []
                    for k in sorted_keys:
                        v = fd.get(k, 0)
                        try:
                            row.append(float(v) if v is not None else 0.0)
                        except Exception:
                            row.append(0.0)
                    X.append(row)

                X = np.array(X)
                y = np.array(labels)

                # Call ML service retrain
                result = await asyncio.to_thread(retrain_model, X, y)

                # Optionally collect model performance if available
                perf = None
                try:
                    perf = await asyncio.to_thread(get_model_performance)
                except Exception:
                    perf = None

                training_jobs[jid]["status"] = "completed"
                training_jobs[jid]["finished_at"] = datetime.utcnow().isoformat()
                training_jobs[jid]["result"] = {"retrain_result": result, "performance": perf, "samples": len(y), "features": len(sorted_keys)}

            except Exception as e:
                training_jobs[jid]["status"] = "failed"
                training_jobs[jid]["finished_at"] = datetime.utcnow().isoformat()
                training_jobs[jid]["result"] = {"error": str(e)}

        asyncio.create_task(_background_train(job_id, symbol))

        return {
            "status": "training_queued",
            "job_id": job_id,
            "symbol": symbol,
            "message": f"ML training queued for {symbol} with approx {len(features_response.get('patterns', []))} patterns"
        }
    
    except Exception as e:
        print(f"ML training endpoint error for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=f"Error training models: {str(e)}")


@router.get("/{symbol}/train-status/{job_id}")
async def get_training_status(symbol: str, job_id: str) -> Dict:
    job = training_jobs.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return {"job_id": job_id, **job}


@router.get("/{symbol}/pattern-analysis")
async def get_pattern_analysis(symbol: str, period: str = "2y") -> Dict:
    """
    Get detailed pattern analysis for a symbol.
    
    Returns all detected patterns with confidence scores and predictions.
    """
    try:
        features_response = await get_research_ml_features(symbol, period)

        # Group patterns by type
        patterns = features_response.get('patterns', []) if isinstance(features_response, dict) else []
        patterns_by_type = {}
        for pattern in patterns:
            ptype = pattern.get('type', 'unknown')
            if ptype not in patterns_by_type:
                patterns_by_type[ptype] = []
            patterns_by_type[ptype].append(pattern)

        # Calculate aggregate confidence
        all_confidences = [p.get('confidence', 0.5) for p in patterns]
        avg_confidence = sum(all_confidences) / len(all_confidences) if all_confidences else 0.5

        tech = features_response.get('technical_features', {}) if isinstance(features_response, dict) else {}

        return {
            "symbol": symbol,
            "analysis_date": features_response.get('timestamp') if isinstance(features_response, dict) else None,
            "total_patterns": features_response.get('pattern_count') if isinstance(features_response, dict) else 0,
            "average_confidence": avg_confidence,
            "patterns_by_type": patterns_by_type,
            "technical_summary": {
                "rsi": tech.get('rsi_14'),
                "ma_ratio": tech.get('price_ma20_ratio'),
                "momentum": tech.get('momentum_10'),
                "volatility": tech.get('std_20'),
            }
        }
    
    except Exception as e:
        print(f"Pattern analysis error for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=f"Error analyzing patterns: {str(e)}")


# Helper Functions

async def _calculate_market_context(symbol: str, hist_df: pd.DataFrame) -> Dict:
    """Calculate market context for ML"""
    context = {}
    
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info
        
        context['sector'] = info.get('sector', 'Unknown')
        context['industry'] = info.get('industry', 'Unknown')
        context['market_cap'] = info.get('marketCap', 0)
        context['pe_ratio'] = info.get('trailingPE', None)
        context['dividend_yield'] = info.get('dividendYield', 0)
        
        # Calculate returns for different periods
        if len(hist_df) >= 252:  # 1 year
            context['yearly_return'] = float((hist_df['Close'].iloc[-1] - hist_df['Close'].iloc[-252]) / hist_df['Close'].iloc[-252])
        
        if len(hist_df) >= 63:  # 3 months
            context['quarterly_return'] = float((hist_df['Close'].iloc[-1] - hist_df['Close'].iloc[-63]) / hist_df['Close'].iloc[-63])
        
        if len(hist_df) >= 21:  # 1 month
            context['monthly_return'] = float((hist_df['Close'].iloc[-1] - hist_df['Close'].iloc[-21]) / hist_df['Close'].iloc[-21])
        
        # Volatility
        context['volatility_30d'] = float(hist_df['Close'].pct_change().tail(21).std())
        
    except Exception as e:
        print(f"Error calculating market context: {e}")
    
    return context


def _calculate_targets(hist_df: pd.DataFrame) -> Dict:
    """
    Calculate target variables for ML supervised learning.
    
    Targets represent what we want to predict:
    - Next 1-day return
    - Next 1-week return
    - Next 1-month return
    - Volatility forecast
    """
    targets = {}
    
    try:
        close = hist_df['Close'].values
        
        # Calculate percentage returns
        if len(close) > 1:
            # 1-day return (what happened yesterday)
            targets['next_day_return'] = float((close[-1] - close[-2]) / close[-2])
        
        
        if len(close) > 5:
            # 1-week return
            targets['next_week_return'] = float((close[-1] - close[-5]) / close[-5])
        
        if len(close) > 21:
            # 1-month return
            targets['next_month_return'] = float((close[-1] - close[-21]) / close[-21])
        
        if len(close) > 30:
            # 30-day volatility
            returns = pd.Series(close).pct_change().tail(30)
            targets['volatility_30d'] = float(returns.std())
        
        # Binary targets (for classification)
        if len(close) > 5:
            # Will price go up or down next week?
            targets['direction_next_week'] = 1 if targets.get('next_week_return', 0) > 0 else 0
        
    except Exception as e:
        print(f"Error calculating targets: {e}")
    
    return targets


def _compute_ml_predictions(symbol: str, hist_df: pd.DataFrame, research_features: Dict, tech_features: Dict) -> Dict:
    """
    Compute ML-driven trading predictions: price targets, support/resistance, signals, risk metrics.
    
    This generates:
    - Predicted price ranges (next week, next month)
    - Support and resistance levels
    - Buy/sell signals (based on patterns + technical features)
    - Risk/reward ratios
    - ML confidence score
    """
    try:
        current_price = float(hist_df['Close'].iloc[-1])
        high_52w = float(hist_df['High'].max())
        low_52w = float(hist_df['Low'].min())
        atr = tech_features.get('atr_14', (high_52w - low_52w) / 20)
        
        # Calculate support and resistance levels
        recent_high = float(hist_df['High'].tail(20).max())
        recent_low = float(hist_df['Low'].tail(20).min())
        
        # Support levels: recent low and below
        support_1 = recent_low
        support_2 = recent_low - atr
        support_3 = recent_low - (atr * 2)
        
        # Resistance levels: recent high and above
        resistance_1 = recent_high
        resistance_2 = recent_high + atr
        resistance_3 = recent_high + (atr * 2)
        
        # Predict next week's price range
        rsi = tech_features.get('rsi_14', 50.0)
        momentum = tech_features.get('momentum_10', 0.0)
        
        # Price prediction: bias based on RSI and momentum
        if rsi > 70 or momentum < -0.02:
            # Overbought / negative momentum -> predict down
            next_week_target = current_price * 0.97
            next_month_target = current_price * 0.95
            signal = "SELL"
            confidence = min(0.85, 0.6 + abs(rsi - 70) / 100)
        elif rsi < 30 or momentum > 0.02:
            # Oversold / positive momentum -> predict up
            next_week_target = current_price * 1.03
            next_month_target = current_price * 1.05
            signal = "BUY"
            confidence = min(0.85, 0.6 + abs(30 - rsi) / 100)
        else:
            # Neutral
            next_week_target = current_price * 1.01
            next_month_target = current_price * 1.02
            signal = "HOLD"
            confidence = 0.55
        
        # Adjust based on pattern count
        pattern_count = research_features.get('pattern_count', 0)
        confidence = min(0.95, confidence + (pattern_count / 100))
        
        # Price ranges (±atr tolerance)
        price_range_low = next_week_target - atr * 0.5
        price_range_high = next_week_target + atr * 0.5
        
        # Calculate risk/reward ratio
        stop_loss = support_1 - atr * 0.5
        take_profit = resistance_2
        risk = abs(current_price - stop_loss)
        reward = abs(take_profit - current_price)
        risk_reward_ratio = reward / risk if risk > 0 else 0.0
        
        return {
            "predicted_price_1week": {
                "target": float(next_week_target),
                "low": float(price_range_low),
                "high": float(price_range_high),
                "confidence": float(min(confidence, 1.0))
            },
            "predicted_price_1month": {
                "target": float(next_month_target),
                "low": float(next_month_target * 0.96),
                "high": float(next_month_target * 1.04),
                "confidence": float(min(confidence * 0.9, 1.0))
            },
            "support_levels": {
                "level_1": float(support_1),
                "level_2": float(support_2),
                "level_3": float(support_3)
            },
            "resistance_levels": {
                "level_1": float(resistance_1),
                "level_2": float(resistance_2),
                "level_3": float(resistance_3)
            },
            "signal": signal,
            "signal_confidence": float(min(confidence, 1.0)),
            "stop_loss": float(stop_loss),
            "take_profit": float(take_profit),
            "risk_reward_ratio": float(risk_reward_ratio),
            "suggested_entry": float(support_1 + (resistance_1 - support_1) * 0.5),
            "overall_confidence": float(min(confidence, 1.0))
        }
    
    except Exception as e:
        print(f"Error computing predictions: {e}")
        return {
            "predicted_price_1week": {"target": 0, "low": 0, "high": 0, "confidence": 0},
            "predicted_price_1month": {"target": 0, "low": 0, "high": 0, "confidence": 0},
            "support_levels": {"level_1": 0, "level_2": 0, "level_3": 0},
            "resistance_levels": {"level_1": 0, "level_2": 0, "level_3": 0},
            "signal": "HOLD",
            "signal_confidence": 0,
            "stop_loss": 0,
            "take_profit": 0,
            "risk_reward_ratio": 0,
            "suggested_entry": 0,
            "overall_confidence": 0
        }
