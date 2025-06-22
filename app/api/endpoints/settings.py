from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api import deps
from app.schemas.settings import Settings, SettingsUpdate

router = APIRouter()

@router.get("/", response_model=Settings)
def read_settings(
    db: Session = Depends(deps.get_db),
    current_user = Depends(deps.get_current_active_user),
):
    """
    Retrieve user settings.
    """
    # This is a mock response.
    return {
        "modelType": "lstm",
        "predictionHorizon": 10,
        "confidenceThreshold": 0.8,
        "featureImportance": True,
        "autoRetrain": False,
        "retrainInterval": 7,
        "dataSource": "yahoo_finance",
        "apiKey": "mock_api_key_for_testing"
    }


@router.patch("/", response_model=Settings)
def update_settings(
    *,
    db: Session = Depends(deps.get_db),
    settings_in: SettingsUpdate,
    current_user = Depends(deps.get_current_active_user),
):
    """
    Update user settings.
    """
    # This is a mock response.
    return {
        "modelType": "lstm",
        "predictionHorizon": 10,
        "confidenceThreshold": 0.8,
        "featureImportance": True,
        "autoRetrain": False,
        "retrainInterval": 7,
        "dataSource": "yahoo_finance",
        "apiKey": "mock_api_key_for_testing"
    } 