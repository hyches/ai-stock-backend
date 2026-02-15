"""
Professional Multi-Model ML Engine for Stock Prediction
========================================================
Implements ensemble of XGBoost, LightGBM, CatBoost, ExtraTrees, and LSTM
with market regime detection and advanced feature engineering.
"""

import os
import json
import joblib
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Any
from datetime import datetime
from dataclasses import dataclass
from enum import Enum
import warnings
warnings.filterwarnings('ignore')

# ML Libraries
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor, ExtraTreesClassifier, ExtraTreesRegressor
from sklearn.linear_model import Ridge, LogisticRegression
from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import accuracy_score, mean_squared_error, f1_score, precision_score
from sklearn.preprocessing import StandardScaler

# Advanced Gradient Boosting
try:
    import xgboost as xgb
    HAS_XGBOOST = True
except ImportError:
    HAS_XGBOOST = False

try:
    import lightgbm as lgb
    HAS_LIGHTGBM = True
except ImportError:
    HAS_LIGHTGBM = False

try:
    from catboost import CatBoostClassifier, CatBoostRegressor
    HAS_CATBOOST = True
except ImportError:
    HAS_CATBOOST = False

# Deep Learning for LSTM
try:
    import tensorflow as tf
    from tensorflow.keras.models import Sequential, load_model
    from tensorflow.keras.layers import LSTM, Dense, Dropout, BatchNormalization
    from tensorflow.keras.callbacks import EarlyStopping
    HAS_TENSORFLOW = True
except ImportError:
    HAS_TENSORFLOW = False

# Directory to save models
MODEL_DIR = "trained_models"
os.makedirs(MODEL_DIR, exist_ok=True)


from app.services.explainability import xai_service
from app.services.ml_auto_retrainer import ml_auto_retrainer

class MarketRegime(Enum):
    """Market regime classification"""
    STRONG_UPTREND = "strong_uptrend"
    UPTREND = "uptrend"
    RANGING = "ranging"
    DOWNTREND = "downtrend"
    STRONG_DOWNTREND = "strong_downtrend"
    BREAKOUT_UP = "breakout_up"
    BREAKOUT_DOWN = "breakout_down"
    HIGH_VOLATILITY = "high_volatility"


@dataclass
class ModelResult:
    """Container for individual model predictions"""
    name: str
    signal: str  # BUY, SELL, HOLD
    confidence: float
    prob_up: float
    prob_down: float
    predicted_return: float
    accuracy: float  # Training accuracy


@dataclass
class EnsembleResult:
    """Container for ensemble prediction"""
    signal: str
    confidence: float
    prob_up: float
    prob_down: float
    predicted_return: float
    individual_models: List[ModelResult]
    regime: MarketRegime
    feature_importance: Dict[str, float]


