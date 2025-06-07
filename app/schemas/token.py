from typing import Optional, List
from pydantic import BaseModel

class Token(BaseModel):
    access_token: str
    token_type: str
    permissions: List[str]

class TokenPayload(BaseModel):
    sub: Optional[int] = None
    permissions: List[str] = [] 