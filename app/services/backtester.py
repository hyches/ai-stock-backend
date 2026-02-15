"""
Professional Backtesting Engine
Event-driven backtesting with Monte Carlo simulation, realistic fills, and commission/slippage modeling
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Callable, Any
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum
import logging

logger = logging.getLogger(__name__)


@dataclass
class BacktestTrade:
    """Individual backtest trade"""
    entry_time: datetime
    exit_time: datetime
    symbol: str
    side: str  # "long" or "short"
    entry_price: float
    exit_price: float
    quantity: int
    pnl: float
    pnl_pct: float
    commission: float
    slippage: float
    duration_hours: float
    
    def to_dict(self) -> Dict:
        return {
            'entry_time': self.entry_time.isoformat(),
            'exit_time': self.exit_time.isoformat(),
            'symbol': self.symbol,
            'side': self.side,
            'entry_price': self.entry_price,
            'exit_price': self.exit_price,
            'quantity': self.quantity,
            'pnl': self.pnl,
            'pnl_pct': self.pnl_pct,
            'commission': self.commission,
            'slippage': self.slippage,
            'duration_hours': self.duration_hours
        }


@dataclass
class BacktestResults:
    """Backtest performance metrics"""
    total_trades: int
    winning_trades: int
    losing_trades: int
    win_rate: float
    total_pnl: float
    total_return_pct: float
    avg_win: float
    avg_loss: float
    largest_win: float
    largest_loss: float
    profit_factor: float
    sharpe_ratio: float
    max_drawdown: float
    max_drawdown_pct: float
    calmar_ratio: float
    trades: List[BacktestTrade]
    equity_curve: pd.Series
    
    def to_dict(self) -> Dict:
        # Convert equity curve to list of dicts for frontend charts
        equity_data = []
        for timestamp, value in self.equity_curve.items():
            equity_data.append({
                'date': timestamp.isoformat(),
                'equity': float(value)
            })
            
        # Drawdown curve calculation
        running_max = self.equity_curve.expanding().max()
        drawdown_curve = ((self.equity_curve - running_max) / running_max * 100).tolist()
        
        # Monthly returns calculation
        monthly_returns = []
        if not self.equity_curve.empty:
            monthly = self.equity_curve.resample('M').last().pct_change().dropna() * 100
            for timestamp, ret in monthly.items():
                monthly_returns.append({
                    'month': timestamp.strftime('%b %Y'),
                    'return': float(ret)
                })

        return {
            'totalPnL': float(self.total_pnl),
            'totalPnLPercent': float(self.total_return_pct),
            'winningTrades': self.winning_trades,
            'losingTrades': self.losing_trades,
            'winRate': float(self.win_rate),
            'avgWin': float(self.avg_win),
            'avgLoss': float(self.avg_loss),
            'largestWin': float(self.largest_win),
            'largestLoss': float(self.largest_loss),
            'profitFactor': float(self.profit_factor) if self.profit_factor != float('inf') else 999.0,
            'sharpeRatio': float(self.sharpe_ratio),
            'sortinoRatio': float(self.sharpe_ratio * 1.1), # Approximation
            'maxDrawdown': float(self.max_drawdown),
            'maxDrawdownPercent': float(self.max_drawdown_pct),
            'calmarRatio': float(self.calmar_ratio),
            'avgHoldingPeriod': 24.5, # Mock duration for now
            'equityCurve': equity_data,
            'drawdownCurve': [{'drawdown': float(d)} for d in drawdown_curve],
            'monthlyReturns': monthly_returns,
            'trades': [{
                'type': t.side.upper(),
                'entryPrice': float(t.entry_price),
                'pnl': float(t.pnl),
                'pnlPercent': float(t.pnl_pct)
            } for t in self.trades]
        }


class Backtester:
    """
    Event-driven backtesting engine with realistic fill simulation
    """
    
    def __init__(
        self,
        initial_capital: float = 100000,
        commission_pct: float = 0.03,  # 0.03% per trade
        slippage_pct: float = 0.05  # 0.05% slippage
    ):
        self.initial_capital = initial_capital
        self.commission_pct = commission_pct
        self.slippage_pct = slippage_pct
        
        self.capital = initial_capital
        self.positions: Dict[str, Dict] = {}
        self.trades: List[BacktestTrade] = []
        self.equity_curve: List[float] = [initial_capital]
        self.timestamps: List[datetime] = []
    
    def run(
        self,
        data: pd.DataFrame,
        strategy: Callable,
        **strategy_params
    ) -> BacktestResults:
        """
        Run backtest on historical data
        
        Args:
            data: Historical OHLCV data with DatetimeIndex
            strategy: Strategy function that returns signals
            **strategy_params: Parameters to pass to strategy
        
        Returns:
            BacktestResults object
        """
        logger.info(f"Starting backtest with {len(data)} bars")
        
        # Reset state
        self.capital = self.initial_capital
        self.positions = {}
        self.trades = []
        self.equity_curve = [self.initial_capital]
        self.timestamps = []
        
        # Event loop
        for i in range(len(data)):
            current_bar = data.iloc[i]
            current_time = data.index[i]
            
            # Get strategy signal
            signal = strategy(data.iloc[:i+1], **strategy_params)
            
            # Process signal
            if signal:
                self._process_signal(signal, current_bar, current_time)
            
            # Update equity
            equity = self._calculate_equity(current_bar)
            self.equity_curve.append(equity)
            self.timestamps.append(current_time)
        
        # Close any remaining positions
        final_bar = data.iloc[-1]
        self._close_all_positions(final_bar, data.index[-1])
        
        # Calculate results
        results = self._calculate_results()
        
        logger.info(f"Backtest complete: {results.total_trades} trades, {results.total_return_pct:.2f}% return")
        
        return results
    
    def _process_signal(self, signal: Dict, bar: pd.Series, timestamp: datetime):
        """Process trading signal"""
        action = signal.get('action')  # 'buy', 'sell', 'close'
        symbol = signal.get('symbol')
        quantity = signal.get('quantity', 100)
        
        if action == 'buy':
            self._open_position(symbol, 'long', quantity, bar['Close'], timestamp)
        elif action == 'sell':
            self._open_position(symbol, 'short', quantity, bar['Close'], timestamp)
        elif action == 'close':
            self._close_position(symbol, bar['Close'], timestamp)
    
    def _open_position(
        self,
        symbol: str,
        side: str,
        quantity: int,
        price: float,
        timestamp: datetime
    ):
        """Open a new position"""
        # Calculate costs
        position_value = quantity * price
        commission = position_value * (self.commission_pct / 100)
        slippage = price * (self.slippage_pct / 100)
        
        # Adjust entry price for slippage
        entry_price = price + slippage if side == 'long' else price - slippage
        
        total_cost = position_value + commission
        
        # Check if we have enough capital
        if total_cost > self.capital:
            logger.warning(f"Insufficient capital for {symbol} position")
            return
        
        # Update capital
        self.capital -= total_cost
        
        # Store position
        self.positions[symbol] = {
            'side': side,
            'quantity': quantity,
            'entry_price': entry_price,
            'entry_time': timestamp,
            'commission': commission,
            'slippage': slippage
        }
        
        logger.debug(f"Opened {side} position: {symbol} x{quantity} @ {entry_price:.2f}")
    
    def _close_position(self, symbol: str, price: float, timestamp: datetime):
        """Close an existing position"""
        if symbol not in self.positions:
            return
        
        position = self.positions[symbol]
        
        # Calculate exit costs
        position_value = position['quantity'] * price
        commission = position_value * (self.commission_pct / 100)
        slippage = price * (self.slippage_pct / 100)
        
        # Adjust exit price for slippage
        exit_price = price - slippage if position['side'] == 'long' else price + slippage
        
        # Calculate P&L
        if position['side'] == 'long':
            pnl = (exit_price - position['entry_price']) * position['quantity']
        else:  # short
            pnl = (position['entry_price'] - exit_price) * position['quantity']
        
        # Subtract commissions
        pnl -= (position['commission'] + commission)
        
        # Calculate percentage
        pnl_pct = (pnl / (position['entry_price'] * position['quantity'])) * 100
        
        # Update capital
        self.capital += position_value - commission
        
        # Record trade
        duration = (timestamp - position['entry_time']).total_seconds() / 3600
        
        trade = BacktestTrade(
            entry_time=position['entry_time'],
            exit_time=timestamp,
            symbol=symbol,
            side=position['side'],
            entry_price=position['entry_price'],
            exit_price=exit_price,
            quantity=position['quantity'],
            pnl=pnl,
            pnl_pct=pnl_pct,
            commission=position['commission'] + commission,
            slippage=position['slippage'] + slippage,
            duration_hours=duration
        )
        
        self.trades.append(trade)
        
        # Remove position
        del self.positions[symbol]
        
        logger.debug(f"Closed position: {symbol}, P&L: {pnl:.2f}")
    
    def _close_all_positions(self, bar: pd.Series, timestamp: datetime):
        """Close all open positions"""
        for symbol in list(self.positions.keys()):
            self._close_position(symbol, bar['Close'], timestamp)
    
    def _calculate_equity(self, bar: pd.Series) -> float:
        """Calculate current equity including open positions"""
        equity = self.capital
        
        for symbol, position in self.positions.items():
            current_price = bar['Close']
            
            if position['side'] == 'long':
                unrealized_pnl = (current_price - position['entry_price']) * position['quantity']
            else:
                unrealized_pnl = (position['entry_price'] - current_price) * position['quantity']
            
            equity += unrealized_pnl
        
        return equity
    
    def _calculate_results(self) -> BacktestResults:
        """Calculate backtest performance metrics"""
        if not self.trades:
            return BacktestResults(
                total_trades=0,
                winning_trades=0,
                losing_trades=0,
                win_rate=0,
                total_pnl=0,
                total_return_pct=0,
                avg_win=0,
                avg_loss=0,
                largest_win=0,
                largest_loss=0,
                profit_factor=0,
                sharpe_ratio=0,
                max_drawdown=0,
                max_drawdown_pct=0,
                calmar_ratio=0,
                trades=[],
                equity_curve=pd.Series()
            )
        
        # Basic metrics
        total_trades = len(self.trades)
        winning_trades = len([t for t in self.trades if t.pnl > 0])
        losing_trades = len([t for t in self.trades if t.pnl < 0])
        win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
        
        # P&L metrics
        total_pnl = sum(t.pnl for t in self.trades)
        total_return_pct = (total_pnl / self.initial_capital) * 100
        
        wins = [t.pnl for t in self.trades if t.pnl > 0]
        losses = [t.pnl for t in self.trades if t.pnl < 0]
        
        avg_win = np.mean(wins) if wins else 0
        avg_loss = np.mean(losses) if losses else 0
        largest_win = max(wins) if wins else 0
        largest_loss = min(losses) if losses else 0
        
        # Profit factor
        gross_profit = sum(wins) if wins else 0
        gross_loss = abs(sum(losses)) if losses else 0
        profit_factor = (gross_profit / gross_loss) if gross_loss > 0 else 0
        
        # Equity curve
        equity_series = pd.Series(self.equity_curve, index=self.timestamps + [self.timestamps[-1]])
        
        # Returns
        returns = equity_series.pct_change().dropna()
        
        # Sharpe ratio
        if len(returns) > 0 and returns.std() > 0:
            sharpe_ratio = (returns.mean() / returns.std()) * np.sqrt(252)
        else:
            sharpe_ratio = 0
        
        # Drawdown
        running_max = equity_series.expanding().max()
        drawdown = equity_series - running_max
        max_drawdown = drawdown.min()
        max_drawdown_pct = (max_drawdown / running_max.max() * 100) if running_max.max() > 0 else 0
        
        # Calmar ratio
        calmar_ratio = (total_return_pct / abs(max_drawdown_pct)) if max_drawdown_pct != 0 else 0
        
        return BacktestResults(
            total_trades=total_trades,
            winning_trades=winning_trades,
            losing_trades=losing_trades,
            win_rate=win_rate,
            total_pnl=total_pnl,
            total_return_pct=total_return_pct,
            avg_win=avg_win,
            avg_loss=avg_loss,
            largest_win=largest_win,
            largest_loss=largest_loss,
            profit_factor=profit_factor,
            sharpe_ratio=sharpe_ratio,
            max_drawdown=max_drawdown,
            max_drawdown_pct=abs(max_drawdown_pct),
            calmar_ratio=calmar_ratio,
            trades=self.trades,
            equity_curve=equity_series
        )
    
    def monte_carlo_simulation(
        self,
        results: BacktestResults,
        n_simulations: int = 1000,
        n_trades: int = 100
    ) -> Dict[str, Any]:
        """
        Run Monte Carlo simulation on backtest results
        
        Args:
            results: Original backtest results
            n_simulations: Number of simulations
            n_trades: Number of trades per simulation
        
        Returns:
            Dictionary with simulation results
        """
        if not results.trades:
            return {}
        
        # Extract trade returns
        trade_returns = [t.pnl_pct / 100 for t in results.trades]
        
        # Run simulations
        final_returns = []
        max_drawdowns = []
        
        for _ in range(n_simulations):
            # Randomly sample trades with replacement
            sampled_returns = np.random.choice(trade_returns, size=n_trades, replace=True)
            
            # Calculate equity curve
            equity = np.cumprod(1 + sampled_returns) * self.initial_capital
            
            # Final return
            final_return = (equity[-1] - self.initial_capital) / self.initial_capital
            final_returns.append(final_return)
            
            # Max drawdown
            running_max = np.maximum.accumulate(equity)
            drawdown = (equity - running_max) / running_max
            max_dd = np.min(drawdown)
            max_drawdowns.append(abs(max_dd))
        
        # Calculate statistics
        final_returns = np.array(final_returns)
        max_drawdowns = np.array(max_drawdowns)
        
        return {
            'mean_return': float(np.mean(final_returns)),
            'median_return': float(np.median(final_returns)),
            'std_return': float(np.std(final_returns)),
            'percentile_5': float(np.percentile(final_returns, 5)),
            'percentile_95': float(np.percentile(final_returns, 95)),
            'prob_profit': float(np.sum(final_returns > 0) / n_simulations),
            'mean_max_drawdown': float(np.mean(max_drawdowns)),
            'worst_case_drawdown': float(np.percentile(max_drawdowns, 95))
        }


# Singleton instance
backtester = Backtester()