class AdvancedFeatureEngineering:
    """
    Professional-grade feature engineering with 50+ technical indicators
    """
    
    @staticmethod
    def compute_all_features(df: pd.DataFrame) -> pd.DataFrame:
        """Compute comprehensive feature set for ML training"""
        data = df.copy()
        
        close = data['Close']
        high = data['High']
        low = data['Low']
        open_ = data['Open']
        volume = data['Volume'] if 'Volume' in data.columns else pd.Series(1, index=data.index)
        
        # ==================== PRICE ACTION FEATURES ====================
        
        # Returns at multiple horizons
        for period in [1, 2, 3, 5, 10, 21, 63]:
            data[f'ret_{period}d'] = close.pct_change(period)
        
        # Log returns
        data['log_ret_1d'] = np.log(close / close.shift(1))
        
        # Price momentum
        data['momentum_5'] = close - close.shift(5)
        data['momentum_10'] = close - close.shift(10)
        data['momentum_21'] = close - close.shift(21)
        
        # ==================== MOVING AVERAGES ====================
        
        for period in [5, 10, 20, 50, 100, 200]:
            data[f'sma_{period}'] = close.rolling(period).mean()
            data[f'ema_{period}'] = close.ewm(span=period, adjust=False).mean()
            # Price to MA ratio (more important for ML)
            data[f'price_sma_{period}_ratio'] = close / data[f'sma_{period}']
        
        # MA Crossovers (binary signals)
        data['sma_5_20_cross'] = (data['sma_5'] > data['sma_20']).astype(int)
        data['sma_20_50_cross'] = (data['sma_20'] > data['sma_50']).astype(int)
        data['sma_50_200_cross'] = (data['sma_50'] > data['sma_200']).astype(int)
        
        # ==================== VOLATILITY INDICATORS ====================
        
        # Standard Deviation
        for period in [5, 10, 20]:
            data[f'std_{period}'] = close.pct_change().rolling(period).std()
        
        # Parkinson Volatility (using High-Low)
        data['parkinson_vol'] = np.sqrt(
            (1 / (4 * np.log(2))) * ((np.log(high / low)) ** 2).rolling(20).mean()
        )
        
        # Garman-Klass Volatility
        log_hl = np.log(high / low) ** 2
        log_co = np.log(close / open_) ** 2
        data['gk_vol'] = np.sqrt(0.5 * log_hl - (2 * np.log(2) - 1) * log_co).rolling(20).mean()
        
        # ATR (Average True Range)
        tr1 = high - low
        tr2 = abs(high - close.shift(1))
        tr3 = abs(low - close.shift(1))
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        data['atr_14'] = tr.rolling(14).mean()
        data['atr_ratio'] = data['atr_14'] / close  # Normalized ATR
        
        # ==================== RSI VARIANTS ====================
        
        for period in [7, 14, 21]:
            delta = close.diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
            rs = gain / loss
            data[f'rsi_{period}'] = 100 - (100 / (1 + rs))
        
        # RSI Divergence
        data['rsi_slope'] = data['rsi_14'].diff(5)
        data['price_slope'] = close.pct_change(5)
        data['rsi_divergence'] = np.sign(data['rsi_slope']) != np.sign(data['price_slope'])
        
        # ==================== MACD ====================
        
        exp12 = close.ewm(span=12, adjust=False).mean()
        exp26 = close.ewm(span=26, adjust=False).mean()
        data['macd'] = exp12 - exp26
        data['macd_signal'] = data['macd'].ewm(span=9, adjust=False).mean()
        data['macd_hist'] = data['macd'] - data['macd_signal']
        data['macd_hist_slope'] = data['macd_hist'].diff(3)
        
        # ==================== BOLLINGER BANDS ====================
        
        sma20 = close.rolling(20).mean()
        std20 = close.rolling(20).std()
        data['bb_upper'] = sma20 + 2 * std20
        data['bb_lower'] = sma20 - 2 * std20
        data['bb_width'] = (data['bb_upper'] - data['bb_lower']) / sma20
        data['bb_position'] = (close - data['bb_lower']) / (data['bb_upper'] - data['bb_lower'])
        
        # Bollinger Squeeze (volatility contraction)
        data['bb_squeeze'] = data['bb_width'] < data['bb_width'].rolling(50).mean()
        
        # ==================== STOCHASTIC OSCILLATOR ====================
        
        for period in [14, 21]:
            low_min = low.rolling(period).min()
            high_max = high.rolling(period).max()
            data[f'stoch_k_{period}'] = 100 * (close - low_min) / (high_max - low_min)
            data[f'stoch_d_{period}'] = data[f'stoch_k_{period}'].rolling(3).mean()
        
        # ==================== WILLIAMS %R ====================
        
        data['williams_r'] = -100 * (high.rolling(14).max() - close) / (high.rolling(14).max() - low.rolling(14).min())
        
        # ==================== CCI (Commodity Channel Index) ====================
        
        typical_price = (high + low + close) / 3
        sma_tp = typical_price.rolling(20).mean()
        mean_dev = typical_price.rolling(20).apply(lambda x: np.abs(x - x.mean()).mean())
        data['cci'] = (typical_price - sma_tp) / (0.015 * mean_dev)
        
        # ==================== ADX (Average Directional Index) ====================
        
        plus_dm = high.diff()
        minus_dm = -low.diff()
        plus_dm[plus_dm < 0] = 0
        minus_dm[minus_dm < 0] = 0
        
        tr_smooth = tr.rolling(14).sum()
        plus_di = 100 * (plus_dm.rolling(14).sum() / tr_smooth)
        minus_di = 100 * (minus_dm.rolling(14).sum() / tr_smooth)
        
        dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di)
        data['adx'] = dx.rolling(14).mean()
        data['plus_di'] = plus_di
        data['minus_di'] = minus_di
        data['di_diff'] = plus_di - minus_di
        
        # ==================== VOLUME INDICATORS ====================
        
        # Volume SMA and ratio
        data['vol_sma_20'] = volume.rolling(20).mean()
        data['vol_ratio'] = volume / data['vol_sma_20']
        
        # On-Balance Volume
        obv = (np.sign(close.diff()) * volume).cumsum()
        data['obv'] = obv
        data['obv_sma'] = obv.rolling(20).mean()
        data['obv_ratio'] = obv / data['obv_sma']
        
        # Money Flow Index
        typical_price = (high + low + close) / 3
        raw_money_flow = typical_price * volume
        positive_flow = raw_money_flow.where(typical_price > typical_price.shift(1), 0).rolling(14).sum()
        negative_flow = raw_money_flow.where(typical_price < typical_price.shift(1), 0).rolling(14).sum()
        mfi = 100 - (100 / (1 + positive_flow / negative_flow))
        data['mfi'] = mfi
        
        # VWAP approximation (cumulative)
        data['vwap'] = (volume * typical_price).cumsum() / volume.cumsum()
        data['price_vwap_ratio'] = close / data['vwap']
        
        # ==================== ICHIMOKU CLOUD ====================
        
        period9_high = high.rolling(9).max()
        period9_low = low.rolling(9).min()
        data['tenkan_sen'] = (period9_high + period9_low) / 2
        
        period26_high = high.rolling(26).max()
        period26_low = low.rolling(26).min()
        data['kijun_sen'] = (period26_high + period26_low) / 2
        
        data['senkou_span_a'] = ((data['tenkan_sen'] + data['kijun_sen']) / 2).shift(26)
        
        period52_high = high.rolling(52).max()
        period52_low = low.rolling(52).min()
        data['senkou_span_b'] = ((period52_high + period52_low) / 2).shift(26)
        
        data['price_above_cloud'] = (close > data[['senkou_span_a', 'senkou_span_b']].max(axis=1)).astype(int)
        data['price_below_cloud'] = (close < data[['senkou_span_a', 'senkou_span_b']].min(axis=1)).astype(int)
        
        # ==================== CANDLESTICK PATTERNS ====================
        
        body = abs(close - open_)
        range_ = high - low
        upper_wick = high - pd.concat([close, open_], axis=1).max(axis=1)
        lower_wick = pd.concat([close, open_], axis=1).min(axis=1) - low
        
        data['body_ratio'] = body / range_
        data['upper_wick_ratio'] = upper_wick / range_
        data['lower_wick_ratio'] = lower_wick / range_
        
        # Doji
        data['is_doji'] = (body / range_ < 0.1).astype(int)
        
        # Hammer/Shooting Star
        data['is_hammer'] = ((lower_wick > 2 * body) & (upper_wick < body)).astype(int)
        data['is_shooting_star'] = ((upper_wick > 2 * body) & (lower_wick < body)).astype(int)
        
        # Engulfing
        data['bullish_engulfing'] = ((close > open_) & (close.shift(1) < open_.shift(1)) & 
                                     (close > open_.shift(1)) & (open_ < close.shift(1))).astype(int)
        data['bearish_engulfing'] = ((close < open_) & (close.shift(1) > open_.shift(1)) & 
                                     (close < open_.shift(1)) & (open_ > close.shift(1))).astype(int)
        
        # ==================== SUPPORT/RESISTANCE DISTANCE ====================
        
        recent_high = high.rolling(20).max()
        recent_low = low.rolling(20).min()
        data['dist_to_resistance'] = (recent_high - close) / close
        data['dist_to_support'] = (close - recent_low) / close
        
        # 52-week high/low distance
        high_52w = high.rolling(252).max()
        low_52w = low.rolling(252).min()
        data['dist_52w_high'] = (high_52w - close) / close
        data['dist_52w_low'] = (close - low_52w) / close
        
        # ==================== TEMPORAL FEATURES ====================
        
        if isinstance(data.index, pd.DatetimeIndex):
            data['day_of_week'] = data.index.dayofweek
            data['month'] = data.index.month
            data['quarter'] = data.index.quarter
            # Cyclical encoding
            data['day_sin'] = np.sin(2 * np.pi * data['day_of_week'] / 5)
            data['day_cos'] = np.cos(2 * np.pi * data['day_of_week'] / 5)
            data['month_sin'] = np.sin(2 * np.pi * data['month'] / 12)
            data['month_cos'] = np.cos(2 * np.pi * data['month'] / 12)
        
        # ==================== HIGHER/LOWER CONSECUTIVE DAYS ====================
        
        data['higher_close'] = (close > close.shift(1)).astype(int)
        data['lower_close'] = (close < close.shift(1)).astype(int)
        data['consecutive_up'] = data['higher_close'].groupby((data['higher_close'] != data['higher_close'].shift()).cumsum()).cumsum()
        data['consecutive_down'] = data['lower_close'].groupby((data['lower_close'] != data['lower_close'].shift()).cumsum()).cumsum()
        
        # ==================== CLEAN UP ====================
        
        # Define feature columns (exclude raw OHLCV and target columns)
        exclude_cols = ['Open', 'High', 'Low', 'Close', 'Volume', 'Adj Close', 'Date']
        feature_cols = [c for c in data.columns if c not in exclude_cols]
        
        # Replace infinities and drop NaN
        result = data[feature_cols].replace([np.inf, -np.inf], np.nan)
        
        return result
    
    @staticmethod
    def get_feature_names() -> List[str]:
        """Return list of expected feature names"""
        return [
            'ret_1d', 'ret_2d', 'ret_3d', 'ret_5d', 'ret_10d', 'ret_21d', 'ret_63d',
            'log_ret_1d', 'momentum_5', 'momentum_10', 'momentum_21',
            'sma_5', 'sma_10', 'sma_20', 'sma_50', 'sma_100', 'sma_200',
            'ema_5', 'ema_10', 'ema_20', 'ema_50', 'ema_100', 'ema_200',
            'price_sma_5_ratio', 'price_sma_10_ratio', 'price_sma_20_ratio',
            'price_sma_50_ratio', 'price_sma_100_ratio', 'price_sma_200_ratio',
            'sma_5_20_cross', 'sma_20_50_cross', 'sma_50_200_cross',
            'std_5', 'std_10', 'std_20', 'parkinson_vol', 'gk_vol', 'atr_14', 'atr_ratio',
            'rsi_7', 'rsi_14', 'rsi_21', 'rsi_slope', 'rsi_divergence',
            'macd', 'macd_signal', 'macd_hist', 'macd_hist_slope',
            'bb_upper', 'bb_lower', 'bb_width', 'bb_position', 'bb_squeeze',
            'stoch_k_14', 'stoch_d_14', 'stoch_k_21', 'stoch_d_21',
            'williams_r', 'cci', 'adx', 'plus_di', 'minus_di', 'di_diff',
            'vol_sma_20', 'vol_ratio', 'obv', 'obv_sma', 'obv_ratio', 'mfi',
            'vwap', 'price_vwap_ratio',
            'tenkan_sen', 'kijun_sen', 'senkou_span_a', 'senkou_span_b',
            'price_above_cloud', 'price_below_cloud',
            'body_ratio', 'upper_wick_ratio', 'lower_wick_ratio',
            'is_doji', 'is_hammer', 'is_shooting_star',
            'bullish_engulfing', 'bearish_engulfing',
            'dist_to_resistance', 'dist_to_support', 'dist_52w_high', 'dist_52w_low',
            'day_of_week', 'month', 'quarter', 'day_sin', 'day_cos', 'month_sin', 'month_cos',
            'higher_close', 'lower_close', 'consecutive_up', 'consecutive_down'
        ]


