from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from app.core.security import (
    Token, User, UserInDB, verify_password, create_access_token,
    get_current_user, get_password_hash
)
from app.schemas.user import UserCreate, UserResponse
from app.models.database import User
from sqlalchemy.orm import Session
from app.database import get_db
from typing import Optional

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

# Mock user database - Replace with actual database in production
fake_users_db = {
    "admin": {
        "username": "admin",
        "hashed_password": get_password_hash("admin123"),
        "disabled": False,
    }
}

def get_user(db, username: str):
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)

def authenticate_user(fake_db, username: str, password: str):
    user = get_user(fake_db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """Authenticate a user using OAuth2 password flow and return an access token.
    Parameters:
        - form_data (OAuth2PasswordRequestForm): Object containing the user's email and password.
        - db (Session): Database session used to query user information.
    Returns:
        - dict: Contains 'access_token' and 'token_type' values for the authenticated user.
    Processing Logic:
        - Searches the database for a user with the provided email.
        - Verifies the provided password against the hashed password stored in the database.
        - Raises an HTTP 401 error if authentication fails.
        - Generates and returns a JWT access token upon successful authentication."""
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/register", response_model=UserResponse)
async def register(user: UserCreate, db: Session = Depends(get_db)):
    """Registers a new user in the database.
    Parameters:
        - user (UserCreate): Object containing user details like email, password, and name.
        - db (Session, optional): Database session object for executing queries. Defaults to session from `get_db`.
    Returns:
        - User: The newly registered user object including all user details except the password.
    Processing Logic:
        - Checks if the user's email is already registered, and raises an HTTPException if it is.
        - Hashes the user's password before storing it in the database.
        - Saves the user into the database and refreshes the session to return the newly created user object."""
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    hashed_password = get_password_hash(user.password)
    db_user = User(
        email=user.email,
        hashed_password=hashed_password,
        full_name=user.name
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@router.post("/logout")
async def logout():
    # In a real app, you might want to blacklist the token
    return {"message": "Successfully logged out"}

@router.get("/me", response_model=UserResponse)
async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """Get the current user based on the provided token.
    Parameters:
        - token (str): The authentication token used for identifying the user; obtained through dependency injection.
        - db (Session): The database session used for querying the user information; obtained through dependency injection.
    Returns:
        - UserResponse: An instance representing the user extracted from the database.
    Processing Logic:
        - Searches for a user in the database by matching the email with the provided token.
        - Raises an HTTP 401 Unauthorized exception if the user is not found.
        - Converts the user information into a UserResponse object before returning."""
    user = db.query(User).filter(User.email == token).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return UserResponse.from_orm(user)

@router.get("/users/me", response_model=UserResponse)
async def read_users_me(current_user: User = Depends(get_current_user)):
    return UserResponse.from_orm(current_user) 