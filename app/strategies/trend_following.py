from typing import Dict, List, Union
import pandas as pd
from datetime import datetime
from app.strategies.base import BaseStrategy
from app.models.trading import Signal

class TrendFollowingStrategy(BaseStrategy):
    def __init__(
        self,
        strategy_id: int,
        parameters: Dict[str, Union[float, int, str, bool]],
        symbols: List[str],
        timeframe: str = '1d'
    ):
        super().__init__(strategy_id, parameters, symbols, timeframe)
        self.validate_parameters()

    def get_required_parameters(self) -> List[str]:
        return [
            'fast_period',
            'slow_period',
            'signal_period',
            'atr_period',
            'atr_multiplier',
            'risk_reward_ratio'
        ]

    def generate_signals(self, data: pd.DataFrame) -> List[Signal]:
        signals = []
        
        # Calculate indicators
        macd, signal, histogram = self.calculate_macd(
            data,
            self.parameters['fast_period'],
            self.parameters['slow_period'],
            self.parameters['signal_period']
        )
        
        atr = self.calculate_atr(data, self.parameters['atr_period'])
        
        # Generate signals
        for i in range(1, len(data)):
            current_price = data['close'].iloc[i]
            prev_price = data['close'].iloc[i-1]
            
            # MACD crossover
            macd_crossover = (
                histogram.iloc[i-1] < 0 and
                histogram.iloc[i] > 0
            )
            
            macd_crossunder = (
                histogram.iloc[i-1] > 0 and
                histogram.iloc[i] < 0
            )
            
            # Trend strength
            trend_strength = abs(macd.iloc[i]) / atr.iloc[i]
            
            # Generate buy signal
            if macd_crossover and trend_strength > 1.0:
                stop_loss = self.calculate_stop_loss(
                    current_price,
                    atr.iloc[i],
                    self.parameters['atr_multiplier']
                )
                
                take_profit = self.calculate_take_profit(
                    current_price,
                    stop_loss,
                    self.parameters['risk_reward_ratio']
                )
                
                signal = Signal(
                    strategy_id=self.strategy_id,
                    symbol=data['symbol'].iloc[i],
                    signal_type='buy',
                    confidence=min(trend_strength / 2, 1.0),
                    created_at=datetime.utcnow(),
                    metrics={
                        'macd': macd.iloc[i],
                        'signal': signal.iloc[i],
                        'histogram': histogram.iloc[i],
                        'atr': atr.iloc[i],
                        'trend_strength': trend_strength,
                        'stop_loss': stop_loss,
                        'take_profit': take_profit
                    }
                )
                signals.append(signal)
            
            # Generate sell signal
            elif macd_crossunder and trend_strength > 1.0:
                signal = Signal(
                    strategy_id=self.strategy_id,
                    symbol=data['symbol'].iloc[i],
                    signal_type='sell',
                    confidence=min(trend_strength / 2, 1.0),
                    created_at=datetime.utcnow(),
                    metrics={
                        'macd': macd.iloc[i],
                        'signal': signal.iloc[i],
                        'histogram': histogram.iloc[i],
                        'atr': atr.iloc[i],
                        'trend_strength': trend_strength
                    }
                )
                signals.append(signal)
        
        return signals

    def calculate_metrics(self) -> Dict[str, float]:
        if not self.trades:
            return {}

        returns = pd.Series([trade.pnl for trade in self.trades])
        winning_trades = returns[returns > 0]
        losing_trades = returns[returns < 0]
        
        metrics = {
            'total_return': returns.sum(),
            'sharpe_ratio': self.calculate_sharpe_ratio(returns),
            'sortino_ratio': self.calculate_sortino_ratio(returns),
            'max_drawdown': self.calculate_max_drawdown(returns),
            'win_rate': len(winning_trades) / len(returns),
            'profit_factor': abs(winning_trades.sum() / losing_trades.sum()) if len(losing_trades) > 0 else float('inf'),
            'average_win': winning_trades.mean() if len(winning_trades) > 0 else 0,
            'average_loss': losing_trades.mean() if len(losing_trades) > 0 else 0,
            'largest_win': winning_trades.max() if len(winning_trades) > 0 else 0,
            'largest_loss': losing_trades.min() if len(losing_trades) > 0 else 0,
            'total_trades': len(returns),
            'winning_trades': len(winning_trades),
            'losing_trades': len(losing_trades)
        }
        
        return metrics 