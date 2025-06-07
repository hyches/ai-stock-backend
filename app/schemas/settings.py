from pydantic import BaseModel
from typing import Optional

class UserSettings(BaseModel):
    theme: Optional[str] = "light"
    notifications_enabled: Optional[bool] = True

class UserSettingsUpdate(BaseModel):
    theme: Optional[str]
    notifications_enabled: Optional[bool] 