class RegimeDetector:
    """
    Detects market regime for adaptive model selection
    """
    
    @staticmethod
    def detect_regime(df: pd.DataFrame) -> Tuple[MarketRegime, Dict[str, float]]:
        """Detect current market regime based on indicators"""
        close = df['Close']
        high = df['High']
        low = df['Low']
        
        # Calculate key indicators
        sma_20 = close.rolling(20).mean().iloc[-1]
        sma_50 = close.rolling(50).mean().iloc[-1]
        sma_200 = close.rolling(200).mean().iloc[-1] if len(df) >= 200 else sma_50
        
        # ADX for trend strength
        tr = (high - low).rolling(14).mean()
        plus_dm = high.diff().clip(lower=0).rolling(14).sum()
        minus_dm = (-low.diff()).clip(lower=0).rolling(14).sum()
        dx = 100 * abs(plus_dm - minus_dm) / (plus_dm + minus_dm)
        adx = dx.rolling(14).mean().iloc[-1] if len(df) >= 28 else 20
        
        # Volatility
        daily_vol = close.pct_change().rolling(20).std().iloc[-1]
        avg_vol = close.pct_change().rolling(60).std().iloc[-1] if len(df) >= 60 else daily_vol
        vol_ratio = daily_vol / avg_vol if avg_vol > 0 else 1
        
        # Bollinger Band Width
        bb_width = (close.rolling(20).std() * 4 / close.rolling(20).mean()).iloc[-1]
        avg_bb_width = (close.rolling(50).std() * 4 / close.rolling(50).mean()).iloc[-1] if len(df) >= 50 else bb_width
        
        current = close.iloc[-1]
        
        # Regime classification logic
        regime_scores = {
            'trend_strength': float(adx),
            'volatility_ratio': float(vol_ratio),
            'price_vs_sma20': float(current / sma_20),
            'price_vs_sma50': float(current / sma_50),
            'bb_squeeze': float(bb_width < avg_bb_width * 0.8),
            'bb_expansion': float(bb_width > avg_bb_width * 1.5)
        }
        
        # Decision tree for regime
        if vol_ratio > 2.0:
            regime = MarketRegime.HIGH_VOLATILITY
        elif adx > 30:
            if current > sma_20 > sma_50:
                regime = MarketRegime.STRONG_UPTREND
            elif current < sma_20 < sma_50:
                regime = MarketRegime.STRONG_DOWNTREND
            elif current > sma_20:
                regime = MarketRegime.UPTREND
            else:
                regime = MarketRegime.DOWNTREND
        elif bb_width > avg_bb_width * 1.5:
            if current > sma_20:
                regime = MarketRegime.BREAKOUT_UP
            else:
                regime = MarketRegime.BREAKOUT_DOWN
        else:
            regime = MarketRegime.RANGING
        
        return regime, regime_scores


