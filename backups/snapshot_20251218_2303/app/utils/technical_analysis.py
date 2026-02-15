import pandas as pd
import numpy as np
from typing import List, Dict, Any
from app.utils.data_fetcher import DataFetcher
from app.core.config import settings

class TechnicalAnalysis:
    def __init__(self):
        self.data_fetcher = DataFetcher()

    def analyze(self, symbol: str, strategy_type: str, parameters: Dict[str, Any]) -> List[Dict[str, Any]]:
        # Get historical data
        data = self.data_fetcher.get_historical_data(symbol)
        if data.empty:
            return []

        # Calculate indicators based on strategy type
        if strategy_type == "trend":
            return self._analyze_trend(data, parameters)
        elif strategy_type == "mean_reversion":
            return self._analyze_mean_reversion(data, parameters)
        elif strategy_type == "momentum":
            return self._analyze_momentum(data, parameters)
        elif strategy_type == "volatility":
            return self._analyze_volatility(data, parameters)
        elif strategy_type == "stat_arb":
            return self._analyze_statistical_arbitrage(data, parameters)
        else:
            return []

    def _analyze_trend(self, data: pd.DataFrame, parameters: Dict[str, Any]) -> List[Dict[str, Any]]:
        signals = []
        
        # Calculate EMAs
        ema_short = data['close'].ewm(span=parameters.get('ema_short', 9)).mean()
        ema_medium = data['close'].ewm(span=parameters.get('ema_medium', 21)).mean()
        ema_long = data['close'].ewm(span=parameters.get('ema_long', 50)).mean()
        
        # Calculate ADX
        high_low = data['high'] - data['low']
        high_close = np.abs(data['high'] - data['close'].shift())
        low_close = np.abs(data['low'] - data['close'].shift())
        ranges = pd.concat([high_low, high_close, low_close], axis=1)
        true_range = np.max(ranges, axis=1)
        atr = true_range.rolling(14).mean()
        
        # Calculate +DM and -DM
        up_move = data['high'] - data['high'].shift()
        down_move = data['low'].shift() - data['low']
        plus_dm = np.where((up_move > down_move) & (up_move > 0), up_move, 0)
        minus_dm = np.where((down_move > up_move) & (down_move > 0), down_move, 0)
        
        # Calculate +DI and -DI
        plus_di = 100 * (pd.Series(plus_dm).rolling(14).mean() / atr)
        minus_di = 100 * (pd.Series(minus_dm).rolling(14).mean() / atr)
        
        # Calculate ADX
        dx = 100 * np.abs(plus_di - minus_di) / (plus_di + minus_di)
        adx = dx.rolling(14).mean()
        
        # Generate signals
        if ema_short.iloc[-1] > ema_medium.iloc[-1] > ema_long.iloc[-1] and adx.iloc[-1] > 25:
            signals.append({
                "type": "buy",
                "confidence": min(adx.iloc[-1] / 100, 0.9),
                "metrics": {
                    "ema_short": ema_short.iloc[-1],
                    "ema_medium": ema_medium.iloc[-1],
                    "ema_long": ema_long.iloc[-1],
                    "adx": adx.iloc[-1]
                }
            })
        elif ema_short.iloc[-1] < ema_medium.iloc[-1] < ema_long.iloc[-1] and adx.iloc[-1] > 25:
            signals.append({
                "type": "sell",
                "confidence": min(adx.iloc[-1] / 100, 0.9),
                "metrics": {
                    "ema_short": ema_short.iloc[-1],
                    "ema_medium": ema_medium.iloc[-1],
                    "ema_long": ema_long.iloc[-1],
                    "adx": adx.iloc[-1]
                }
            })
        
        return signals

    def _analyze_mean_reversion(self, data: pd.DataFrame, parameters: Dict[str, Any]) -> List[Dict[str, Any]]:
        signals = []
        
        # Calculate Bollinger Bands
        window = parameters.get('bb_window', 20)
        num_std = parameters.get('bb_std', 2)
        
        sma = data['close'].rolling(window=window).mean()
        std = data['close'].rolling(window=window).std()
        upper_band = sma + (std * num_std)
        lower_band = sma - (std * num_std)
        
        # Calculate RSI
        delta = data['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        # Generate signals
        if data['close'].iloc[-1] < lower_band.iloc[-1] and rsi.iloc[-1] < 30:
            signals.append({
                "type": "buy",
                "confidence": min((30 - rsi.iloc[-1]) / 30, 0.9),
                "metrics": {
                    "price": data['close'].iloc[-1],
                    "lower_band": lower_band.iloc[-1],
                    "rsi": rsi.iloc[-1]
                }
            })
        elif data['close'].iloc[-1] > upper_band.iloc[-1] and rsi.iloc[-1] > 70:
            signals.append({
                "type": "sell",
                "confidence": min((rsi.iloc[-1] - 70) / 30, 0.9),
                "metrics": {
                    "price": data['close'].iloc[-1],
                    "upper_band": upper_band.iloc[-1],
                    "rsi": rsi.iloc[-1]
                }
            })
        
        return signals

    def _analyze_momentum(self, data: pd.DataFrame, parameters: Dict[str, Any]) -> List[Dict[str, Any]]:
        signals = []
        
        # Calculate RSI
        delta = data['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        # Calculate Stochastic Oscillator
        low_min = data['low'].rolling(window=14).min()
        high_max = data['high'].rolling(window=14).max()
        k = 100 * ((data['close'] - low_min) / (high_max - low_min))
        d = k.rolling(window=3).mean()
        
        # Generate signals
        if rsi.iloc[-1] < 30 and k.iloc[-1] < 20 and d.iloc[-1] < 20:
            signals.append({
                "type": "buy",
                "confidence": min((30 - rsi.iloc[-1]) / 30, 0.9),
                "metrics": {
                    "rsi": rsi.iloc[-1],
                    "stoch_k": k.iloc[-1],
                    "stoch_d": d.iloc[-1]
                }
            })
        elif rsi.iloc[-1] > 70 and k.iloc[-1] > 80 and d.iloc[-1] > 80:
            signals.append({
                "type": "sell",
                "confidence": min((rsi.iloc[-1] - 70) / 30, 0.9),
                "metrics": {
                    "rsi": rsi.iloc[-1],
                    "stoch_k": k.iloc[-1],
                    "stoch_d": d.iloc[-1]
                }
            })
        
        return signals

    def _analyze_volatility(self, data: pd.DataFrame, parameters: Dict[str, Any]) -> List[Dict[str, Any]]:
        signals = []
        
        # Calculate ATR
        high_low = data['high'] - data['low']
        high_close = np.abs(data['high'] - data['close'].shift())
        low_close = np.abs(data['low'] - data['close'].shift())
        ranges = pd.concat([high_low, high_close, low_close], axis=1)
        true_range = np.max(ranges, axis=1)
        atr = true_range.rolling(14).mean()
        
        # Calculate Bollinger Bands
        window = parameters.get('bb_window', 20)
        num_std = parameters.get('bb_std', 2)
        
        sma = data['close'].rolling(window=window).mean()
        std = data['close'].rolling(window=window).std()
        upper_band = sma + (std * num_std)
        lower_band = sma - (std * num_std)
        
        # Generate signals
        if data['close'].iloc[-1] < lower_band.iloc[-1] and atr.iloc[-1] > atr.iloc[-2]:
            signals.append({
                "type": "buy",
                "confidence": min((lower_band.iloc[-1] - data['close'].iloc[-1]) / lower_band.iloc[-1], 0.9),
                "metrics": {
                    "price": data['close'].iloc[-1],
                    "lower_band": lower_band.iloc[-1],
                    "atr": atr.iloc[-1]
                }
            })
        elif data['close'].iloc[-1] > upper_band.iloc[-1] and atr.iloc[-1] > atr.iloc[-2]:
            signals.append({
                "type": "sell",
                "confidence": min((data['close'].iloc[-1] - upper_band.iloc[-1]) / upper_band.iloc[-1], 0.9),
                "metrics": {
                    "price": data['close'].iloc[-1],
                    "upper_band": upper_band.iloc[-1],
                    "atr": atr.iloc[-1]
                }
            })
        
        return signals

    def _analyze_statistical_arbitrage(self, data: pd.DataFrame, parameters: Dict[str, Any]) -> List[Dict[str, Any]]:
        signals = []
        
        # Calculate z-score
        window = parameters.get('zscore_window', 20)
        sma = data['close'].rolling(window=window).mean()
        std = data['close'].rolling(window=window).std()
        zscore = (data['close'] - sma) / std
        
        # Calculate Hurst Exponent
        lags = range(2, 100)
        tau = [np.std(np.subtract(data['close'][lag:], data['close'][:-lag])) for lag in lags]
        reg = np.polyfit(np.log(lags), np.log(tau), 1)
        hurst = reg[0]
        
        # Generate signals
        if zscore.iloc[-1] < -2 and hurst < 0.5:
            signals.append({
                "type": "buy",
                "confidence": min(abs(zscore.iloc[-1]) / 4, 0.9),
                "metrics": {
                    "zscore": zscore.iloc[-1],
                    "hurst": hurst
                }
            })
        elif zscore.iloc[-1] > 2 and hurst < 0.5:
            signals.append({
                "type": "sell",
                "confidence": min(abs(zscore.iloc[-1]) / 4, 0.9),
                "metrics": {
                    "zscore": zscore.iloc[-1],
                    "hurst": hurst
                }
            })
        
        return signals 