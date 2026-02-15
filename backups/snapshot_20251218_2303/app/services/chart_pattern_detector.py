"""
Chart Pattern Detection & Feature Engineering Module
Extracts patterns and features from price data for ML training
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class PatternType(Enum):
    HEAD_SHOULDERS = "head_shoulders"
    DOUBLE_TOP = "double_top"
    DOUBLE_BOTTOM = "double_bottom"
    TRIPLE_TOP = "triple_top"
    TRIPLE_BOTTOM = "triple_bottom"
    TRIANGLE = "triangle"
    ASCENDING_TRIANGLE = "ascending_triangle"
    DESCENDING_TRIANGLE = "descending_triangle"
    WEDGE = "wedge"
    CHANNEL = "channel"
    BREAKOUT = "breakout"
    SUPPORT_BOUNCE = "support_bounce"
    RESISTANCE_REJECTION = "resistance_rejection"
    CUP_HANDLE = "cup_handle"
    FLAG = "flag"


@dataclass
class PatternSignal:
    """Detected pattern signal"""
    pattern_type: PatternType
    confidence: float  # 0-1 probability
    start_index: int
    end_index: int
    price_level: float
    direction: str  # "up" or "down"
    strength: float  # Pattern strength measure
    target_price: Optional[float] = None
    stop_loss: Optional[float] = None
    description: str = ""


class ChartPatternDetector:
    """Detects chart patterns from historical price data"""
    
    def __init__(self, min_confidence: float = 0.65):
        self.min_confidence = min_confidence
    
    def detect_all_patterns(self, df: pd.DataFrame) -> List[PatternSignal]:
        """Detect all chart patterns in data"""
        patterns = []
        
        patterns.extend(self.detect_head_shoulders(df))
        patterns.extend(self.detect_double_patterns(df))
        patterns.extend(self.detect_triangles(df))
        patterns.extend(self.detect_wedges(df))
        patterns.extend(self.detect_channels(df))
        patterns.extend(self.detect_breakouts(df))
        patterns.extend(self.detect_support_resistance(df))
        patterns.extend(self.detect_cup_handle(df))
        patterns.extend(self.detect_flags(df))
        
        return [p for p in patterns if p.confidence >= self.min_confidence]
    
    def detect_head_shoulders(self, df: pd.DataFrame) -> List[PatternSignal]:
        """Detect head & shoulders pattern"""
        patterns = []
        
        if len(df) < 50:
            return patterns
        
        high = df['High'].values
        low = df['Low'].values
        close = df['Close'].values
        
        # Find local peaks (potential shoulders and head)
        peaks = self._find_local_peaks(high, window=5, threshold=0.02)
        
        if len(peaks) >= 3:
            for i in range(len(peaks) - 2):
                left_shoulder = peaks[i]
                head = peaks[i + 1]
                right_shoulder = peaks[i + 2]
                
                # Head should be higher than shoulders
                if high[head] > high[left_shoulder] * 1.02 and high[head] > high[right_shoulder] * 1.02:
                    # Shoulders should be roughly equal
                    if abs(high[left_shoulder] - high[right_shoulder]) < high[head] * 0.02:
                        # Neckline: connect lows between shoulders
                        neckline = (low[left_shoulder] + low[right_shoulder]) / 2
                        
                        # Price should break below neckline
                        if i + 2 < len(df) - 5:
                            future_low = min(low[peaks[i+2]:peaks[i+2]+5])
                            if future_low < neckline * 0.99:
                                confidence = self._calculate_pattern_confidence(
                                    high[head] / high[left_shoulder],
                                    high[head] / high[right_shoulder],
                                    0.98
                                )
                                
                                patterns.append(PatternSignal(
                                    pattern_type=PatternType.HEAD_SHOULDERS,
                                    confidence=confidence,
                                    start_index=left_shoulder,
                                    end_index=right_shoulder,
                                    price_level=neckline,
                                    direction="down",
                                    strength=1.0,
                                    target_price=neckline - (high[head] - neckline),
                                    stop_loss=high[head] * 1.01,
                                    description=f"Head & Shoulders reversal at {neckline:.2f}"
                                ))
        
        return patterns
    
    def detect_double_patterns(self, df: pd.DataFrame) -> List[PatternSignal]:
        """Detect double tops and bottoms"""
        patterns = []
        
        if len(df) < 40:
            return patterns
        
        high = df['High'].values
        low = df['Low'].values
        
        # Double tops
        peaks = self._find_local_peaks(high, window=5, threshold=0.01)
        if len(peaks) >= 2:
            for i in range(len(peaks) - 1):
                peak1, peak2 = peaks[i], peaks[i + 1]
                
                # Peaks should be at similar levels
                if abs(high[peak1] - high[peak2]) < high[peak1] * 0.02:
                    # Find valley between peaks
                    valley = np.argmin(high[peak1:peak2]) + peak1
                    valley_price = low[valley]
                    
                    confidence = self._calculate_pattern_confidence(
                        high[peak1] / high[peak2],
                        high[peak1],
                        0.96
                    )
                    
                    patterns.append(PatternSignal(
                        pattern_type=PatternType.DOUBLE_TOP,
                        confidence=confidence,
                        start_index=peak1,
                        end_index=peak2,
                        price_level=high[peak1],
                        direction="down",
                        strength=0.9,
                        target_price=valley_price * 0.98,
                        stop_loss=high[peak1] * 1.02,
                        description=f"Double Top reversal at {high[peak1]:.2f}"
                    ))
        
        # Double bottoms
        troughs = self._find_local_troughs(low, window=5, threshold=0.01)
        if len(troughs) >= 2:
            for i in range(len(troughs) - 1):
                trough1, trough2 = troughs[i], troughs[i + 1]
                
                # Troughs should be at similar levels
                if abs(low[trough1] - low[trough2]) < low[trough1] * 0.02:
                    peak = np.argmax(high[trough1:trough2]) + trough1
                    peak_price = high[peak]
                    
                    confidence = self._calculate_pattern_confidence(
                        low[trough1] / low[trough2],
                        low[trough1],
                        0.96
                    )
                    
                    patterns.append(PatternSignal(
                        pattern_type=PatternType.DOUBLE_BOTTOM,
                        confidence=confidence,
                        start_index=trough1,
                        end_index=trough2,
                        price_level=low[trough1],
                        direction="up",
                        strength=0.9,
                        target_price=peak_price * 1.02,
                        stop_loss=low[trough1] * 0.98,
                        description=f"Double Bottom reversal at {low[trough1]:.2f}"
                    ))
        
        return patterns
    
    def detect_triangles(self, df: pd.DataFrame) -> List[PatternSignal]:
        """Detect triangle patterns"""
        patterns = []
        
        if len(df) < 30:
            return patterns
        
        high = df['High'].values
        low = df['Low'].values
        close = df['Close'].values
        
        # Symmetric triangle: highs lower, lows higher
        window = 20
        for i in range(window, len(df) - 5):
            segment_high = high[i-window:i]
            segment_low = low[i-window:i]
            
            # Check if range is contracting
            if np.max(segment_high) - np.min(segment_high) > 0:
                high_trend = (segment_high[-1] - segment_high[0]) / np.max(segment_high)
                low_trend = (segment_low[-1] - segment_low[0]) / np.max(segment_low)
                
                # Triangle pattern: highs descending, lows ascending
                if high_trend < -0.02 and low_trend > 0.02:
                    # Check for breakout
                    future_segment = close[i:min(i+10, len(df))]
                    current_range = np.max(segment_high) - np.min(segment_low)
                    
                    if len(future_segment) > 0:
                        breakout_dist = abs(future_segment[-1] - close[i]) / current_range
                        if breakout_dist > 0.03:
                            confidence = min(0.8, 0.5 + breakout_dist)
                            
                            patterns.append(PatternSignal(
                                pattern_type=PatternType.ASCENDING_TRIANGLE,
                                confidence=confidence,
                                start_index=i-window,
                                end_index=i,
                                price_level=np.mean(segment_low),
                                direction="up",
                                strength=breakout_dist,
                                target_price=close[i] + (np.max(segment_high) - np.min(segment_low)),
                                description=f"Ascending Triangle breakout pattern"
                            ))
        
        return patterns
    
    def detect_breakouts(self, df: pd.DataFrame) -> List[PatternSignal]:
        """Detect price breakouts from consolidation"""
        patterns = []
        
        if len(df) < 25:
            return patterns
        
        high = df['High'].values
        low = df['Low'].values
        close = df['Close'].values
        volume = df['Volume'].values if 'Volume' in df.columns else np.ones(len(df))
        
        window = 15
        for i in range(window, len(df) - 5):
            # Check consolidation range
            consol_high = np.max(high[i-window:i])
            consol_low = np.min(low[i-window:i])
            consol_range = consol_high - consol_low
            
            if consol_range > 0:
                # Check for breakout
                future_high = np.max(high[i:min(i+7, len(df))])
                future_low = np.min(low[i:min(i+7, len(df))])
                
                # Upside breakout
                if future_high > consol_high * 1.03 and close[i] > consol_high:
                    volume_surge = volume[i] / np.mean(volume[i-5:i]) if i >= 5 else 1.0
                    confidence = min(0.85, 0.6 + (volume_surge / 10) * 0.25)
                    
                    patterns.append(PatternSignal(
                        pattern_type=PatternType.BREAKOUT,
                        confidence=confidence,
                        start_index=i-window,
                        end_index=i,
                        price_level=consol_high,
                        direction="up",
                        strength=volume_surge,
                        target_price=consol_high + (consol_range * 1.5),
                        stop_loss=consol_low * 0.99,
                        description=f"Bullish breakout from {consol_low:.2f}-{consol_high:.2f}"
                    ))
        
        return patterns
    
    def detect_support_resistance(self, df: pd.DataFrame) -> List[PatternSignal]:
        """Detect support and resistance levels"""
        patterns = []
        
        if len(df) < 30:
            return patterns
        
        high = df['High'].values
        low = df['Low'].values
        
        # Find recent support levels (local minima)
        troughs = self._find_local_troughs(low, window=7, threshold=0.01)
        
        # Find recent resistance levels (local maxima)
        peaks = self._find_local_peaks(high, window=7, threshold=0.01)
        
        # Support bounces
        if len(troughs) >= 2:
            recent_trough = troughs[-1]
            support_level = low[recent_trough]
            
            # Check if price tested support multiple times
            tests = sum(1 for idx in troughs[-3:] if abs(low[idx] - support_level) < support_level * 0.01)
            
            if tests >= 2 and recent_trough < len(df) - 3:
                # Check if price bounced
                recent_high = np.max(high[recent_trough:min(recent_trough+5, len(df))])
                
                if recent_high > support_level * 1.02:
                    confidence = min(0.85, 0.7 + (tests / 3) * 0.15)
                    
                    patterns.append(PatternSignal(
                        pattern_type=PatternType.SUPPORT_BOUNCE,
                        confidence=confidence,
                        start_index=troughs[-2] if len(troughs) >= 2 else recent_trough,
                        end_index=recent_trough,
                        price_level=support_level,
                        direction="up",
                        strength=0.8,
                        target_price=recent_high * 1.02,
                        stop_loss=support_level * 0.98,
                        description=f"Support bounce at {support_level:.2f}"
                    ))
        
        return patterns
    
    def detect_wedges(self, df: pd.DataFrame) -> List[PatternSignal]:
        """Detect wedge patterns"""
        # Similar logic to triangles but with different slope characteristics
        return []
    
    def detect_channels(self, df: pd.DataFrame) -> List[PatternSignal]:
        """Detect price channels"""
        return []
    
    def detect_cup_handle(self, df: pd.DataFrame) -> List[PatternSignal]:
        """Detect cup and handle pattern"""
        return []
    
    def detect_flags(self, df: pd.DataFrame) -> List[PatternSignal]:
        """Detect flag patterns"""
        return []
    
    # Helper methods
    def _find_local_peaks(self, data: np.ndarray, window: int = 5, threshold: float = 0.01) -> List[int]:
        """Find local maximum peaks"""
        peaks = []
        
        for i in range(window, len(data) - window):
            if data[i] >= np.max(data[i-window:i+window]):
                # Confirm it's a significant peak
                if (data[i] - np.mean(data[i-window:i])) / np.mean(data[i-window:i]) > threshold:
                    peaks.append(i)
        
        # Remove consecutive peaks (keep highest)
        cleaned_peaks = []
        i = 0
        while i < len(peaks):
            if i + 1 < len(peaks) and peaks[i+1] - peaks[i] < window:
                if data[peaks[i]] > data[peaks[i+1]]:
                    cleaned_peaks.append(peaks[i])
                    i += 2
                else:
                    cleaned_peaks.append(peaks[i+1])
                    i += 2
            else:
                cleaned_peaks.append(peaks[i])
                i += 1
        
        return cleaned_peaks
    
    def _find_local_troughs(self, data: np.ndarray, window: int = 5, threshold: float = 0.01) -> List[int]:
        """Find local minimum troughs"""
        troughs = []
        
        for i in range(window, len(data) - window):
            if data[i] <= np.min(data[i-window:i+window]):
                # Confirm it's a significant trough
                if (np.mean(data[i-window:i]) - data[i]) / np.mean(data[i-window:i]) > threshold:
                    troughs.append(i)
        
        # Remove consecutive troughs (keep lowest)
        cleaned_troughs = []
        i = 0
        while i < len(troughs):
            if i + 1 < len(troughs) and troughs[i+1] - troughs[i] < window:
                if data[troughs[i]] < data[troughs[i+1]]:
                    cleaned_troughs.append(troughs[i])
                    i += 2
                else:
                    cleaned_troughs.append(troughs[i+1])
                    i += 2
            else:
                cleaned_troughs.append(troughs[i])
                i += 1
        
        return cleaned_troughs
    
    def _calculate_pattern_confidence(self, *factors: float) -> float:
        """Calculate pattern confidence from multiple factors"""
        # Combine factors (each between 0-1) with geometric mean
        valid_factors = [f for f in factors if 0 <= f <= 1]
        
        if not valid_factors:
            return 0.5
        
        # Geometric mean
        confidence = np.prod(valid_factors) ** (1 / len(valid_factors))
        return min(0.95, max(0.3, confidence))


class TechnicalFeatureExtractor:
    """Extract technical indicators as ML features"""
    
    @staticmethod
    def extract_all_features(df: pd.DataFrame) -> Dict[str, float]:
        """Extract 50+ technical features for ML"""
        features = {}
        
        if len(df) < 200:
            return features
        
        close = df['Close'].values
        high = df['High'].values
        low = df['Low'].values
        volume = df['Volume'].values if 'Volume' in df.columns else np.ones(len(df))
        
        # Trend Features
        trend_feats = TechnicalFeatureExtractor._extract_trend_features(close)
        features.update(trend_feats)
        
        # Momentum Features
        mom_feats = TechnicalFeatureExtractor._extract_momentum_features(close)
        features.update(mom_feats)
        
        # Volatility Features
        vol_feats = TechnicalFeatureExtractor._extract_volatility_features(close, high, low)
        features.update(vol_feats)
        
        # Volume Features
        volu_feats = TechnicalFeatureExtractor._extract_volume_features(volume, close)
        features.update(volu_feats)
        
        # Candle Pattern Features
        features.update(TechnicalFeatureExtractor._extract_candle_features(open_=df['Open'].values, high=high, low=low, close=close))

        # Additional indicators snapshot (last values)
        series = TechnicalFeatureExtractor.extract_indicator_series(df)
        # MACD
        macd_line = series.get('macd', {}).get('line', [])
        macd_signal = series.get('macd', {}).get('signal', [])
        macd_hist = series.get('macd', {}).get('hist', [])
        if macd_line:
            features['macd_line'] = float(macd_line[-1])
        if macd_signal:
            features['macd_signal'] = float(macd_signal[-1])
        if macd_hist:
            features['macd_hist'] = float(macd_hist[-1])
        # ADX
        adx = series.get('adx_14', [])
        if adx:
            features['adx_14'] = float(adx[-1])
        # Stochastic
        stoch_k = series.get('stoch', {}).get('k', [])
        stoch_d = series.get('stoch', {}).get('d', [])
        if stoch_k:
            features['stoch_k_14'] = float(stoch_k[-1])
        if stoch_d:
            features['stoch_d_14'] = float(stoch_d[-1])
        # Williams %R
        willr = series.get('williams_r', [])
        if willr:
            features['williams_r_14'] = float(willr[-1])
        # ROC, CCI
        roc10 = series.get('roc_10', [])
        if roc10:
            features['roc_10'] = float(roc10[-1])
        cci20 = series.get('cci_20', [])
        if cci20:
            features['cci_20'] = float(cci20[-1])
        # MFI
        mfi14 = series.get('mfi_14', [])
        if mfi14:
            features['mfi_14'] = float(mfi14[-1])
        
        return features

    @staticmethod
    def extract_indicator_series(df: pd.DataFrame) -> Dict:
        """Return time-series for key indicators for plotting and UI overlays."""
        if df is None or df.empty:
            return {}
        # Ensure required columns
        for col in ['Open', 'High', 'Low', 'Close']:
            if col not in df.columns:
                return {}
        volume = df['Volume'].values if 'Volume' in df.columns else np.ones(len(df))
        close = df['Close'].astype(float).values
        high = df['High'].astype(float).values
        low = df['Low'].astype(float).values
        open_ = df['Open'].astype(float).values

        s_close = pd.Series(close)
        dates = [pd.to_datetime(d).strftime('%Y-%m-%d') for d in df.index]

        # SMA/EMA
        sma20 = s_close.rolling(20).mean().tolist()
        sma50 = s_close.rolling(50).mean().tolist()
        sma200 = s_close.rolling(200).mean().tolist()
        ema12 = s_close.ewm(span=12, adjust=False).mean().tolist()
        ema26 = s_close.ewm(span=26, adjust=False).mean().tolist()

        # MACD
        macd_line_series = (pd.Series(ema12) - pd.Series(ema26)).tolist()
        macd_signal_series = pd.Series(macd_line_series).ewm(span=9, adjust=False).mean().tolist()
        macd_hist_series = (pd.Series(macd_line_series) - pd.Series(macd_signal_series)).tolist()

        # RSI
        rsi_series = TechnicalFeatureExtractor._rsi_series(close, period=14)

        # Bollinger Bands (20, 2)
        bb_mid = s_close.rolling(20).mean()
        bb_std = s_close.rolling(20).std()
        bb_upper = (bb_mid + 2 * bb_std).tolist()
        bb_lower = (bb_mid - 2 * bb_std).tolist()
        bb_middle = bb_mid.tolist()

        # Keltner Channel (EMA20 +/- 2 * ATR(14))
        ema20 = s_close.ewm(span=20, adjust=False).mean()
        atr14_full = TechnicalFeatureExtractor._atr_series(high, low, close, period=14)
        kelt_mid = ema20.tolist()
        kelt_upper = (ema20 + 2 * pd.Series(atr14_full)).tolist()
        kelt_lower = (ema20 - 2 * pd.Series(atr14_full)).tolist()

        # Stochastic %K and %D (14,3)
        stoch_k, stoch_d = TechnicalFeatureExtractor._stochastic_series(high, low, close, k_period=14, d_period=3)

        # Williams %R (14)
        willr = TechnicalFeatureExtractor._williams_r_series(high, low, close, period=14)

        # ADX (14)
        adx14 = TechnicalFeatureExtractor._adx_series(high, low, close, period=14)

        # ROC (10)
        roc10 = TechnicalFeatureExtractor._roc_series(close, period=10)

        # CCI (20)
        cci20 = TechnicalFeatureExtractor._cci_series(high, low, close, period=20)

        # OBV
        obv_series = TechnicalFeatureExtractor._obv_series(close, volume)

        # MFI (14)
        mfi14 = TechnicalFeatureExtractor._mfi_series(high, low, close, volume, period=14)

        # Pivot points (last)
        pivots = TechnicalFeatureExtractor._pivot_levels(high, low, close)

        # Fibonacci levels (based on recent 120 bars swing)
        fib = TechnicalFeatureExtractor._fibonacci_levels(high, low, lookback=120)

        def clean_list(lst):
            return [float(x) if pd.notna(x) else None for x in lst]

        return {
            "dates": dates,
            "close": clean_list(close.tolist()),
            "sma20": clean_list(sma20),
            "sma50": clean_list(sma50),
            "sma200": clean_list(sma200),
            "ema12": clean_list(ema12),
            "ema26": clean_list(ema26),
            "macd": {"line": clean_list(macd_line_series), "signal": clean_list(macd_signal_series), "hist": clean_list(macd_hist_series)},
            "rsi_14": clean_list(rsi_series),
            "bb": {"upper": clean_list(bb_upper), "middle": clean_list(bb_middle), "lower": clean_list(bb_lower)},
            "keltner": {"upper": clean_list(kelt_upper), "middle": clean_list(kelt_mid), "lower": clean_list(kelt_lower)},
            "stoch": {"k": clean_list(stoch_k), "d": clean_list(stoch_d)},
            "williams_r": clean_list(willr),
            "adx_14": clean_list(adx14),
            "roc_10": clean_list(roc10),
            "cci_20": clean_list(cci20),
            "obv": clean_list(obv_series),
            "mfi_14": clean_list(mfi14),
            "levels": {"pivots": pivots, "fibonacci": fib}
        }
    
    @staticmethod
    def _extract_trend_features(close: np.ndarray) -> Dict[str, float]:
        """Extract trend-based features"""
        features = {}
        
        # Moving averages
        ma_20 = pd.Series(close).rolling(20).mean().iloc[-1] if len(close) >= 20 else np.nan
        ma_50 = pd.Series(close).rolling(50).mean().iloc[-1] if len(close) >= 50 else np.nan
        ma_200 = pd.Series(close).rolling(200).mean().iloc[-1] if len(close) >= 200 else np.nan
        
        features['ma_20'] = ma_20 if not np.isnan(ma_20) else close[-1]
        features['ma_50'] = ma_50 if not np.isnan(ma_50) else close[-1]
        features['ma_200'] = ma_200 if not np.isnan(ma_200) else close[-1]
        
        # MA ratios
        if not np.isnan(ma_50):
            features['price_ma20_ratio'] = close[-1] / ma_20
            features['ma20_ma50_ratio'] = ma_20 / ma_50
            features['ma50_ma200_ratio'] = ma_50 / ma_200
        
        # EMA slopes
        ema_12 = pd.Series(close).ewm(span=12, adjust=False).mean()
        ema_26 = pd.Series(close).ewm(span=26, adjust=False).mean()
        
        features['ema_slope_12'] = float((ema_12.iloc[-1] - ema_12.iloc[-5]) / ema_12.iloc[-5])
        features['macd'] = float(ema_12.iloc[-1] - ema_26.iloc[-1])
        
        return features
    
    @staticmethod
    def _extract_momentum_features(close: np.ndarray) -> Dict[str, float]:
        """Extract momentum features"""
        features = {}
        
        # RSI
        rsi = TechnicalFeatureExtractor._calculate_rsi(close, 14)
        features['rsi_14'] = rsi if not np.isnan(rsi) else 50.0
        
        # Rate of Change
        roc = (close[-1] - close[-11]) / close[-11] * 100 if len(close) > 11 else 0
        features['roc_10'] = roc
        
        # Momentum
        momentum = close[-1] - close[-11] if len(close) > 11 else 0
        features['momentum_10'] = momentum
        
        return features
    
    @staticmethod
    def _extract_volatility_features(close: np.ndarray, high: np.ndarray, low: np.ndarray) -> Dict[str, float]:
        """Extract volatility features"""
        features = {}
        
        # ATR
        atr = TechnicalFeatureExtractor._calculate_atr(high, low, close, 14)
        features['atr_14'] = atr
        
        # Standard deviation
        std_20 = pd.Series(close).rolling(20).std().iloc[-1] if len(close) >= 20 else np.std(close)
        features['std_20'] = std_20
        
        # Bollinger Bands
        bb_middle = pd.Series(close).rolling(20).mean().iloc[-1]
        bb_std = std_20
        features['bb_upper'] = bb_middle + (bb_std * 2)
        features['bb_lower'] = bb_middle - (bb_std * 2)
        features['bb_width'] = features['bb_upper'] - features['bb_lower']
        
        return features
    
    @staticmethod
    def _extract_volume_features(volume: np.ndarray, close: np.ndarray) -> Dict[str, float]:
        """Extract volume features"""
        features = {}
        
        # Volume trend
        vol_20_mean = np.mean(volume[-20:]) if len(volume) >= 20 else np.mean(volume)
        features['volume_current'] = volume[-1]
        features['volume_ratio'] = volume[-1] / vol_20_mean if vol_20_mean > 0 else 1.0
        
        # OBV (simplified)
        obv = 0
        for i in range(len(close)):
            if close[i] > (close[i-1] if i > 0 else close[i]):
                obv += volume[i]
            elif close[i] < (close[i-1] if i > 0 else close[i]):
                obv -= volume[i]
        
        features['obv'] = float(obv)
        
        return features
    
    @staticmethod
    def _extract_candle_features(open_: np.ndarray, high: np.ndarray, low: np.ndarray, close: np.ndarray) -> Dict[str, float]:
        """Extract candle pattern features"""
        features = {}
        
        # Recent candles
        bodies = [abs(close[i] - open_[i]) / open_[i] for i in range(-5, 0)]
        features['avg_body_size'] = np.mean(bodies) if bodies else 0
        features['last_candle_body'] = bodies[-1] if bodies else 0
        
        # Wicks
        upper_wicks = [high[i] - max(open_[i], close[i]) for i in range(-5, 0)]
        lower_wicks = [min(open_[i], close[i]) - low[i] for i in range(-5, 0)]
        
        features['avg_upper_wick'] = np.mean(upper_wicks)
        features['avg_lower_wick'] = np.mean(lower_wicks)
        
        return features
    
    @staticmethod
    def _calculate_rsi(prices: np.ndarray, period: int = 14) -> float:
        """Calculate RSI indicator"""
        if len(prices) < period + 1:
            return 50.0
        
        deltas = np.diff(prices)
        seed = deltas[:period+1]
        
        up = seed[seed >= 0].sum() / period
        down = -seed[seed < 0].sum() / period
        
        rs = up / down if down != 0 else 0
        rsi = 100 - (100 / (1 + rs))
        
        return rsi
    
    @staticmethod
    def _calculate_atr(high: np.ndarray, low: np.ndarray, close: np.ndarray, period: int = 14) -> float:
        """Calculate Average True Range"""
        if len(high) < period:
            return 0.0
        
        tr1 = high - low
        tr2 = np.abs(high[:-1] - close[:-1]) if len(close) > 1 else np.zeros(len(high))
        tr3 = np.abs(low[:-1] - close[:-1]) if len(close) > 1 else np.zeros(len(high))
        
        # Pad to match length
        if isinstance(tr2, (int, float)):
            tr2 = np.zeros(len(high))
        if isinstance(tr3, (int, float)):
            tr3 = np.zeros(len(high))
        
        # Ensure all arrays same length
        min_len = min(len(tr1), len(tr2), len(tr3))
        tr1 = tr1[-min_len:]
        tr2 = tr2[-min_len:] if len(tr2) > 0 else np.zeros(min_len)
        tr3 = tr3[-min_len:] if len(tr3) > 0 else np.zeros(min_len)
        
        tr = np.maximum(tr1, np.maximum(tr2, tr3))
        atr = np.mean(tr[-period:])
        
        return atr

    # --- Series helpers for indicators ---
    @staticmethod
    def _rsi_series(close: np.ndarray, period: int = 14) -> List[float]:
        if len(close) < period + 1:
            return [None] * len(close)
        deltas = np.diff(close)
        gains = np.where(deltas > 0, deltas, 0.0)
        losses = np.where(deltas < 0, -deltas, 0.0)
        gain_ema = pd.Series(gains).ewm(alpha=1/period, adjust=False).mean()
        loss_ema = pd.Series(losses).ewm(alpha=1/period, adjust=False).mean()
        rs = gain_ema / (loss_ema + 1e-12)
        rsi = 100 - (100 / (1 + rs))
        rsi = rsi.reindex(range(len(close)-1)).tolist()
        return [None] + [float(x) if pd.notna(x) else None for x in rsi]

    @staticmethod
    def _atr_series(high: np.ndarray, low: np.ndarray, close: np.ndarray, period: int = 14) -> List[float]:
        if len(close) < 2:
            return [0.0] * len(close)
        high_series = pd.Series(high)
        low_series = pd.Series(low)
        close_series = pd.Series(close)
        prev_close = close_series.shift(1)
        tr = pd.concat([
            high_series - low_series,
            (high_series - prev_close).abs(),
            (low_series - prev_close).abs()
        ], axis=1).max(axis=1)
        atr = tr.rolling(window=period, min_periods=period).mean()
        return [float(x) if pd.notna(x) else None for x in atr.tolist()]

    @staticmethod
    def _stochastic_series(high: np.ndarray, low: np.ndarray, close: np.ndarray, k_period: int = 14, d_period: int = 3) -> Tuple[List[float], List[float]]:
        high_s = pd.Series(high)
        low_s = pd.Series(low)
        close_s = pd.Series(close)
        lowest_low = low_s.rolling(window=k_period, min_periods=k_period).min()
        highest_high = high_s.rolling(window=k_period, min_periods=k_period).max()
        k = 100 * (close_s - lowest_low) / (highest_high - lowest_low + 1e-12)
        d = k.rolling(window=d_period, min_periods=d_period).mean()
        k_list = [float(x) if pd.notna(x) else None for x in k.tolist()]
        d_list = [float(x) if pd.notna(x) else None for x in d.tolist()]
        return k_list, d_list

    @staticmethod
    def _williams_r_series(high: np.ndarray, low: np.ndarray, close: np.ndarray, period: int = 14) -> List[float]:
        high_s = pd.Series(high)
        low_s = pd.Series(low)
        close_s = pd.Series(close)
        highest_high = high_s.rolling(window=period, min_periods=period).max()
        lowest_low = low_s.rolling(window=period, min_periods=period).min()
        willr = -100 * (highest_high - close_s) / (highest_high - lowest_low + 1e-12)
        return [float(x) if pd.notna(x) else None for x in willr.tolist()]

    @staticmethod
    def _adx_series(high: np.ndarray, low: np.ndarray, close: np.ndarray, period: int = 14) -> List[float]:
        high_s = pd.Series(high)
        low_s = pd.Series(low)
        close_s = pd.Series(close)
        plus_dm = (high_s.diff()).clip(lower=0)
        minus_dm = (-low_s.diff()).clip(lower=0)
        tr = pd.concat([
            high_s - low_s,
            (high_s - close_s.shift(1)).abs(),
            (low_s - close_s.shift(1)).abs()
        ], axis=1).max(axis=1)
        atr = tr.rolling(window=period, min_periods=period).mean()
        plus_di = 100 * (plus_dm.rolling(window=period, min_periods=period).mean() / (atr + 1e-12))
        minus_di = 100 * (minus_dm.rolling(window=period, min_periods=period).mean() / (atr + 1e-12))
        dx = (abs(plus_di - minus_di) / (plus_di + minus_di + 1e-12)) * 100
        adx = dx.rolling(window=period, min_periods=period).mean()
        return [float(x) if pd.notna(x) else None for x in adx.tolist()]

    @staticmethod
    def _roc_series(close: np.ndarray, period: int = 10) -> List[float]:
        close_s = pd.Series(close)
        roc = close_s.pct_change(periods=period) * 100
        return [float(x) if pd.notna(x) else None for x in roc.tolist()]

    @staticmethod
    def _cci_series(high: np.ndarray, low: np.ndarray, close: np.ndarray, period: int = 20) -> List[float]:
        tp = (pd.Series(high) + pd.Series(low) + pd.Series(close)) / 3
        sma = tp.rolling(window=period, min_periods=period).mean()
        mad = (tp - sma).abs().rolling(window=period, min_periods=period).mean()
        cci = (tp - sma) / (0.015 * (mad + 1e-12))
        return [float(x) if pd.notna(x) else None for x in cci.tolist()]

    @staticmethod
    def _obv_series(close: np.ndarray, volume: np.ndarray) -> List[float]:
        obv = [0.0]
        for i in range(1, len(close)):
            if close[i] > close[i-1]:
                obv.append(obv[-1] + float(volume[i]))
            elif close[i] < close[i-1]:
                obv.append(obv[-1] - float(volume[i]))
            else:
                obv.append(obv[-1])
        return obv

    @staticmethod
    def _mfi_series(high: np.ndarray, low: np.ndarray, close: np.ndarray, volume: np.ndarray, period: int = 14) -> List[float]:
        tp = (pd.Series(high) + pd.Series(low) + pd.Series(close)) / 3
        rmf = tp * pd.Series(volume)
        pos_flow = []
        neg_flow = []
        for i in range(1, len(tp)):
            if tp.iloc[i] > tp.iloc[i-1]:
                pos_flow.append(rmf.iloc[i])
                neg_flow.append(0)
            else:
                pos_flow.append(0)
                neg_flow.append(rmf.iloc[i])
        pos_mf = pd.Series(pos_flow).rolling(window=period, min_periods=period).sum()
        neg_mf = pd.Series(neg_flow).rolling(window=period, min_periods=period).sum()
        mfi = 100 - (100 / (1 + (pos_mf / (neg_mf + 1e-12))))
        mfi = mfi.reindex(range(len(close)-1)).tolist()
        return [None] + [float(x) if pd.notna(x) else None for x in mfi]

    @staticmethod
    def _pivot_levels(high: np.ndarray, low: np.ndarray, close: np.ndarray) -> Dict[str, float]:
        if len(close) < 2:
            return {"pp": 0, "r1": 0, "r2": 0, "r3": 0, "s1": 0, "s2": 0, "s3": 0}
        h = float(high[-2])
        l = float(low[-2])
        c = float(close[-2])
        pp = (h + l + c) / 3
        r1 = 2*pp - l
        s1 = 2*pp - h
        r2 = pp + (h - l)
        s2 = pp - (h - l)
        r3 = h + 2*(pp - l)
        s3 = l - 2*(h - pp)
        return {"pp": pp, "r1": r1, "r2": r2, "r3": r3, "s1": s1, "s2": s2, "s3": s3}

    @staticmethod
    def _fibonacci_levels(high: np.ndarray, low: np.ndarray, lookback: int = 120) -> Dict:
        n = len(high)
        if n == 0:
            return {"levels": {}, "swing_high": 0, "swing_low": 0}
        start = max(0, n - lookback)
        segment_high = float(np.max(high[start:]))
        segment_low = float(np.min(low[start:]))
        diff = segment_high - segment_low
        levels = {
            "0.236": segment_high - 0.236 * diff,
            "0.382": segment_high - 0.382 * diff,
            "0.5": segment_high - 0.5 * diff,
            "0.618": segment_high - 0.618 * diff,
            "0.786": segment_high - 0.786 * diff,
        }
        return {"levels": levels, "swing_high": segment_high, "swing_low": segment_low}


# Convenience function
def extract_research_features(df: pd.DataFrame) -> Dict:
    """Extract all features for research/ML"""
    detector = ChartPatternDetector()
    extractor = TechnicalFeatureExtractor()
    
    patterns = detector.detect_all_patterns(df)
    features = extractor.extract_all_features(df)
    series = extractor.extract_indicator_series(df)
    
    return {
        "patterns": [
            {
                "type": p.pattern_type.value,
                "confidence": p.confidence,
                "price_level": p.price_level,
                "direction": p.direction,
                "target_price": p.target_price,
                "stop_loss": p.stop_loss,
                "description": p.description
            }
            for p in patterns
        ],
        "technical_features": features,
        "series": series,
        "pattern_count": len(patterns)
    }
