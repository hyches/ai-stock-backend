from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Body
from app.core.security import get_current_user
from app.services.ml_service import (
    predict,
    get_predictions,
    get_model_performance,
    retrain_model,
    get_feature_importance
)
from app.schemas.ml import (
    PredictionRequest,
    PredictionResponse,
    ModelPerformance,
    FeatureImportance
)
from typing import List, Dict, Any

router = APIRouter()

@router.post("/predict", response_model=Dict[str, Any])
async def predict_endpoint(
    data: Dict[str, float] = Body(...),
    current_user = Depends(get_current_user)
):
    try:
        return predict(data)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error predicting: {str(e)}")

@router.post("/batch_predict", response_model=Dict[str, Any])
async def batch_predict_endpoint(
    data: List[Dict[str, float]] = Body(...),
    current_user = Depends(get_current_user)
):
    try:
        return get_predictions(data)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error batch predicting: {str(e)}")

@router.get("/performance", response_model=ModelPerformance)
async def performance(
    current_user = Depends(get_current_user)
):
    try:
        return get_model_performance()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error getting model performance: {str(e)}")

@router.post("/retrain", response_model=Dict[str, str])
async def retrain(
    X: List[List[float]] = Body(...),
    y: List[int] = Body(...),
    current_user = Depends(get_current_user)
):
    try:
        return retrain_model(X, y)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error retraining model: {str(e)}")

@router.get("/features", response_model=FeatureImportance)
async def features(
    current_user = Depends(get_current_user)
):
    try:
        return get_feature_importance()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error getting feature importance: {str(e)}") 