class BaseMLModel:
    """Base class for ML models"""
    
    def __init__(self, name: str):
        self.name = name
        self.classifier = None
        self.regressor = None
        self.scaler = StandardScaler()
        self.accuracy = 0.0
        self.feature_names = []
    
    def train(self, X: np.ndarray, y_cls: np.ndarray, y_reg: np.ndarray, feature_names: List[str]) -> Dict:
        raise NotImplementedError
    
    def predict(self, X: np.ndarray) -> ModelResult:
        raise NotImplementedError
    
    def save(self, path: str):
        joblib.dump({
            'classifier': self.classifier,
            'regressor': self.regressor,
            'scaler': self.scaler,
            'accuracy': self.accuracy,
            'feature_names': self.feature_names
        }, path)
    
    def load(self, path: str) -> bool:
        if os.path.exists(path):
            data = joblib.load(path)
            self.classifier = data['classifier']
            self.regressor = data['regressor']
            self.scaler = data['scaler']
            self.accuracy = data['accuracy']
            self.feature_names = data['feature_names']
            return True
        return False


class XGBoostModel(BaseMLModel):
    """XGBoost Gradient Boosting Model"""
    
    def __init__(self):
        super().__init__("XGBoost")
    
    def train(self, X: np.ndarray, y_cls: np.ndarray, y_reg: np.ndarray, feature_names: List[str]) -> Dict:
        if not HAS_XGBOOST:
            return {"status": "error", "message": "XGBoost not installed"}
        
        self.feature_names = feature_names
        X_scaled = self.scaler.fit_transform(X)
        
        # Time series split
        tscv = TimeSeriesSplit(n_splits=3)
        scores = []
        
        self.classifier = xgb.XGBClassifier(
            n_estimators=200,
            max_depth=6,
            learning_rate=0.05,
            subsample=0.8,
            colsample_bytree=0.8,
            random_state=42,
            use_label_encoder=False,
            eval_metric='logloss'
        )
        
        self.regressor = xgb.XGBRegressor(
            n_estimators=200,
            max_depth=6,
            learning_rate=0.05,
            subsample=0.8,
            colsample_bytree=0.8,
            random_state=42
        )
        
        for train_idx, test_idx in tscv.split(X_scaled):
            X_train, X_test = X_scaled[train_idx], X_scaled[test_idx]
            y_train, y_test = y_cls[train_idx], y_cls[test_idx]
            
            self.classifier.fit(X_train, y_train)
            scores.append(accuracy_score(y_test, self.classifier.predict(X_test)))
        
        # Final train on all data
        self.classifier.fit(X_scaled, y_cls)
        self.regressor.fit(X_scaled, y_reg)
        self.accuracy = np.mean(scores)
        
        return {"status": "success", "accuracy": self.accuracy, "model": self.name}
    
    def predict(self, X: np.ndarray) -> ModelResult:
        X_scaled = self.scaler.transform(X)
        probs = self.classifier.predict_proba(X_scaled)[0]
        ret = self.regressor.predict(X_scaled)[0]
        
        if probs[1] > 0.55:
            signal = "BUY"
        elif probs[0] > 0.55:
            signal = "SELL"
        else:
            signal = "HOLD"
        
        return ModelResult(
            name=self.name,
            signal=signal,
            confidence=float(max(probs)),
            prob_up=float(probs[1]) if len(probs) > 1 else 0,
            prob_down=float(probs[0]),
            predicted_return=float(ret),
            accuracy=self.accuracy
        )


