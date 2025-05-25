from fastapi import APIRouter, Depends, HTTPException
from app.core.security import get_current_user
from app.schemas.settings import UserSettings, UserSettingsUpdate
from app.models.database import User
from sqlalchemy.orm import Session
from app.database import get_db

router = APIRouter()

@router.get("/", response_model=UserSettings)
async def get_settings(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        return current_user.settings
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Error getting settings: {str(e)}"
        )

@router.patch("/", response_model=UserSettings)
async def update_settings(
    settings: UserSettingsUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        for key, value in settings.dict(exclude_unset=True).items():
            setattr(current_user.settings, key, value)
        db.commit()
        db.refresh(current_user)
        return current_user.settings
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Error updating settings: {str(e)}"
        ) 