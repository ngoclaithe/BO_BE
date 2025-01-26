from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class MoneyBase(BaseModel):
    userId: int
    type_trans: str
    number_moneys: int
    name_bank: str
    number_bank: int
    type_bank: str
    time: datetime
    type_bank: str
    code: Optional[str] = None
    result: Optional[str] = "pending"
    
class MoneyCreate(MoneyBase):
    pass

class MoneyResponse(MoneyBase):
    id: int

    class Config:
        from_attributes  = True
        
class MoneyUpdate(BaseModel):
    userId: Optional[int] = None
    result: Optional[str] = None