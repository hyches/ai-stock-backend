from pydantic import BaseModel
from typing import Optional

class SettingsBase(BaseModel):
    modelType: Optional[str] = "lstm"
    predictionHorizon: Optional[int] = 10
    confidenceThreshold: Optional[float] = 0.8
    featureImportance: Optional[bool] = True
    autoRetrain: Optional[bool] = False
    retrainInterval: Optional[int] = 7
    dataSource: Optional[str] = "yahoo_finance"
    apiKey: Optional[str] = None

class Settings(SettingsBase):
    pass

class SettingsUpdate(SettingsBase):
    pass 