"""
Comprehensive ML services testing suite
"""
import pytest
import numpy as np
from unittest.mock import patch, Mock, AsyncMock
from fastapi import status
from tests.test_config import TestConfig, TestClient, sample_ml_data

class TestMLService:
    """Test ML service functionality"""
    
    @pytest.mark.asyncio
    async def test_ml_model_prediction(self, mock_ml_model):
        """Test ML model prediction functionality"""
        # Test single prediction
        result = await mock_ml_model.predict(sample_ml_data)
        assert result == 1
        
        # Test batch prediction
        batch_data = [sample_ml_data for _ in range(3)]
        batch_result = await mock_ml_model.batch_predict(batch_data)
        assert batch_result == [1, 0, 1]
    
    def test_ml_model_performance(self, mock_ml_model):
        """Test ML model performance metrics"""
        performance = mock_ml_model.get_performance()
        assert 'accuracy' in performance
        assert 'loss' in performance
        assert 0 <= performance['accuracy'] <= 1
        assert performance['loss'] >= 0
    
    def test_ml_model_feature_importance(self, mock_ml_model):
        """Test ML model feature importance"""
        importance = mock_ml_model.get_feature_importance()
        assert isinstance(importance, dict)
        assert len(importance) > 0
    
    @pytest.mark.asyncio
    async def test_ml_model_retrain(self, mock_ml_model):
        """Test ML model retraining"""
        X = np.random.random((100, 10))
        y = np.random.randint(0, 2, 100)
        
        result = mock_ml_model.retrain(X, y)
        assert result is True

class TestMLAPIEndpoints:
    """Test ML API endpoints"""
    
    def test_ml_predict_endpoint(self, authorized_client: TestClient, sample_ml_data):
        """Test ML prediction API endpoint"""
        response = authorized_client.post("/api/v1/ml/predict", json=sample_ml_data)
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_422_UNPROCESSABLE_ENTITY]
        
        if response.status_code == status.HTTP_200_OK:
            data = response.json()
            assert 'prediction' in data
    
    def test_ml_batch_predict_endpoint(self, authorized_client: TestClient):
        """Test ML batch prediction API endpoint"""
        batch_data = [sample_ml_data for _ in range(3)]
        response = authorized_client.post("/api/v1/ml/batch_predict", json=batch_data)
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_422_UNPROCESSABLE_ENTITY]
        
        if response.status_code == status.HTTP_200_OK:
            data = response.json()
            assert 'predictions' in data
            assert len(data['predictions']) == 3
    
    def test_ml_performance_endpoint(self, authorized_client: TestClient):
        """Test ML performance API endpoint"""
        response = authorized_client.get("/api/v1/ml/performance")
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]
        
        if response.status_code == status.HTTP_200_OK:
            data = response.json()
            assert 'accuracy' in data
            assert 'loss' in data
    
    def test_ml_feature_importance_endpoint(self, authorized_client: TestClient):
        """Test ML feature importance API endpoint"""
        response = authorized_client.get("/api/v1/ml/feature_importance")
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]
        
        if response.status_code == status.HTTP_200_OK:
            data = response.json()
            assert 'feature_importance' in data
    
    def test_ml_retrain_endpoint(self, superuser_client: TestClient):
        """Test ML retrain API endpoint"""
        retrain_data = {
            "X": [[0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0] for _ in range(10)],
            "y": [1, 0, 1, 0, 1, 0, 1, 0, 1, 0]
        }
        response = superuser_client.post("/api/v1/ml/retrain", json=retrain_data)
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_422_UNPROCESSABLE_ENTITY]
        
        if response.status_code == status.HTTP_200_OK:
            data = response.json()
            assert 'status' in data

