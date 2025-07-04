from typing import Optional, List
from pydantic import BaseModel, EmailStr, constr

# Shared properties
class UserBase(BaseModel):
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = True
    is_superuser: bool = False
    full_name: Optional[str] = None
    permissions: List[str] = []

# Properties to receive via API on creation
class UserCreate(UserBase):
    email: EmailStr
    password: constr(min_length=8)
    full_name: str
    permissions: List[str] = []

# Properties to receive via API on update
class UserUpdate(UserBase):
    password: Optional[constr(min_length=8)] = None

# Properties shared by models stored in DB
class UserInDBBase(UserBase):
    id: Optional[int] = None

    class Config:
        orm_mode = True

# Additional properties to return via API
class User(UserInDBBase):
    pass

# Additional properties stored in DB
class UserInDB(UserInDBBase):
    hashed_password: str

class UserResponse(UserInDBBase):
    pass 