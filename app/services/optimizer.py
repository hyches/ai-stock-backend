import numpy as np
import pandas as pd
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import yfinance as yf
from sklearn.ensemble import RandomForestRegressor
from app.models.portfolio import PortfolioOutput, PortfolioMetrics, StockWeight
import logging

logger = logging.getLogger(__name__)

class PortfolioOptimizer:
    """
    Service for optimizing portfolio weights using RandomForest-based approach.
    """
    
    def __init__(self):
        self.rf_model = RandomForestRegressor(n_estimators=100, random_state=42)
        
    async def optimize(
        self,
        stocks: List[str],
        capital: float,
        risk_tolerance: float = 0.5,
        min_weight: float = 0.05,
        max_weight: float = 0.3,
        sector_constraints: Optional[Dict[str, float]] = None
    ) -> PortfolioOutput:
        """
        Optimize portfolio weights based on historical data and constraints.
        
        Args:
            stocks: List of stock symbols
            capital: Total capital to invest
            risk_tolerance: Risk tolerance (0-1)
            min_weight: Minimum weight per stock
            max_weight: Maximum weight per stock
            sector_constraints: Maximum allocation per sector
            
        Returns:
            PortfolioOutput object with optimized weights and metrics
        """
        try:
            logger.info(f"Starting portfolio optimization for {len(stocks)} stocks")
            
            # Fetch historical data
            historical_data = await self._fetch_historical_data(stocks)
            if not historical_data:
                raise ValueError("Failed to fetch historical data")
                
            # Calculate features and returns
            features, returns = self._prepare_data(historical_data)
            
            # Train RandomForest model
            self.rf_model.fit(features, returns)
            
            # Get feature importance scores
            importance_scores = self.rf_model.feature_importances_
            
            # Calculate initial weights based on feature importance
            weights = self._calculate_initial_weights(importance_scores, stocks)
            
            # Apply constraints
            weights = self._apply_constraints(
                weights,
                min_weight,
                max_weight,
                sector_constraints,
                historical_data
            )
            
            # Calculate portfolio metrics
            metrics = self._calculate_metrics(weights, historical_data)
            
            # Calculate cash allocation (5% buffer)
            cash_allocation = capital * 0.05
            
            # Determine rebalancing frequency based on volatility
            rebalance_freq = "monthly" if metrics.volatility > 0.2 else "quarterly"
            
            # Create output
            return PortfolioOutput(
                weights=[
                    StockWeight(symbol=stock, weight=weight)
                    for stock, weight in zip(stocks, weights)
                ],
                metrics=metrics,
                cash_allocation=cash_allocation,
                rebalance_frequency=rebalance_freq
            )
            
        except Exception as e:
            logger.error(f"Error in portfolio optimization: {str(e)}")
            raise
            
    async def _fetch_historical_data(self, stocks: List[str]) -> Optional[pd.DataFrame]:
        """Fetch historical data for stocks"""
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=365)  # 1 year of data
            
            data = {}
            for stock in stocks:
                ticker = yf.Ticker(stock)
                hist = ticker.history(start=start_date, end=end_date)
                if not hist.empty:
                    data[stock] = hist['Close']
                    
            if not data:
                return None
                
            return pd.DataFrame(data)
            
        except Exception as e:
            logger.error(f"Error fetching historical data: {str(e)}")
            return None
            
    def _prepare_data(self, data: pd.DataFrame) -> tuple:
        """Prepare features and returns for model training"""
        # Calculate daily returns
        returns = data.pct_change().dropna()
        
        # Calculate features
        features = pd.DataFrame()
        for col in data.columns:
            # Price momentum (20-day)
            features[f'{col}_momentum'] = data[col].pct_change(20)
            # Volatility (20-day)
            features[f'{col}_volatility'] = returns[col].rolling(20).std()
            # Volume (if available)
            if 'Volume' in data.columns:
                features[f'{col}_volume'] = data['Volume'].rolling(20).mean()
                
        return features.fillna(0), returns.mean()
        
    def _calculate_initial_weights(self, importance_scores: np.ndarray, stocks: List[str]) -> np.ndarray:
        """Calculate initial weights based on feature importance"""
        # Normalize importance scores
        weights = importance_scores / importance_scores.sum()
        return weights
        
    def _apply_constraints(
        self,
        weights: np.ndarray,
        min_weight: float,
        max_weight: float,
        sector_constraints: Optional[Dict[str, float]],
        historical_data: pd.DataFrame
    ) -> np.ndarray:
        """Apply weight constraints including sector constraints"""
        try:
            # Apply min/max weight constraints
            weights = np.clip(weights, min_weight, max_weight)
            
            # Normalize weights to sum to 1
            weights = weights / weights.sum()
            
            # Apply sector constraints if provided
            if sector_constraints:
                # Get sector information for each stock
                stock_sectors = {}
                for i, stock in enumerate(historical_data.columns):
                    stock_info = yf.Ticker(stock).info
                    sector = stock_info.get('sector', 'Unknown')
                    stock_sectors[stock] = sector
                
                # Calculate current sector allocations
                sector_allocations = {}
                for stock, weight in zip(historical_data.columns, weights):
                    sector = stock_sectors[stock]
                    sector_allocations[sector] = sector_allocations.get(sector, 0) + weight
                
                # Check and adjust sector allocations
                for sector, max_allocation in sector_constraints.items():
                    if sector in sector_allocations and sector_allocations[sector] > max_allocation:
                        # Calculate excess allocation
                        excess = sector_allocations[sector] - max_allocation
                        
                        # Get stocks in this sector
                        sector_stocks = [stock for stock, s in stock_sectors.items() if s == sector]
                        
                        # Reduce weights proportionally
                        total_sector_weight = sum(weights[i] for i, stock in enumerate(historical_data.columns) if stock in sector_stocks)
                        for i, stock in enumerate(historical_data.columns):
                            if stock in sector_stocks:
                                weights[i] *= (1 - excess / total_sector_weight)
                
                # Re-normalize weights
                weights = weights / weights.sum()
            
            return weights
            
        except Exception as e:
            logger.error(f"Error applying constraints: {str(e)}")
            raise
        
    def _calculate_metrics(
        self,
        weights: np.ndarray,
        historical_data: pd.DataFrame
    ) -> PortfolioMetrics:
        """Calculate portfolio performance metrics"""
        # Calculate daily returns
        returns = historical_data.pct_change().dropna()
        
        # Calculate portfolio returns
        portfolio_returns = (returns * weights).sum(axis=1)
        
        # Calculate metrics
        expected_return = portfolio_returns.mean() * 252  # Annualized
        volatility = portfolio_returns.std() * np.sqrt(252)  # Annualized
        sharpe_ratio = expected_return / volatility if volatility != 0 else 0
        
        # Calculate maximum drawdown
        cum_returns = (1 + portfolio_returns).cumprod()
        rolling_max = cum_returns.expanding().max()
        drawdowns = cum_returns / rolling_max - 1
        max_drawdown = drawdowns.min()
        
        # Calculate sector allocation
        sector_allocation = {}  # TODO: Implement sector allocation calculation
        
        return PortfolioMetrics(
            expected_return=expected_return * 100,  # Convert to percentage
            volatility=volatility * 100,
            sharpe_ratio=sharpe_ratio,
            max_drawdown=max_drawdown * 100,
            sector_allocation=sector_allocation
        ) 