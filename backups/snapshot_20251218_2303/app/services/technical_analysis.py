from typing import Dict, List, Optional
import pandas as pd
import numpy as np
import asyncio
from datetime import datetime, timedelta
from app.services.zerodha_service import ZerodhaService
from app.core.cache import redis_cache
import ta
from ta.trend import SMAIndicator, EMAIndicator, MACD
from ta.momentum import RSIIndicator, StochasticOscillator
from ta.volatility import BollingerBands
from ta.volume import VolumeWeightedAveragePrice

class TechnicalAnalysis:
    def __init__(self):
        self.zerodha_service = ZerodhaService()
        self.cache_ttl = 3600  # 1 hour

    async def get_comprehensive_analysis(self, symbol: str, interval: str = "1d") -> Dict:
        """Get comprehensive technical analysis"""
        try:
            # Get historical data
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=365)  # 1 year of data
            data = await self.zerodha_service.get_historical_data(
                symbol,
                start_date,
                end_date,
                interval
            )
            
            # Convert to DataFrame (run in threadpool)
            df = await asyncio.to_thread(self._prepare_dataframe, data)

            return {
                "trend_analysis": await self._analyze_trend(df),
                "momentum_indicators": await self._analyze_momentum(df),
                "volatility_indicators": await self._analyze_volatility(df),
                "volume_analysis": await self._analyze_volume(df),
                "support_resistance": await self._find_support_resistance(df),
                "pattern_recognition": await self._identify_patterns(df),
                "market_structure": await self._analyze_market_structure(df),
                "vwap_analysis": await self._analyze_vwap(df)
            }
        except Exception as e:
            logger.error(f"Error in comprehensive analysis: {str(e)}")
            raise

    def _prepare_dataframe(self, data: List[Dict]) -> pd.DataFrame:
        """Prepare DataFrame from data (runs in threadpool)"""
        df = pd.DataFrame(data)
        df['date'] = pd.to_datetime(df['date'])
        df.set_index('date', inplace=True)
        return df

    async def _analyze_trend(self, df: pd.DataFrame) -> Dict:
        """Analyze price trends"""
        try:
            return await asyncio.to_thread(self._analyze_trend_sync, df)
        except Exception as e:
            logger.error(f"Error in trend analysis: {str(e)}")
            raise

    def _analyze_trend_sync(self, df: pd.DataFrame) -> Dict:
        """Analyze price trends (runs in threadpool)"""
        # Calculate moving averages
        sma_20 = SMAIndicator(close=df['close'], window=20)
        sma_50 = SMAIndicator(close=df['close'], window=50)
        sma_200 = SMAIndicator(close=df['close'], window=200)
        
        # Calculate MACD
        macd = MACD(close=df['close'])
        
        return {
            "sma_20": sma_20.sma_indicator().iloc[-1],
            "sma_50": sma_50.sma_indicator().iloc[-1],
            "sma_200": sma_200.sma_indicator().iloc[-1],
            "macd": macd.macd().iloc[-1],
            "macd_signal": macd.macd_signal().iloc[-1],
            "macd_histogram": macd.macd_diff().iloc[-1],
            "trend_strength": self._calculate_trend_strength(df),
            "trend_direction": self._determine_trend_direction(df)
        }

    async def _analyze_momentum(self, df: pd.DataFrame) -> Dict:
        """Analyze momentum indicators"""
        try:
            return await asyncio.to_thread(self._analyze_momentum_sync, df)
        except Exception as e:
            logger.error(f"Error in momentum analysis: {str(e)}")
            raise
    
    def _analyze_momentum_sync(self, df: pd.DataFrame) -> Dict:
        """Analyze momentum indicators (sync version)"""
        # Calculate RSI
        rsi = RSIIndicator(close=df['close'])
        
        # Calculate Stochastic Oscillator
        stoch = StochasticOscillator(high=df['high'], low=df['low'], close=df['close'])
        
        return {
            "rsi": rsi.rsi().iloc[-1],
            "stoch_k": stoch.stoch().iloc[-1],
            "stoch_d": stoch.stoch_signal().iloc[-1],
            "momentum": self._calculate_momentum(df),
            "overbought_oversold": self._check_overbought_oversold(df)
        }

    async def _analyze_volatility(self, df: pd.DataFrame) -> Dict:
        """Analyze volatility indicators"""
        try:
            return await asyncio.to_thread(self._analyze_volatility_sync, df)
        except Exception as e:
            logger.error(f"Error in volatility analysis: {str(e)}")
            raise
    
    def _analyze_volatility_sync(self, df: pd.DataFrame) -> Dict:
        """Analyze volatility indicators (sync version)"""
        # Calculate Bollinger Bands
        bb = BollingerBands(close=df['close'])
        
        # Calculate ATR
        atr = ta.volatility.AverageTrueRange(
            high=df['high'],
            low=df['low'],
            close=df['close']
        )
        
        return {
            "bb_upper": bb.bollinger_hband().iloc[-1],
            "bb_middle": bb.bollinger_mavg().iloc[-1],
            "bb_lower": bb.bollinger_lband().iloc[-1],
            "bb_width": bb.bollinger_wband().iloc[-1],
            "atr": atr.average_true_range().iloc[-1],
            "volatility_ratio": self._calculate_volatility_ratio(df)
        }

    async def _analyze_volume(self, df: pd.DataFrame) -> Dict:
        """Analyze volume patterns"""
        try:
            return await asyncio.to_thread(self._analyze_volume_sync, df)
        except Exception as e:
            logger.error(f"Error in volume analysis: {str(e)}")
            raise
    
    def _analyze_volume_sync(self, df: pd.DataFrame) -> Dict:
        """Analyze volume patterns (sync version)"""
        # Calculate VWAP
        vwap = VolumeWeightedAveragePrice(
            high=df['high'],
            low=df['low'],
            close=df['close'],
            volume=df['volume']
        )
        
        return {
            "volume_sma": df['volume'].rolling(window=20).mean().iloc[-1],
            "volume_ratio": df['volume'].iloc[-1] / df['volume'].rolling(window=20).mean().iloc[-1],
            "vwap": vwap.volume_weighted_average_price().iloc[-1],
            "volume_trend": self._analyze_volume_trend(df),
            "volume_support_resistance": self._find_volume_support_resistance(df)
        }

    async def _analyze_vwap(self, df: pd.DataFrame) -> Dict:
        """Analyze VWAP patterns"""
        try:
            return await asyncio.to_thread(self._analyze_vwap_sync, df)
        except Exception as e:
            logger.error(f"Error in VWAP analysis: {str(e)}")
            raise
    
    def _analyze_vwap_sync(self, df: pd.DataFrame) -> Dict:
        """Analyze VWAP patterns (sync version)"""
        vwap = VolumeWeightedAveragePrice(
            high=df['high'],
            low=df['low'],
            close=df['close'],
            volume=df['volume']
        )
        vwap_value = vwap.volume_weighted_average_price()
        
        return {
            "vwap": vwap_value.iloc[-1],
            "vwap_trend": self._analyze_vwap_trend(vwap_value),
            "vwap_deviation": self._calculate_vwap_deviation(df['close'], vwap_value),
            "vwap_support_resistance": self._find_vwap_support_resistance(vwap_value)
        }

    def _calculate_trend_strength(self, df: pd.DataFrame) -> float:
        """Calculate trend strength using ADX"""
        try:
            adx = ta.trend.ADXIndicator(
                high=df['high'],
                low=df['low'],
                close=df['close']
            )
            return adx.adx().iloc[-1]
        except Exception as e:
            logger.error(f"Error calculating trend strength: {str(e)}")
            return 0.0

    def _determine_trend_direction(self, df: pd.DataFrame) -> str:
        """Determine trend direction"""
        try:
            sma_20 = df['close'].rolling(window=20).mean()
            sma_50 = df['close'].rolling(window=50).mean()
            
            if sma_20.iloc[-1] > sma_50.iloc[-1]:
                return "uptrend"
            elif sma_20.iloc[-1] < sma_50.iloc[-1]:
                return "downtrend"
            else:
                return "sideways"
        except Exception as e:
            logger.error(f"Error determining trend direction: {str(e)}")
            return "unknown"

    def _calculate_momentum(self, df: pd.DataFrame) -> float:
        """Calculate momentum"""
        try:
            return (df['close'].iloc[-1] - df['close'].iloc[-20]) / df['close'].iloc[-20] * 100
        except Exception as e:
            logger.error(f"Error calculating momentum: {str(e)}")
            return 0.0

    def _check_overbought_oversold(self, df: pd.DataFrame) -> str:
        """Check if price is overbought or oversold"""
        try:
            rsi = RSIIndicator(close=df['close']).rsi().iloc[-1]
            if rsi > 70:
                return "overbought"
            elif rsi < 30:
                return "oversold"
            else:
                return "neutral"
        except Exception as e:
            logger.error(f"Error checking overbought/oversold: {str(e)}")
            return "unknown"

    def _calculate_volatility_ratio(self, df: pd.DataFrame) -> float:
        """Calculate volatility ratio"""
        try:
            return df['close'].pct_change().std() * np.sqrt(252)
        except Exception as e:
            logger.error(f"Error calculating volatility ratio: {str(e)}")
            return 0.0

    def _analyze_volume_trend(self, df: pd.DataFrame) -> str:
        """Analyze volume trend"""
        try:
            volume_sma = df['volume'].rolling(window=20).mean()
            if df['volume'].iloc[-1] > volume_sma.iloc[-1] * 1.5:
                return "high"
            elif df['volume'].iloc[-1] < volume_sma.iloc[-1] * 0.5:
                return "low"
            else:
                return "normal"
        except Exception as e:
            logger.error(f"Error analyzing volume trend: {str(e)}")
            return "unknown"

    def _analyze_vwap_trend(self, vwap: pd.Series) -> str:
        """Analyze VWAP trend"""
        try:
            if vwap.iloc[-1] > vwap.iloc[-20]:
                return "uptrend"
            elif vwap.iloc[-1] < vwap.iloc[-20]:
                return "downtrend"
            else:
                return "sideways"
        except Exception as e:
            logger.error(f"Error analyzing VWAP trend: {str(e)}")
            return "unknown"

    def _calculate_vwap_deviation(self, close: pd.Series, vwap: pd.Series) -> float:
        """Calculate VWAP deviation"""
        try:
            return (close.iloc[-1] - vwap.iloc[-1]) / vwap.iloc[-1] * 100
        except Exception as e:
            logger.error(f"Error calculating VWAP deviation: {str(e)}")
            return 0.0

    async def _find_support_resistance(self, df: pd.DataFrame) -> Dict:
        """Find support and resistance levels"""
        try:
            return await asyncio.to_thread(self._find_support_resistance_sync, df)
        except Exception as e:
            logger.error(f"Error finding support/resistance: {str(e)}")
            return {}

    def _find_support_resistance_sync(self, df: pd.DataFrame) -> Dict:
        """Find support and resistance levels (sync version)"""
        # Implement support and resistance level calculation logic here
        return {}

    async def _identify_patterns(self, df: pd.DataFrame) -> Dict:
        """Identify chart patterns"""
        try:
            return await asyncio.to_thread(self._identify_patterns_sync, df)
        except Exception as e:
            logger.error(f"Error identifying patterns: {str(e)}")
            return {}

    def _identify_patterns_sync(self, df: pd.DataFrame) -> Dict:
        """Identify chart patterns (sync version)"""
        # Implement pattern recognition logic here
        return {}

    async def _analyze_market_structure(self, df: pd.DataFrame) -> Dict:
        """Analyze market structure"""
        try:
            return await asyncio.to_thread(self._analyze_market_structure_sync, df)
        except Exception as e:
            logger.error(f"Error analyzing market structure: {str(e)}")
            return {}

    def _analyze_market_structure_sync(self, df: pd.DataFrame) -> Dict:
        """Analyze market structure (sync version)"""
        # Implement market structure analysis logic here
        return {}

    async def _find_volume_support_resistance(self, df: pd.DataFrame) -> Dict:
        """Find volume support and resistance levels"""
        try:
            return await asyncio.to_thread(self._find_volume_support_resistance_sync, df)
        except Exception as e:
            logger.error(f"Error finding volume support/resistance: {str(e)}")
            return {}

    def _find_volume_support_resistance_sync(self, df: pd.DataFrame) -> Dict:
        """Find volume support and resistance levels (sync version)"""
        # Implement volume support and resistance level calculation logic here
        return {}

    async def _find_vwap_support_resistance(self, vwap: pd.Series) -> Dict:
        """Find VWAP support and resistance levels"""
        try:
            return await asyncio.to_thread(self._find_vwap_support_resistance_sync, vwap)
        except Exception as e:
            logger.error(f"Error finding VWAP support/resistance: {str(e)}")
            return {}

    def _find_vwap_support_resistance_sync(self, vwap: pd.Series) -> Dict:
        """Find VWAP support and resistance levels (sync version)"""
        # Implement VWAP support and resistance level calculation logic here
        return {}

technical_analysis = TechnicalAnalysis() 