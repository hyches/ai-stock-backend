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
    """Retrieve user settings based on the current authenticated user.
    Parameters:
        - current_user (User): The authenticated user. Automatically injected through dependency.
        - db (Session): Database session for accessing user data. Automatically injected through dependency.
    Returns:
        - dict: The settings of the currently authenticated user.
    Processing Logic:
        - Attempts to access the settings attribute of the current user.
        - Raises an HTTPException with status code 400 if there's an error accessing the settings."""
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
    """Updates user settings based on provided values.
    Parameters:
        - settings (UserSettingsUpdate): Object containing the new settings values to update.
        - current_user (User, optional): The currently authenticated user whose settings will be updated. Defaults to a dependency that retrieves the current user.
        - db (Session, optional): Database session used for committing changes. Defaults to a dependency that provides the database session.
    Returns:
        - UserSettings: The updated settings of the user.
    Processing Logic:
        - Iterates through the settings provided, updating only those that are set.
        - Changes are committed to the database immediately upon update.
        - Refreshes the current user's settings to ensure the returned object reflects the latest database state."""
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