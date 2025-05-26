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
    """Fetch predictions for a given stock symbol.
    Parameters:
        - symbol (str): The stock symbol for which predictions are required.
        - current_user (Depends): Dependency for fetching the current authenticated user, default is fetched through Depends(get_current_user).
    Returns:
        - list: A list of prediction data associated with the given stock symbol.
    Processing Logic:
        - Utilizes asynchronous function to fetch predictions.
        - Handles exceptions by raising HTTP 400 errors with a descriptive message.
        - Ensures error feedback includes details from the caught exception."""
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
    """Fetch the performance metrics of a model.
    Parameters:
        - current_user (Depends): The user dependency to check current user context. Not explicitly used in the function but part of the callable signature for dependency injection.
    Returns:
        - dict: The performance metrics of the model.
    Processing Logic:
        - Asynchronously fetch model performance using `get_model_performance`.
        - Handles exceptions, raising an HTTP 400 error if fetching performance data fails."""
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
    """Initiates the retraining process for a model associated with a given symbol.
    Parameters:
        - symbol (str): Identifier for the specific model to be retrained.
        - background_tasks (BackgroundTasks): Instance to manage asynchronous background tasks.
        - current_user (Depends): Current authenticated user, automatically provided by dependency injection.
    Returns:
        - dict: A message indicating the retraining process has started.
    Processing Logic:
        - Utilizes background tasks to execute the retrain_model function asynchronously.
        - If an error occurs while adding the retraining task, a HTTPException with a 400 status code is raised."""
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
    """Feature Importance Retrieval Function.
    Parameters:
        - symbol (str): The financial data symbol for which feature importance is calculated.
        - current_user: Provides the current authenticated user context. Retrieved using `Depends(get_current_user)`.
    Returns:
        - dict: The importance of features associated with the provided symbol.
    Processing Logic:
        - Executes an asynchronous call to retrieve feature importance data using the symbol.
        - Handles exceptions by raising an HTTPException with a status code of 400 on failure."""
    try:
        features = await get_feature_importance(symbol)
        return features
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Error getting feature importance: {str(e)}"
        ) 