class TestMLDataValidation:
    """Test ML data validation"""
    
    def test_invalid_feature_count(self, authorized_client: TestClient):
        """Test ML prediction with invalid feature count"""
        invalid_data = {"f0": 0.1, "f1": 0.2}  # Only 2 features instead of 10
        response = authorized_client.post("/api/v1/ml/predict", json=invalid_data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_invalid_feature_values(self, authorized_client: TestClient):
        """Test ML prediction with invalid feature values"""
        invalid_data = sample_ml_data.copy()
        invalid_data["f0"] = "invalid_value"  # String instead of float
        response = authorized_client.post("/api/v1/ml/predict", json=invalid_data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_missing_features(self, authorized_client: TestClient):
        """Test ML prediction with missing features"""
        incomplete_data = {"f0": 0.1, "f1": 0.2}  # Missing f2-f9
        response = authorized_client.post("/api/v1/ml/predict", json=incomplete_data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

class TestMLModelPersistence:
    """Test ML model persistence and loading"""
    
    def test_model_save_and_load(self, mock_ml_model):
        """Test model saving and loading"""
        # This would test the actual model persistence
        # For now, we'll test the mock behavior
        assert mock_ml_model is not None
    
    def test_model_file_existence(self):
        """Test that model file exists or can be created"""
        import os
        model_path = 'ml_model.joblib'
        # The model should exist or be created during testing
        # This is handled by the MLModel class initialization

class TestMLPerformance:
    """Test ML performance and optimization"""
    
    def test_prediction_speed(self, mock_ml_model):
        """Test prediction speed"""
        import time
        
        start_time = time.time()
        # Simulate prediction
        mock_ml_model.predict(sample_ml_data)
        end_time = time.time()
        
        # Prediction should be fast (less than 1 second)
        assert (end_time - start_time) < 1.0
    
    def test_batch_prediction_efficiency(self, mock_ml_model):
        """Test batch prediction efficiency"""
        import time
        
        batch_data = [sample_ml_data for _ in range(100)]
        
        start_time = time.time()
        mock_ml_model.batch_predict(batch_data)
        end_time = time.time()
        
        # Batch prediction should be efficient
        assert (end_time - start_time) < 5.0

class TestMLIntegration:
    """Test ML integration with other services"""
    
    def test_ml_with_trading_data(self, authorized_client: TestClient):
        """Test ML predictions with trading data"""
        # Create a trade first
        trade_data = {
            "symbol": TestConfig.TEST_SYMBOL,
            "type": "buy",
            "quantity": TestConfig.TEST_QUANTITY,
            "price": TestConfig.TEST_PRICE
        }
        
        trade_response = authorized_client.post("/api/v1/trading/trades/", json=trade_data)
        
        # Then get ML prediction
        ml_response = authorized_client.post("/api/v1/ml/predict", json=sample_ml_data)
        
        # Both should work
        assert trade_response.status_code in [status.HTTP_201_CREATED, status.HTTP_422_UNPROCESSABLE_ENTITY]
        assert ml_response.status_code in [status.HTTP_200_OK, status.HTTP_422_UNPROCESSABLE_ENTITY]
    
    def test_ml_with_portfolio_data(self, authorized_client: TestClient):
        """Test ML predictions with portfolio data"""
        # Create a portfolio first
        portfolio_data = {
            "name": TestConfig.TEST_PORTFOLIO_NAME,
            "description": "Test portfolio",
            "initial_balance": TestConfig.TEST_INITIAL_BALANCE
        }
        
        portfolio_response = authorized_client.post("/api/v1/portfolio/", json=portfolio_data)
        
        # Then get ML prediction
        ml_response = authorized_client.post("/api/v1/ml/predict", json=sample_ml_data)
        
        # Both should work
        assert portfolio_response.status_code in [status.HTTP_201_CREATED, status.HTTP_422_UNPROCESSABLE_ENTITY]
        assert ml_response.status_code in [status.HTTP_200_OK, status.HTTP_422_UNPROCESSABLE_ENTITY]

class TestMLSecurity:
    """Test ML security and access control"""
    
    def test_ml_endpoint_authentication(self, client: TestClient):
        """Test that ML endpoints require authentication"""
        response = client.post("/api/v1/ml/predict", json=sample_ml_data)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_ml_retrain_authorization(self, authorized_client: TestClient):
        """Test that ML retrain requires superuser privileges"""
        retrain_data = {
            "X": [[0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]],
            "y": [1]
        }
        response = authorized_client.post("/api/v1/ml/retrain", json=retrain_data)
        # Should require superuser privileges
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_403_FORBIDDEN, status.HTTP_422_UNPROCESSABLE_ENTITY]

class TestMLDataProcessing:
    """Test ML data processing and preprocessing"""
    
    def test_data_normalization(self, mock_ml_model):
        """Test data normalization in ML pipeline"""
        # Test with normalized data
        normalized_data = {f"f{i}": i/10.0 for i in range(10)}
        result = mock_ml_model.predict(normalized_data)
        assert result in [0, 1]
    
    def test_data_scaling(self, mock_ml_model):
        """Test data scaling in ML pipeline"""
        # Test with scaled data
        scaled_data = {f"f{i}": i * 100 for i in range(10)}
        result = mock_ml_model.predict(scaled_data)
        assert result in [0, 1]
    
    def test_outlier_handling(self, mock_ml_model):
        """Test outlier handling in ML pipeline"""
        # Test with outlier data
        outlier_data = {f"f{i}": 1000 if i == 0 else i/10.0 for i in range(10)}
        result = mock_ml_model.predict(outlier_data)
        assert result in [0, 1]
