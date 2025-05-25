from typing import Dict, List, Optional, Union
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.strategies.base import BaseStrategy
from app.strategies.trend_following import TrendFollowingStrategy
from app.models.trading import Strategy, BacktestResult
from app.core.config import settings
from app.db.session import get_db

class BacktestService:
    def __init__(self, db: Session):
        self.db = db
        self.strategy_map = {
            'trend': TrendFollowingStrategy,
            # Add more strategies here
        }

    def run_backtest(
        self,
        strategy_id: int,
        start_date: datetime,
        end_date: datetime,
        initial_capital: float = 100000.0,
        risk_per_trade: float = 0.02
    ) -> Dict[str, Union[float, List[Dict]]]:
        """Run backtest for a strategy"""
        # Get strategy from database
        strategy = self.db.query(Strategy).filter(Strategy.id == strategy_id).first()
        if not strategy:
            raise ValueError(f"Strategy with ID {strategy_id} not found")

        # Get historical data
        data = self._get_historical_data(
            strategy.symbols,
            start_date,
            end_date,
            strategy.timeframe
        )

        # Initialize strategy
        strategy_class = self.strategy_map.get(strategy.type)
        if not strategy_class:
            raise ValueError(f"Strategy type {strategy.type} not supported")

        strategy_instance = strategy_class(
            strategy_id=strategy.id,
            parameters=strategy.parameters,
            symbols=strategy.symbols,
            timeframe=strategy.timeframe
        )

        # Run backtest
        results = strategy_instance.backtest(
            data,
            initial_capital=initial_capital,
            risk_per_trade=risk_per_trade
        )

        # Save results
        backtest_result = BacktestResult(
            strategy_id=strategy.id,
            symbol=','.join(strategy.symbols),
            start_date=start_date,
            end_date=end_date,
            initial_balance=initial_capital,
            final_balance=results['final_capital'],
            total_return=results['total_return'],
            sharpe_ratio=results['metrics']['sharpe_ratio'],
            max_drawdown=results['metrics']['max_drawdown'],
            win_rate=results['metrics']['win_rate'],
            metrics=results['metrics'],
            created_at=datetime.utcnow()
        )
        self.db.add(backtest_result)
        self.db.commit()

        return results

    def _get_historical_data(
        self,
        symbols: List[str],
        start_date: datetime,
        end_date: datetime,
        timeframe: str
    ) -> pd.DataFrame:
        """Get historical data for symbols"""
        # This is a placeholder - implement actual data fetching logic
        # You might want to fetch from a database or external API
        data = []
        for symbol in symbols:
            # Generate sample data for testing
            dates = pd.date_range(start_date, end_date, freq='D')
            prices = np.random.normal(100, 2, len(dates))
            volumes = np.random.normal(1000000, 200000, len(dates))
            
            for i, date in enumerate(dates):
                data.append({
                    'symbol': symbol,
                    'date': date,
                    'open': prices[i] * (1 + np.random.normal(0, 0.01)),
                    'high': prices[i] * (1 + abs(np.random.normal(0, 0.02))),
                    'low': prices[i] * (1 - abs(np.random.normal(0, 0.02))),
                    'close': prices[i],
                    'volume': volumes[i]
                })
        
        return pd.DataFrame(data)

    def optimize_parameters(
        self,
        strategy_id: int,
        start_date: datetime,
        end_date: datetime,
        param_grid: Dict[str, List[Union[float, int, str, bool]]],
        initial_capital: float = 100000.0,
        risk_per_trade: float = 0.02
    ) -> Dict[str, Union[float, Dict]]:
        """Optimize strategy parameters using grid search"""
        best_sharpe = -float('inf')
        best_params = None
        best_results = None

        # Generate parameter combinations
        param_combinations = self._generate_param_combinations(param_grid)

        for params in param_combinations:
            # Update strategy parameters
            strategy = self.db.query(Strategy).filter(Strategy.id == strategy_id).first()
            strategy.parameters.update(params)
            self.db.commit()

            # Run backtest
            results = self.run_backtest(
                strategy_id,
                start_date,
                end_date,
                initial_capital,
                risk_per_trade
            )

            # Update best parameters if better Sharpe ratio
            if results['metrics']['sharpe_ratio'] > best_sharpe:
                best_sharpe = results['metrics']['sharpe_ratio']
                best_params = params
                best_results = results

        return {
            'best_sharpe_ratio': best_sharpe,
            'best_parameters': best_params,
            'best_results': best_results
        }

    def _generate_param_combinations(
        self,
        param_grid: Dict[str, List[Union[float, int, str, bool]]]
    ) -> List[Dict[str, Union[float, int, str, bool]]]:
        """Generate all combinations of parameters"""
        import itertools
        
        keys = param_grid.keys()
        values = param_grid.values()
        
        combinations = []
        for combination in itertools.product(*values):
            combinations.append(dict(zip(keys, combination)))
        
        return combinations

    def analyze_results(
        self,
        backtest_id: int
    ) -> Dict[str, Union[float, List[Dict]]]:
        """Analyze backtest results in detail"""
        backtest = self.db.query(BacktestResult).filter(BacktestResult.id == backtest_id).first()
        if not backtest:
            raise ValueError(f"Backtest with ID {backtest_id} not found")

        # Calculate additional metrics
        metrics = backtest.metrics
        metrics.update({
            'annualized_return': metrics['total_return'] * (252 / (backtest.end_date - backtest.start_date).days),
            'volatility': metrics.get('volatility', 0),
            'calmar_ratio': metrics['annualized_return'] / metrics['max_drawdown'] if metrics['max_drawdown'] > 0 else float('inf'),
            'sortino_ratio': metrics.get('sortino_ratio', 0),
            'profit_factor': metrics.get('profit_factor', 0),
            'average_win': metrics.get('average_win', 0),
            'average_loss': metrics.get('average_loss', 0),
            'largest_win': metrics.get('largest_win', 0),
            'largest_loss': metrics.get('largest_loss', 0),
            'total_trades': metrics.get('total_trades', 0),
            'winning_trades': metrics.get('winning_trades', 0),
            'losing_trades': metrics.get('losing_trades', 0)
        })

        return {
            'metrics': metrics,
            'equity_curve': self._generate_equity_curve(backtest),
            'monthly_returns': self._calculate_monthly_returns(backtest),
            'drawdown_analysis': self._analyze_drawdowns(backtest)
        }

    def _generate_equity_curve(self, backtest: BacktestResult) -> List[Dict]:
        """Generate equity curve data"""
        # This is a placeholder - implement actual equity curve generation
        return []

    def _calculate_monthly_returns(self, backtest: BacktestResult) -> Dict[str, float]:
        """Calculate monthly returns"""
        # This is a placeholder - implement actual monthly returns calculation
        return {}

    def _analyze_drawdowns(self, backtest: BacktestResult) -> Dict[str, Union[float, List[Dict]]]:
        """Analyze drawdowns in detail"""
        # This is a placeholder - implement actual drawdown analysis
        return {} 