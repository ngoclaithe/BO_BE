from pydantic import BaseModel
from typing import Optional

class WalletBase(BaseModel):
    userId: int
    current_balance: Optional[float] = 0.0

class WalletCreate(WalletBase):
    pass

class WalletUpdate(BaseModel):
    current_balance: Optional[float] = None

class Wallet(WalletBase):
    id: int

    class Config:
        orm_mode = True