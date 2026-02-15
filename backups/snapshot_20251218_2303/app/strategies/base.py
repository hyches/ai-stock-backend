from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Union
import pandas as pd
import numpy as np
from datetime import datetime
from app.models.trading import Strategy, Signal, Trade
from app.core.config import settings

class BaseStrategy(ABC):
    def __init__(
        self,
        strategy_id: int,
        parameters: Dict[str, Union[float, int, str, bool]],
        symbols: List[str],
        timeframe: str = '1d'
    ):
        self.strategy_id = strategy_id
        self.parameters = parameters
        self.symbols = symbols
        self.timeframe = timeframe
        self.position = {}  # Current positions
        self.signals = []   # Generated signals
        self.trades = []    # Executed trades
        self.metrics = {}   # Strategy metrics

    @abstractmethod
    def generate_signals(self, data: pd.DataFrame) -> List[Signal]:
        """Generate trading signals based on strategy logic"""
        pass

    @abstractmethod
    def calculate_metrics(self) -> Dict[str, float]:
        """Calculate strategy performance metrics"""
        pass

    def validate_parameters(self) -> bool:
        """Validate strategy parameters"""
        required_params = self.get_required_parameters()
        return all(param in self.parameters for param in required_params)

    @abstractmethod
    def get_required_parameters(self) -> List[str]:
        """Get list of required parameters"""
        pass

    def calculate_position_size(
        self,
        capital: float,
        risk_per_trade: float,
        stop_loss: float
    ) -> float:
        """Calculate position size based on risk management"""
        risk_amount = capital * risk_per_trade
        position_size = risk_amount / abs(stop_loss)
        return position_size

    def calculate_stop_loss(
        self,
        entry_price: float,
        atr: float,
        multiplier: float = 2.0
    ) -> float:
        """Calculate stop loss based on ATR"""
        return entry_price - (atr * multiplier)

    def calculate_take_profit(
        self,
        entry_price: float,
        stop_loss: float,
        risk_reward_ratio: float = 2.0
    ) -> float:
        """Calculate take profit based on risk-reward ratio"""
        risk = abs(entry_price - stop_loss)
        return entry_price + (risk * risk_reward_ratio)

    def calculate_atr(self, data: pd.DataFrame, period: int = 14) -> pd.Series:
        """Calculate Average True Range"""
        high = data['high']
        low = data['low']
        close = data['close']
        
        tr1 = high - low
        tr2 = abs(high - close.shift())
        tr3 = abs(low - close.shift())
        
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr = tr.rolling(period).mean()
        
        return atr

    def calculate_rsi(self, data: pd.DataFrame, period: int = 14) -> pd.Series:
        """Calculate Relative Strength Index"""
        delta = data['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi

    def calculate_macd(
        self,
        data: pd.DataFrame,
        fast_period: int = 12,
        slow_period: int = 26,
        signal_period: int = 9
    ) -> tuple:
        """Calculate MACD (Moving Average Convergence Divergence)"""
        exp1 = data['close'].ewm(span=fast_period, adjust=False).mean()
        exp2 = data['close'].ewm(span=slow_period, adjust=False).mean()
        macd = exp1 - exp2
        signal = macd.ewm(span=signal_period, adjust=False).mean()
        histogram = macd - signal
        
        return macd, signal, histogram

    def calculate_bollinger_bands(
        self,
        data: pd.DataFrame,
        period: int = 20,
        std_dev: float = 2.0
    ) -> tuple:
        """Calculate Bollinger Bands"""
        sma = data['close'].rolling(window=period).mean()
        std = data['close'].rolling(window=period).std()
        upper_band = sma + (std * std_dev)
        lower_band = sma - (std * std_dev)
        
        return upper_band, sma, lower_band

    def calculate_risk_metrics(self) -> Dict[str, float]:
        """Calculate risk metrics for the strategy"""
        if not self.trades:
            return {}

        returns = pd.Series([trade.pnl for trade in self.trades])
        
        metrics = {
            'total_return': returns.sum(),
            'sharpe_ratio': self.calculate_sharpe_ratio(returns),
            'sortino_ratio': self.calculate_sortino_ratio(returns),
            'max_drawdown': self.calculate_max_drawdown(returns),
            'win_rate': len(returns[returns > 0]) / len(returns),
            'profit_factor': abs(returns[returns > 0].sum() / returns[returns < 0].sum())
        }
        
        return metrics

    def calculate_sharpe_ratio(self, returns: pd.Series, risk_free_rate: float = 0.02) -> float:
        """Calculate Sharpe Ratio"""
        excess_returns = returns - risk_free_rate/252
        if len(excess_returns) < 2:
            return 0.0
        return np.sqrt(252) * excess_returns.mean() / excess_returns.std()

    def calculate_sortino_ratio(self, returns: pd.Series, risk_free_rate: float = 0.02) -> float:
        """Calculate Sortino Ratio"""
        excess_returns = returns - risk_free_rate/252
        downside_returns = excess_returns[excess_returns < 0]
        if len(downside_returns) < 2:
            return 0.0
        return np.sqrt(252) * excess_returns.mean() / downside_returns.std()

    def calculate_max_drawdown(self, returns: pd.Series) -> float:
        """Calculate Maximum Drawdown"""
        cumulative_returns = (1 + returns).cumprod()
        rolling_max = cumulative_returns.expanding().max()
        drawdowns = cumulative_returns / rolling_max - 1
        return abs(drawdowns.min())

    def backtest(
        self,
        data: pd.DataFrame,
        initial_capital: float = 100000.0,
        risk_per_trade: float = 0.02
    ) -> Dict[str, Union[float, List[Trade]]]:
        """Run backtest of the strategy"""
        self.position = {}
        self.trades = []
        capital = initial_capital
        
        for symbol in self.symbols:
            symbol_data = data[data['symbol'] == symbol].copy()
            signals = self.generate_signals(symbol_data)
            
            for signal in signals:
                if signal.signal_type == 'buy':
                    stop_loss = self.calculate_stop_loss(
                        signal.price,
                        self.calculate_atr(symbol_data).iloc[-1]
                    )
                    take_profit = self.calculate_take_profit(
                        signal.price,
                        stop_loss
                    )
                    position_size = self.calculate_position_size(
                        capital,
                        risk_per_trade,
                        stop_loss
                    )
                    
                    trade = Trade(
                        signal_id=signal.id,
                        symbol=symbol,
                        action='buy',
                        quantity=position_size,
                        price=signal.price,
                        stop_loss=stop_loss,
                        take_profit=take_profit,
                        status='executed',
                        pnl=0.0,
                        created_at=datetime.utcnow()
                    )
                    self.trades.append(trade)
                    self.position[symbol] = trade
                    
                elif signal.signal_type == 'sell' and symbol in self.position:
                    trade = self.position[symbol]
                    trade.status = 'closed'
                    trade.closed_at = datetime.utcnow()
                    trade.pnl = (signal.price - trade.price) * trade.quantity
                    capital += trade.pnl
                    del self.position[symbol]
        
        return {
            'final_capital': capital,
            'total_return': (capital - initial_capital) / initial_capital,
            'trades': self.trades,
            'metrics': self.calculate_risk_metrics()
        } 