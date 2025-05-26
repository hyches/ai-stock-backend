from typing import Dict, List, Optional, Tuple
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
import yfinance as yf
import pandas_ta as ta
from app.services.fundamental_analysis import fundamental_analysis
from app.services.technical_analysis import technical_analysis
from app.services.sentiment_analysis import sentiment_analysis
from app.core.cache import redis_cache

class MLPredictions:
    """
    MLPredictions is a class designed to provide comprehensive machine learning-based predictions for financial markets, including price movements, volatility, and trend directions.
    Parameters:
        - cache_ttl (int): Time-to-live for cached data, default is 3600 seconds (1 hour).
        - models (Dict): Dictionary storing the initialized machine learning models.
        - scalers (Dict): Dictionary storing the data scalers for feature preprocessing.
    Processing Logic:
        - The class initializes models using RandomForestRegressor and GradientBoostingRegressor techniques for predicting prices, volatility, and trends.
        - It employs asynchronous methods to fetch historical stock data and generate predictions efficiently.
        - Comprehensive predictions for a given symbol are derived from a combination of models, with ensemble methods used to improve reliability.
        - Confidence measures and technical indicators are calculated to assess validity and importance of predictions with specific emphasis on feature significance and prediction confidence.
    """
    def __init__(self):
        self.cache_ttl = 3600  # 1 hour
        self.models = {}
        self.scalers = {}
        self._initialize_models()

    def _initialize_models(self):
        """Initialize ML models"""
        # Price prediction models
        self.models['price_rf'] = RandomForestRegressor(n_estimators=100, random_state=42)
        self.models['price_gbm'] = GradientBoostingRegressor(n_estimators=100, random_state=42)

        # Volatility prediction models
        self.models['volatility_rf'] = RandomForestRegressor(n_estimators=100, random_state=42)
        self.models['volatility_gbm'] = GradientBoostingRegressor(n_estimators=100, random_state=42)

        # Trend prediction models
        self.models['trend_rf'] = RandomForestRegressor(n_estimators=100, random_state=42)
        self.models['trend_gbm'] = GradientBoostingRegressor(n_estimators=100, random_state=42)

        # Initialize scalers
        self.scalers['price'] = StandardScaler()
        self.scalers['volatility'] = StandardScaler()
        self.scalers['trend'] = StandardScaler()

    async def get_comprehensive_predictions(self, symbol: str) -> Dict:
        """Get comprehensive ML predictions"""
        return {
            "price_predictions": await self._predict_price(symbol),
            "volatility_predictions": await self._predict_volatility(symbol),
            "trend_predictions": await self._predict_trend(symbol),
            "model_metrics": await self._get_model_metrics(symbol)
        }

    async def _predict_price(self, symbol: str) -> Dict:
        """Predict future price movements"""
        try:
            # Get historical data from yfinance
            hist_data = await self._get_historical_data(symbol)
            
            # Calculate technical indicators
            tech_indicators = self._calculate_technical_indicators(hist_data)
            
            # Prepare features
            features = self._prepare_price_features(hist_data, tech_indicators)

            # Make predictions using different models
            predictions = {
                "random_forest": self._predict_with_model('price_rf', features),
                "gradient_boosting": self._predict_with_model('price_gbm', features)
            }

            # Calculate ensemble prediction
            predictions["ensemble"] = self._calculate_ensemble_prediction(predictions)

            return {
                "predictions": predictions,
                "confidence": self._calculate_prediction_confidence(predictions),
                "time_horizon": self._get_prediction_time_horizon(),
                "feature_importance": self._get_feature_importance('price_rf')
            }
        except Exception as e:
            logger.error(f"Error predicting price: {str(e)}")
            return {}

    async def _predict_volatility(self, symbol: str) -> Dict:
        """Predict future volatility"""
        try:
            # Get historical data
            hist_data = await self._get_historical_data(symbol)
            
            # Calculate volatility indicators
            vol_indicators = self._calculate_volatility_indicators(hist_data)
            
            # Prepare features
            features = self._prepare_volatility_features(hist_data, vol_indicators)

            # Make predictions
            predictions = {
                "random_forest": self._predict_with_model('volatility_rf', features),
                "gradient_boosting": self._predict_with_model('volatility_gbm', features)
            }

            return {
                "predictions": predictions,
                "confidence": self._calculate_prediction_confidence(predictions),
                "volatility_regime": self._identify_volatility_regime(predictions)
            }
        except Exception as e:
            logger.error(f"Error predicting volatility: {str(e)}")
            return {}

    async def _predict_trend(self, symbol: str) -> Dict:
        """Predict future trend direction and strength"""
        try:
            # Get historical data
            hist_data = await self._get_historical_data(symbol)
            
            # Calculate trend indicators
            trend_indicators = self._calculate_trend_indicators(hist_data)
            
            # Prepare features
            features = self._prepare_trend_features(hist_data, trend_indicators)

            # Make predictions
            predictions = {
                "random_forest": self._predict_with_model('trend_rf', features),
                "gradient_boosting": self._predict_with_model('trend_gbm', features)
            }

            return {
                "predictions": predictions,
                "confidence": self._calculate_prediction_confidence(predictions),
                "trend_strength": self._calculate_trend_strength(predictions),
                "trend_duration": self._predict_trend_duration(predictions)
            }
        except Exception as e:
            logger.error(f"Error predicting trend: {str(e)}")
            return {}

    async def _get_historical_data(self, symbol: str) -> pd.DataFrame:
        """Get historical data from yfinance"""
        try:
            # Try to get from cache first
            cache_key = f"hist_data_{symbol}"
            cached_data = await redis_cache.get(cache_key)
            if cached_data:
                return pd.DataFrame(cached_data)

            # If not in cache, fetch from yfinance
            ticker = yf.Ticker(symbol)
            hist_data = ticker.history(period="1y", interval="1d")
            
            # Cache the data
            await redis_cache.set(cache_key, hist_data.to_dict(), self.cache_ttl)
            
            return hist_data
        except Exception as e:
            logger.error(f"Error fetching historical data: {str(e)}")
            return pd.DataFrame()

    def _calculate_technical_indicators(self, data: pd.DataFrame) -> Dict:
        """Calculate technical indicators using pandas_ta"""
        try:
            # Calculate various technical indicators
            indicators = {}
            
            # Trend indicators
            indicators['sma_20'] = ta.sma(data['Close'], length=20)
            indicators['sma_50'] = ta.sma(data['Close'], length=50)
            indicators['sma_200'] = ta.sma(data['Close'], length=200)
            
            # Momentum indicators
            indicators['rsi'] = ta.rsi(data['Close'])
            indicators['macd'] = ta.macd(data['Close'])
            indicators['stoch'] = ta.stoch(data['High'], data['Low'], data['Close'])
            
            # Volatility indicators
            indicators['bbands'] = ta.bbands(data['Close'])
            indicators['atr'] = ta.atr(data['High'], data['Low'], data['Close'])
            
            # Volume indicators
            indicators['obv'] = ta.obv(data['Close'], data['Volume'])
            indicators['vwap'] = ta.vwap(data['High'], data['Low'], data['Close'], data['Volume'])
            
            return indicators
        except Exception as e:
            logger.error(f"Error calculating technical indicators: {str(e)}")
            return {}

    def _prepare_price_features(self, hist_data: pd.DataFrame, indicators: Dict) -> np.ndarray:
        """Prepare features for price prediction"""
        try:
            features = []
            
            # Price features
            features.extend([
                hist_data['Close'].pct_change().iloc[-1],
                hist_data['Volume'].pct_change().iloc[-1],
                hist_data['High'].iloc[-1] / hist_data['Low'].iloc[-1] - 1
            ])
            
            # Technical indicators
            if indicators:
                features.extend([
                    indicators['sma_20'].iloc[-1],
                    indicators['rsi'].iloc[-1],
                    indicators['macd']['MACD_12_26_9'].iloc[-1],
                    indicators['bbands']['BBL_20_2.0'].iloc[-1],
                    indicators['atr'].iloc[-1]
                ])
            
            return np.array(features).reshape(1, -1)
        except Exception as e:
            logger.error(f"Error preparing price features: {str(e)}")
            return np.array([])

    def _predict_with_model(self, model_name: str, features: np.ndarray) -> float:
        """Make prediction using specified model"""
        try:
            model = self.models[model_name]
            return model.predict(features)[0]
        except Exception as e:
            logger.error(f"Error making prediction with {model_name}: {str(e)}")
            return 0.0

    def _calculate_ensemble_prediction(self, predictions: Dict) -> float:
        """Calculate ensemble prediction from multiple models"""
        try:
            weights = {
                'random_forest': 0.5,
                'gradient_boosting': 0.5
            }
            return sum(predictions[model] * weights[model] for model in weights)
        except Exception as e:
            logger.error(f"Error calculating ensemble prediction: {str(e)}")
            return 0.0

    def _calculate_prediction_confidence(self, predictions: Dict) -> float:
        """Calculate confidence in predictions"""
        try:
            values = list(predictions.values())
            variance = np.var(values)
            return 1 / (1 + variance)  # Higher variance = lower confidence
        except Exception as e:
            logger.error(f"Error calculating prediction confidence: {str(e)}")
            return 0.0

    # Add more helper methods for feature preparation and predictions...

ml_predictions = MLPredictions() 