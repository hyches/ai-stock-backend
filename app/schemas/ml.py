from pydantic import BaseModel
from typing import List, Dict, Any

class PredictionRequest(BaseModel):
    data: List[Any]

class PredictionResponse(BaseModel):
    predictions: List[Any]

class ModelPerformanceResponse(BaseModel):
    accuracy: float
    loss: float

class FeatureImportanceResponse(BaseModel):
    feature_importance: Dict[str, float]

class ModelPerformance(BaseModel):
    accuracy: float
    loss: float

class FeatureImportance(BaseModel):
    feature_importance: Dict[str, float] 