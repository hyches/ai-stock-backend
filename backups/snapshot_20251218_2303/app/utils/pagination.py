from typing import List, TypeVar, Generic, Optional
from pydantic import BaseModel
from pydantic.generics import GenericModel

T = TypeVar('T')

class PaginatedResponse(GenericModel, Generic[T]):
    """Generic pagination response model"""
    items: List[T]
    total: int
    skip: int
    limit: int
    has_more: bool = False

    def __init__(self, **data):
        super().__init__(**data)
        self.has_more = (self.skip + self.limit) < self.total

    class Config:
        arbitrary_types_allowed = True 