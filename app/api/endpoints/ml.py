from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from app.core.security import get_current_user
from app.services.ml_service import (
    get_predictions,
    get_model_performance,
    retrain_model,
    get_feature_importance
)
from app.schemas.ml import (
    PredictionResponse,
    ModelPerformance,
    FeatureImportance
)
from typing import List

router = APIRouter()

@router.get("/predictions/{symbol}", response_model=PredictionResponse)
async def predictions(
    symbol: str,
    current_user = Depends(get_current_user)
):
    try:
        predictions = await get_predictions(symbol)
        return predictions
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Error getting predictions: {str(e)}"
        )

@router.get("/performance", response_model=ModelPerformance)
async def performance(
    current_user = Depends(get_current_user)
):
    try:
        performance = await get_model_performance()
        return performance
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Error getting model performance: {str(e)}"
        )

@router.post("/retrain/{symbol}")
async def retrain(
    symbol: str,
    background_tasks: BackgroundTasks,
    current_user = Depends(get_current_user)
):
    try:
        background_tasks.add_task(retrain_model, symbol)
        return {"message": "Model retraining started"}
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Error starting model retraining: {str(e)}"
        )

@router.get("/features/{symbol}", response_model=List[FeatureImportance])
async def features(
    symbol: str,
    current_user = Depends(get_current_user)
):
    try:
        features = await get_feature_importance(symbol)
        return features
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Error getting feature importance: {str(e)}"
        ) 