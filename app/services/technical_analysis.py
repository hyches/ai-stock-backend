from typing import Dict, List, Optional
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from app.services.zerodha_service import ZerodhaService
from app.core.cache import redis_cache

class TechnicalAnalysis:
    def __init__(self):
        self.zerodha_service = ZerodhaService()
        self.cache_ttl = 3600  # 1 hour

    async def get_comprehensive_analysis(self, symbol: str, interval: str = "1d") -> Dict:
        """Get comprehensive technical analysis"""
        return {
            "trend_analysis": await self._analyze_trend(symbol, interval),
            "momentum_indicators": await self._analyze_momentum(symbol, interval),
            "volatility_indicators": await self._analyze_volatility(symbol, interval),
            "volume_analysis": await self._analyze_volume(symbol, interval),
            "support_resistance": await self._find_support_resistance(symbol, interval),
            "pattern_recognition": await self._identify_patterns(symbol, interval),
            "market_structure": await self._analyze_market_structure(symbol, interval)
        }

    async def _analyze_trend(self, symbol: str, interval: str) -> Dict:
        """Analyze price trends"""
        try:
            ohlc_data = await self._get_ohlc_data(symbol, interval)
            
            return {
                "moving_averages": {
                    "sma": self._calculate_sma(ohlc_data, [20, 50, 100, 200]),
                    "ema": self._calculate_ema(ohlc_data, [20, 50, 100, 200]),
                    "vwap": self._calculate_vwap(ohlc_data)
                },
                "trend_strength": {
                    "adx": self._calculate_adx(ohlc_data),
                    "trend_strength_index": self._calculate_trend_strength_index(ohlc_data),
                    "ichimoku": self._calculate_ichimoku(ohlc_data)
                },
                "trend_direction": {
                    "macd": self._calculate_macd(ohlc_data),
                    "parabolic_sar": self._calculate_parabolic_sar(ohlc_data),
                    "supertrend": self._calculate_supertrend(ohlc_data)
                }
            }
        except Exception as e:
            logger.error(f"Error analyzing trend: {str(e)}")
            return {}

    async def _analyze_momentum(self, symbol: str, interval: str) -> Dict:
        """Analyze momentum indicators"""
        try:
            ohlc_data = await self._get_ohlc_data(symbol, interval)
            
            return {
                "oscillators": {
                    "rsi": self._calculate_rsi(ohlc_data),
                    "stochastic": self._calculate_stochastic(ohlc_data),
                    "cci": self._calculate_cci(ohlc_data),
                    "mfi": self._calculate_mfi(ohlc_data)
                },
                "momentum": {
                    "roc": self._calculate_roc(ohlc_data),
                    "momentum": self._calculate_momentum(ohlc_data),
                    "williams_r": self._calculate_williams_r(ohlc_data)
                },
                "divergence": {
                    "rsi_divergence": self._find_rsi_divergence(ohlc_data),
                    "macd_divergence": self._find_macd_divergence(ohlc_data)
                }
            }
        except Exception as e:
            logger.error(f"Error analyzing momentum: {str(e)}")
            return {}

    async def _analyze_volatility(self, symbol: str, interval: str) -> Dict:
        """Analyze volatility indicators"""
        try:
            ohlc_data = await self._get_ohlc_data(symbol, interval)
            
            return {
                "volatility_indicators": {
                    "bollinger_bands": self._calculate_bollinger_bands(ohlc_data),
                    "atr": self._calculate_atr(ohlc_data),
                    "keltner_channels": self._calculate_keltner_channels(ohlc_data)
                },
                "volatility_analysis": {
                    "historical_volatility": self._calculate_historical_volatility(ohlc_data),
                    "implied_volatility": self._calculate_implied_volatility(ohlc_data),
                    "volatility_breakout": self._identify_volatility_breakout(ohlc_data)
                }
            }
        except Exception as e:
            logger.error(f"Error analyzing volatility: {str(e)}")
            return {}

    async def _analyze_volume(self, symbol: str, interval: str) -> Dict:
        """Analyze volume indicators"""
        try:
            ohlc_data = await self._get_ohlc_data(symbol, interval)
            
            return {
                "volume_indicators": {
                    "obv": self._calculate_obv(ohlc_data),
                    "vpt": self._calculate_vpt(ohlc_data),
                    "cmf": self._calculate_cmf(ohlc_data)
                },
                "volume_analysis": {
                    "volume_profile": self._calculate_volume_profile(ohlc_data),
                    "volume_delta": self._calculate_volume_delta(ohlc_data),
                    "volume_trend": self._analyze_volume_trend(ohlc_data)
                }
            }
        except Exception as e:
            logger.error(f"Error analyzing volume: {str(e)}")
            return {}

    async def _find_support_resistance(self, symbol: str, interval: str) -> Dict:
        """Find support and resistance levels"""
        try:
            ohlc_data = await self._get_ohlc_data(symbol, interval)
            
            return {
                "pivot_points": self._calculate_pivot_points(ohlc_data),
                "support_resistance_levels": self._identify_support_resistance(ohlc_data),
                "fibonacci_levels": self._calculate_fibonacci_levels(ohlc_data)
            }
        except Exception as e:
            logger.error(f"Error finding support/resistance: {str(e)}")
            return {}

    async def _identify_patterns(self, symbol: str, interval: str) -> Dict:
        """Identify chart patterns"""
        try:
            ohlc_data = await self._get_ohlc_data(symbol, interval)
            
            return {
                "candlestick_patterns": self._identify_candlestick_patterns(ohlc_data),
                "chart_patterns": {
                    "head_and_shoulders": self._identify_head_and_shoulders(ohlc_data),
                    "double_top_bottom": self._identify_double_top_bottom(ohlc_data),
                    "triangles": self._identify_triangles(ohlc_data),
                    "flags_pennants": self._identify_flags_pennants(ohlc_data)
                },
                "harmonic_patterns": self._identify_harmonic_patterns(ohlc_data)
            }
        except Exception as e:
            logger.error(f"Error identifying patterns: {str(e)}")
            return {}

    async def _analyze_market_structure(self, symbol: str, interval: str) -> Dict:
        """Analyze market structure"""
        try:
            ohlc_data = await self._get_ohlc_data(symbol, interval)
            
            return {
                "market_phases": self._identify_market_phases(ohlc_data),
                "trend_structure": {
                    "higher_highs_lows": self._identify_higher_highs_lows(ohlc_data),
                    "trend_channels": self._identify_trend_channels(ohlc_data),
                    "breakouts_breakdowns": self._identify_breakouts_breakdowns(ohlc_data)
                },
                "market_regime": self._identify_market_regime(ohlc_data)
            }
        except Exception as e:
            logger.error(f"Error analyzing market structure: {str(e)}")
            return {}

    # Helper methods for calculations
    def _calculate_sma(self, data: pd.DataFrame, periods: List[int]) -> Dict:
        """Calculate Simple Moving Average"""
        return {f"sma_{period}": data['close'].rolling(window=period).mean() for period in periods}

    def _calculate_ema(self, data: pd.DataFrame, periods: List[int]) -> Dict:
        """Calculate Exponential Moving Average"""
        return {f"ema_{period}": data['close'].ewm(span=period, adjust=False).mean() for period in periods}

    def _calculate_vwap(self, data: pd.DataFrame) -> pd.Series:
        """Calculate Volume Weighted Average Price"""
        v = data['volume'].values
        tp = (data['high'] + data['low'] + data['close']) / 3
        return (tp * v).cumsum() / v.cumsum()

    # Add more calculation methods for other indicators...

technical_analysis = TechnicalAnalysis() 