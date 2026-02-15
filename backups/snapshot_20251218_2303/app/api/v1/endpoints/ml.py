from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from app.db.session import get_db
from app.models.user import User
from app.api.deps import get_current_user

router = APIRouter()

@router.get("/performance", response_model=Dict[str, Any])
def get_ml_performance(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get ML model performance metrics"""
    # Return mock performance data for now
    return {
        "overall_accuracy": 0.85,
        "precision": 0.82,
        "recall": 0.78,
        "f1_score": 0.80,
        "models": [
            {
                "name": "Random Forest",
                "accuracy": 0.87,
                "precision": 0.84,
                "recall": 0.81,
                "f1_score": 0.82,
                "last_trained": "2024-01-15T10:30:00Z"
            },
            {
                "name": "Gradient Boosting",
                "accuracy": 0.83,
                "precision": 0.80,
                "recall": 0.75,
                "f1_score": 0.77,
                "last_trained": "2024-01-15T10:30:00Z"
            },
            {
                "name": "Neural Network",
                "accuracy": 0.85,
                "precision": 0.82,
                "recall": 0.78,
                "f1_score": 0.80,
                "last_trained": "2024-01-15T10:30:00Z"
            }
        ],
        "training_history": [
            {"date": "2024-01-15", "accuracy": 0.85, "loss": 0.15},
            {"date": "2024-01-14", "accuracy": 0.83, "loss": 0.17},
            {"date": "2024-01-13", "accuracy": 0.81, "loss": 0.19},
            {"date": "2024-01-12", "accuracy": 0.79, "loss": 0.21},
            {"date": "2024-01-11", "accuracy": 0.77, "loss": 0.23}
        ]
    }

@router.get("/predictions/{symbol}", response_model=Dict[str, Any])
def get_ml_predictions(
    symbol: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get ML predictions for a symbol"""
    # Return mock prediction data for now
    return {
        "symbol": symbol,
        "predictions": [
            {
                "timeframe": "1d",
                "predicted_price": 185.50,
                "confidence": 0.85,
                "direction": "up",
                "probability": 0.75
            },
            {
                "timeframe": "1w", 
                "predicted_price": 192.30,
                "confidence": 0.78,
                "direction": "up",
                "probability": 0.68
            },
            {
                "timeframe": "1m",
                "predicted_price": 201.20,
                "confidence": 0.72,
                "direction": "up", 
                "probability": 0.62
            }
        ],
        "technical_indicators": {
            "rsi": 65.2,
            "macd": 2.1,
            "bollinger_upper": 185.0,
            "bollinger_lower": 175.0,
            "moving_average_20": 180.5,
            "moving_average_50": 178.2
        },
        "sentiment": {
            "overall": "positive",
            "score": 0.72,
            "news_sentiment": 0.68,
            "social_sentiment": 0.76
        }
    }

@router.get("/anomaly-detection", response_model=List[Dict[str, Any]])
def get_anomaly_detection(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get anomaly detection results"""
    # Return mock anomaly data for now
    return [
        {
            "id": 1,
            "symbol": "AAPL",
            "anomaly_type": "price_spike",
            "severity": "medium",
            "detected_at": "2024-01-15T14:30:00Z",
            "description": "Unusual price movement detected",
            "confidence": 0.85
        },
        {
            "id": 2,
            "symbol": "TSLA",
            "anomaly_type": "volume_spike",
            "severity": "high",
            "detected_at": "2024-01-15T13:45:00Z",
            "description": "Abnormal trading volume detected",
            "confidence": 0.92
        }
    ]

@router.post("/train", response_model=Dict[str, Any])
def train_ml_models(
    symbols: List[str],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Trigger ML model training"""
    # Mock training response
    return {
        "status": "training_started",
        "message": f"Training started for {len(symbols)} symbols",
        "estimated_duration": "30 minutes",
        "symbols": symbols
    }