class LightGBMModel(BaseMLModel):
    """LightGBM Fast Gradient Boosting Model"""
    
    def __init__(self):
        super().__init__("LightGBM")
    
    def train(self, X: np.ndarray, y_cls: np.ndarray, y_reg: np.ndarray, feature_names: List[str]) -> Dict:
        if not HAS_LIGHTGBM:
            return {"status": "error", "message": "LightGBM not installed"}
        
        self.feature_names = feature_names
        X_scaled = self.scaler.fit_transform(X)
        
        tscv = TimeSeriesSplit(n_splits=3)
        scores = []
        
        self.classifier = lgb.LGBMClassifier(
            n_estimators=200,
            max_depth=6,
            learning_rate=0.05,
            num_leaves=31,
            random_state=42,
            verbose=-1
        )
        
        self.regressor = lgb.LGBMRegressor(
            n_estimators=200,
            max_depth=6,
            learning_rate=0.05,
            num_leaves=31,
            random_state=42,
            verbose=-1
        )
        
        for train_idx, test_idx in tscv.split(X_scaled):
            X_train, X_test = X_scaled[train_idx], X_scaled[test_idx]
            y_train, y_test = y_cls[train_idx], y_cls[test_idx]
            
            self.classifier.fit(X_train, y_train)
            scores.append(accuracy_score(y_test, self.classifier.predict(X_test)))
        
        self.classifier.fit(X_scaled, y_cls)
        self.regressor.fit(X_scaled, y_reg)
        self.accuracy = np.mean(scores)
        
        return {"status": "success", "accuracy": self.accuracy, "model": self.name}
    
    def predict(self, X: np.ndarray) -> ModelResult:
        X_scaled = self.scaler.transform(X)
        probs = self.classifier.predict_proba(X_scaled)[0]
        ret = self.regressor.predict(X_scaled)[0]
        
        if probs[1] > 0.55:
            signal = "BUY"
        elif probs[0] > 0.55:
            signal = "SELL"
        else:
            signal = "HOLD"
        
        return ModelResult(
            name=self.name,
            signal=signal,
            confidence=float(max(probs)),
            prob_up=float(probs[1]) if len(probs) > 1 else 0,
            prob_down=float(probs[0]),
            predicted_return=float(ret),
            accuracy=self.accuracy
        )


class CatBoostModel(BaseMLModel):
    """CatBoost Gradient Boosting Model"""
    
    def __init__(self):
        super().__init__("CatBoost")
    
    def train(self, X: np.ndarray, y_cls: np.ndarray, y_reg: np.ndarray, feature_names: List[str]) -> Dict:
        if not HAS_CATBOOST:
            return {"status": "error", "message": "CatBoost not installed"}
        
        self.feature_names = feature_names
        X_scaled = self.scaler.fit_transform(X)
        
        tscv = TimeSeriesSplit(n_splits=3)
        scores = []
        
        self.classifier = CatBoostClassifier(
            iterations=200,
            depth=6,
            learning_rate=0.05,
            random_state=42,
            verbose=False
        )
        
        self.regressor = CatBoostRegressor(
            iterations=200,
            depth=6,
            learning_rate=0.05,
            random_state=42,
            verbose=False
        )
        
        for train_idx, test_idx in tscv.split(X_scaled):
            X_train, X_test = X_scaled[train_idx], X_scaled[test_idx]
            y_train, y_test = y_cls[train_idx], y_cls[test_idx]
            
            self.classifier.fit(X_train, y_train)
            scores.append(accuracy_score(y_test, self.classifier.predict(X_test)))
        
        self.classifier.fit(X_scaled, y_cls)
        self.regressor.fit(X_scaled, y_reg)
        self.accuracy = np.mean(scores)
        
        return {"status": "success", "accuracy": self.accuracy, "model": self.name}
    
    def predict(self, X: np.ndarray) -> ModelResult:
        X_scaled = self.scaler.transform(X)
        probs = self.classifier.predict_proba(X_scaled)[0]
        ret = self.regressor.predict(X_scaled)[0]
        
        if probs[1] > 0.55:
            signal = "BUY"
        elif probs[0] > 0.55:
            signal = "SELL"
        else:
            signal = "HOLD"
        
        return ModelResult(
            name=self.name,
            signal=signal,
            confidence=float(max(probs)),
            prob_up=float(probs[1]) if len(probs) > 1 else 0,
            prob_down=float(probs[0]),
            predicted_return=float(ret),
            accuracy=self.accuracy
        )


