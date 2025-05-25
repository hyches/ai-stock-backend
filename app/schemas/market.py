from pydantic import BaseModel
from typing import List

class StockData(BaseModel):
    symbol: str
    price: float
    name: str = ""
    currency: str = "USD"

class SymbolSearch(BaseModel):
    symbol: str
    name: str

class SymbolSearchResults(BaseModel):
    results: List[SymbolSearch] 