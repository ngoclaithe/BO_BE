from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class TradeBase(BaseModel):
    symbol: str
    userId: int
    time_predict: datetime
    type_predict: str
    deposit: str
    current_price: Optional[float] = None
    result: Optional[str] = "pending"

class TradeCreate(TradeBase):
    pass

class TradeResponse(TradeBase):
    id: int

    class Config:
        from_attributes  = True

class TradeUpdate(BaseModel):
    symbol: Optional[str] = None
    userId: Optional[int] = None
    time_predict: Optional[datetime] = None
    type_predict: Optional[str] = None
    deposit: Optional[str] = None
    current_price: Optional[float] = None
    result: Optional[str] = None

class UserTradeResponse(BaseModel):
    id: int
    phonezalo: str
    email: str
    pending_trades: List[TradeResponse]

    class Config:
        from_attributes  = True