class ExtraTreesModel(BaseMLModel):
    """Extra Trees Ensemble Model"""
    
    def __init__(self):
        super().__init__("ExtraTrees")
    
    def train(self, X: np.ndarray, y_cls: np.ndarray, y_reg: np.ndarray, feature_names: List[str]) -> Dict:
        self.feature_names = feature_names
        X_scaled = self.scaler.fit_transform(X)
        
        tscv = TimeSeriesSplit(n_splits=3)
        scores = []
        
        self.classifier = ExtraTreesClassifier(
            n_estimators=200,
            max_depth=10,
            min_samples_split=5,
            random_state=42,
            n_jobs=-1
        )
        
        self.regressor = ExtraTreesRegressor(
            n_estimators=200,
            max_depth=10,
            min_samples_split=5,
            random_state=42,
            n_jobs=-1
        )
        
        for train_idx, test_idx in tscv.split(X_scaled):
            X_train, X_test = X_scaled[train_idx], X_scaled[test_idx]
            y_train, y_test = y_cls[train_idx], y_cls[test_idx]
            
            self.classifier.fit(X_train, y_train)
            scores.append(accuracy_score(y_test, self.classifier.predict(X_test)))
        
        self.classifier.fit(X_scaled, y_cls)
        self.regressor.fit(X_scaled, y_reg)
        self.accuracy = np.mean(scores)
        
        return {"status": "success", "accuracy": self.accuracy, "model": self.name}
    
    def predict(self, X: np.ndarray) -> ModelResult:
        X_scaled = self.scaler.transform(X)
        probs = self.classifier.predict_proba(X_scaled)[0]
        ret = self.regressor.predict(X_scaled)[0]
        
        if probs[1] > 0.55:
            signal = "BUY"
        elif probs[0] > 0.55:
            signal = "SELL"
        else:
            signal = "HOLD"
        
        return ModelResult(
            name=self.name,
            signal=signal,
            confidence=float(max(probs)),
            prob_up=float(probs[1]) if len(probs) > 1 else 0,
            prob_down=float(probs[0]),
            predicted_return=float(ret),
            accuracy=self.accuracy
        )


class RandomForestModel(BaseMLModel):
    """Random Forest Baseline Model"""
    
    def __init__(self):
        super().__init__("RandomForest")
    
    def train(self, X: np.ndarray, y_cls: np.ndarray, y_reg: np.ndarray, feature_names: List[str]) -> Dict:
        self.feature_names = feature_names
        X_scaled = self.scaler.fit_transform(X)
        
        tscv = TimeSeriesSplit(n_splits=3)
        scores = []
        
        self.classifier = RandomForestClassifier(
            n_estimators=200,
            max_depth=10,
            min_samples_split=5,
            random_state=42,
            n_jobs=-1
        )
        
        self.regressor = RandomForestRegressor(
            n_estimators=200,
            max_depth=10,
            min_samples_split=5,
            random_state=42,
            n_jobs=-1
        )
        
        for train_idx, test_idx in tscv.split(X_scaled):
            X_train, X_test = X_scaled[train_idx], X_scaled[test_idx]
            y_train, y_test = y_cls[train_idx], y_cls[test_idx]
            
            self.classifier.fit(X_train, y_train)
            scores.append(accuracy_score(y_test, self.classifier.predict(X_test)))
        
        self.classifier.fit(X_scaled, y_cls)
        self.regressor.fit(X_scaled, y_reg)
        self.accuracy = np.mean(scores)
        
        return {"status": "success", "accuracy": self.accuracy, "model": self.name}
    
    def predict(self, X: np.ndarray) -> ModelResult:
        X_scaled = self.scaler.transform(X)
        probs = self.classifier.predict_proba(X_scaled)[0]
        ret = self.regressor.predict(X_scaled)[0]
        
        if probs[1] > 0.55:
            signal = "BUY"
        elif probs[0] > 0.55:
            signal = "SELL"
        else:
            signal = "HOLD"
        
        return ModelResult(
            name=self.name,
            signal=signal,
            confidence=float(max(probs)),
            prob_up=float(probs[1]) if len(probs) > 1 else 0,
            prob_down=float(probs[0]),
            predicted_return=float(ret),
            accuracy=self.accuracy
        )


