from pydantic import BaseModel
from typing import Optional, Dict
from datetime import datetime

class AlertBase(BaseModel):
    message: str
    level: str = "info"
    source: str = "system"
    metadata: Optional[Dict] = None

class AlertCreate(AlertBase):
    pass

class AlertUpdate(BaseModel):
    read: Optional[bool] = None

class Alert(AlertBase):
    id: int
    created_at: datetime
    read: bool

    class Config:
        orm_mode = True