class EnsemblePredictor:
    """
    Professional Ensemble Predictor combining multiple models
    with weighted voting based on individual accuracy
    """
    
    def __init__(self):
        self.models: Dict[str, BaseMLModel] = {}
        self.weights: Dict[str, float] = {}
        self.feature_engineering = AdvancedFeatureEngineering()
        self.regime_detector = RegimeDetector()
        self.trained = False
    
    def _get_model_path(self, symbol: str, model_name: str) -> str:
        return os.path.join(MODEL_DIR, f"{symbol.upper()}_{model_name}.joblib")
    
    def _initialize_models(self):
        """Initialize all available models"""
        self.models = {
            'RandomForest': RandomForestModel(),
            'ExtraTrees': ExtraTreesModel(),
        }
        
        if HAS_XGBOOST:
            self.models['XGBoost'] = XGBoostModel()
        if HAS_LIGHTGBM:
            self.models['LightGBM'] = LightGBMModel()
        if HAS_CATBOOST:
            self.models['CatBoost'] = CatBoostModel()
    
    def train(self, symbol: str, df: pd.DataFrame) -> Dict[str, Any]:
        """Train all models on the data"""
        if len(df) < 250:
            return {"status": "error", "message": "Need at least 250 candles for reliable training"}
        
        self._initialize_models()
        
        # Feature engineering
        features_df = self.feature_engineering.compute_all_features(df)
        
        # Add target columns
        horizon = 5
        close = df['Close'].iloc[len(df) - len(features_df):]
        close = close.reset_index(drop=True)
        features_df = features_df.reset_index(drop=True)
        
        features_df['_target_direction'] = (close.shift(-horizon) > close).astype(int)
        features_df['_target_return'] = (close.shift(-horizon) - close) / close
        
        # Drop NaN
        data = features_df.dropna()
        
        if len(data) < 100:
            return {"status": "error", "message": "Insufficient clean data after feature engineering"}
        
        feature_cols = [c for c in data.columns if not c.startswith('_')]
        
        X = data[feature_cols].values
        y_cls = data['_target_direction'].values
        y_reg = data['_target_return'].values
        
        # Train each model
        results = {}
        total_accuracy = 0
        
        for name, model in self.models.items():
            try:
                result = model.train(X, y_cls, y_reg, feature_cols)
                results[name] = result
                if result.get('status') == 'success':
                    model.save(self._get_model_path(symbol, name))
                    total_accuracy += model.accuracy
            except Exception as e:
                results[name] = {"status": "error", "message": str(e)}
        
        # Calculate weights based on accuracy
        if total_accuracy > 0:
            for name, model in self.models.items():
                if model.accuracy > 0:
                    self.weights[name] = model.accuracy / total_accuracy
        
        # Save weights
        joblib.dump({
            'weights': self.weights,
            'feature_cols': feature_cols
        }, os.path.join(MODEL_DIR, f"{symbol.upper()}_ensemble_meta.joblib"))
        
        self.trained = True
        
        return {
            "status": "success",
            "symbol": symbol,
            "models_trained": len([r for r in results.values() if r.get('status') == 'success']),
            "model_results": results,
            "weights": self.weights,
            "samples": len(X),
            "features": len(feature_cols),
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def predict(self, symbol: str, df: pd.DataFrame) -> Dict[str, Any]:
        """Get ensemble prediction from all loaded models"""
        # Initialize and load models
        self._initialize_models()
        
        loaded_models = 0
        for name, model in self.models.items():
            if model.load(self._get_model_path(symbol, name)):
                loaded_models += 1
        
        # Load ensemble metadata
        meta_path = os.path.join(MODEL_DIR, f"{symbol.upper()}_ensemble_meta.joblib")
        if os.path.exists(meta_path):
            meta = joblib.load(meta_path)
            self.weights = meta.get('weights', {})
            feature_cols = meta.get('feature_cols', [])
        else:
            feature_cols = []
        
        # Detect regime
        regime, regime_scores = self.regime_detector.detect_regime(df)
        
        # Current price and support/resistance
        current_price = float(df['Close'].iloc[-1])
        recent_high = float(df['High'].tail(20).max())
        recent_low = float(df['Low'].tail(20).min())
        atr = float((df['High'] - df['Low']).tail(14).mean())
        
        # Support/Resistance levels
        support_levels = {
            "level_1": float(recent_low),
            "level_2": float(recent_low - atr),
            "level_3": float(recent_low - 2 * atr)
        }
        resistance_levels = {
            "level_1": float(recent_high),
            "level_2": float(recent_high + atr),
            "level_3": float(recent_high + 2 * atr)
        }
        
        # Base result structure
        result = {
            "status": "success",
            "symbol": symbol,
            "timestamp": datetime.utcnow().isoformat(),
            "current_price": current_price,
            "regime": regime.value,
            "regime_scores": regime_scores,
            "support_levels": support_levels,
            "resistance_levels": resistance_levels,
            "models_loaded": loaded_models,
            "individual_models": [],
            "signal": "HOLD",
            "confidence": 0.5,
            "probabilities": {"up": 0.5, "down": 0.5},
            "predicted_return_pct": 0,
            "predicted_price_1week": {
                "target": current_price,
                "low": current_price * 0.97,
                "high": current_price * 1.03,
                "confidence": 0.5
            },
            "stop_loss": support_levels["level_1"],
            "take_profit": resistance_levels["level_1"],
            "risk_reward_ratio": 1.0,
            "feature_importance": {}
        }
        
        if loaded_models == 0:
            result["status"] = "no_models"
            result["message"] = "No trained models found. Please train first."
            return result
        
        # Get features for current data
        features_df = self.feature_engineering.compute_all_features(df)
        if features_df.empty:
            result["status"] = "error"
            result["message"] = "Feature extraction failed"
            return result
        
        # Prepare prediction input
        last_row = features_df.iloc[[-1]].copy()
        
        # Align columns with saved feature list
        for col in feature_cols:
            if col not in last_row.columns:
                last_row[col] = 0.0
        
        if feature_cols:
            X = last_row[feature_cols].fillna(0).values
        else:
            X = last_row.fillna(0).values
        
        # Collect predictions from each model
        ensemble_prob_up = 0
        ensemble_prob_down = 0
        ensemble_return = 0
        total_weight = 0
        
        individual_results = []
        
        for name, model in self.models.items():
            if model.classifier is not None:
                try:
                    pred = model.predict(X)
                    individual_results.append({
                        "name": pred.name,
                        "signal": pred.signal,
                        "confidence": pred.confidence,
                        "prob_up": pred.prob_up,
                        "prob_down": pred.prob_down,
                        "predicted_return": pred.predicted_return,
                        "accuracy": pred.accuracy
                    })
                    
                    weight = self.weights.get(name, 1.0 / loaded_models)
                    ensemble_prob_up += pred.prob_up * weight
                    ensemble_prob_down += pred.prob_down * weight
                    ensemble_return += pred.predicted_return * weight
                    total_weight += weight
                except Exception as e:
                    print(f"Prediction error for {name}: {e}")
        
        if total_weight > 0:
            ensemble_prob_up /= total_weight
            ensemble_prob_down /= total_weight
            ensemble_return /= total_weight
        
        # Determine ensemble signal
        if ensemble_prob_up > 0.55:
            signal = "BUY"
        elif ensemble_prob_down > 0.55:
            signal = "SELL"
        else:
            signal = "HOLD"
        
        confidence = max(ensemble_prob_up, ensemble_prob_down)
        
        # Calculate stop loss and take profit
        if signal == "BUY":
            stop_loss = max(support_levels["level_1"], current_price - 2 * atr)
            take_profit = current_price + abs(current_price - stop_loss) * 2
        elif signal == "SELL":
            stop_loss = min(resistance_levels["level_1"], current_price + 2 * atr)
            take_profit = current_price - abs(stop_loss - current_price) * 2
        else:
            stop_loss = support_levels["level_1"]
            take_profit = resistance_levels["level_1"]
        
        risk = abs(current_price - stop_loss)
        reward = abs(take_profit - current_price)
        rr_ratio = reward / risk if risk > 0 else 1.0
        
        # Predicted price
        predicted_price_1w = current_price * (1 + ensemble_return)
        
        # Update result
        result.update({
            "individual_models": individual_results,
            "signal": signal,
            "confidence": float(confidence),
            "probabilities": {"up": float(ensemble_prob_up), "down": float(ensemble_prob_down)},
            "predicted_return_pct": float(ensemble_return * 100),
            "predicted_price_1week": {
                "target": float(predicted_price_1w),
                "low": float(predicted_price_1w - atr),
                "high": float(predicted_price_1w + atr),
                "confidence": float(confidence)
            },
            "predicted_price_1month": {
                "target": float(current_price * (1 + ensemble_return * 3)),
                "low": float(predicted_price_1w * 0.9),
                "high": float(predicted_price_1w * 1.1),
                "confidence": float(confidence * 0.85)
            },
            "stop_loss": float(stop_loss),
            "take_profit": float(take_profit),
            "risk_reward_ratio": float(rr_ratio),
            "suggested_entry": float(current_price),
            "ensemble_weights": self.weights
        })
        
        # Add XAI Explanation if requested
        if df.get('include_explanation', False):
            try:
                # Explain the top contributing model
                top_model_name = max(self.weights, key=self.weights.get) if self.weights else 'RandomForest'
                top_model = self.models.get(top_model_name)
                if top_model and top_model.classifier:
                    # We need some training data for SHAP background
                    # For performance, we can use a sample or cached background
                    # Here we use the current X as a placeholder for local explanation
                    explanation = xai_service.explain_prediction(
                        top_model.classifier, 
                        X, 
                        X, # Background should ideally be more samples
                        feature_cols,
                        method="shap"
                    )
                    result["explanation"] = explanation
            except Exception as e:
                logger.error(f"Failed to generate XAI explanation: {e}")

        # Cache prediction
        try:
            cache_dir = os.path.join(MODEL_DIR, "predictions")
            os.makedirs(cache_dir, exist_ok=True)
            with open(os.path.join(cache_dir, f"{symbol.upper()}_latest.json"), 'w') as f:
                json.dump(result, f, default=str)
        except Exception:
            pass
        
        return result
    
    def get_cached_prediction(self, symbol: str) -> Optional[Dict]:
        """Retrieve cached prediction"""
        try:
            cache_path = os.path.join(MODEL_DIR, "predictions", f"{symbol.upper()}_latest.json")
            if os.path.exists(cache_path):
                with open(cache_path, 'r') as f:
                    return json.load(f)
        except Exception:
            pass
        return None
    
    def get_available_models(self) -> List[str]:
        """Return list of available model names"""
        models = ['RandomForest', 'ExtraTrees']
        if HAS_XGBOOST:
            models.append('XGBoost')
        if HAS_LIGHTGBM:
            models.append('LightGBM')
        if HAS_CATBOOST:
            models.append('CatBoost')
        return models


# Singleton instance for backward compatibility
ml_engine = EnsemblePredictor()


# Legacy compatibility wrapper
def train_model(symbol: str, df: pd.DataFrame) -> Dict:
    """Legacy train function"""
    return ml_engine.train(symbol, df)


def predict(symbol: str, df: pd.DataFrame) -> Dict:
    """Legacy predict function"""
    return ml_engine.predict(symbol, df)


def get_cached_prediction(symbol: str) -> Optional[Dict]:
    """Legacy cache function"""
    return ml_engine.get_cached_prediction(symbol)
