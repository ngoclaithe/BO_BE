from fastapi import APIRouter, Depends, HTTPException
from typing import List
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.trade_service import TradeService
from app.utils.auth import get_current_user
from ..models.user import User
from ..schemas.trade import TradeResponse, UserTradeResponse, TradeCreate, TradeUpdate

router = APIRouter(prefix="/api/trades", tags=["Trades"])

def is_admin(user: User = Depends(get_current_user)):
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admins can perform this action")
    return user

@router.post("/", response_model=TradeResponse)
def create_trade(
    trade: TradeCreate, 
    db: Session = Depends(get_db), 
    user: User = Depends(is_admin)
):
    trade_service = TradeService(db)
    return trade_service.create_trade(trade)

@router.get("/{trade_id}", response_model=TradeResponse)
def get_trade(
    trade_id: int, 
    db: Session = Depends(get_db), 
    user: User = Depends(is_admin)
):
    trade_service = TradeService(db)
    return trade_service.get_trade(trade_id)

@router.get("/user/{user_id}", response_model=List[TradeResponse])
def get_trades_by_user(
    user_id: str, 
    db: Session = Depends(get_db), 
    user: User = Depends(is_admin)
):
    trade_service = TradeService(db)
    return trade_service.get_trades_by_user(user_id)

@router.put("/{trade_id}", response_model=TradeResponse)
def update_trade(
    trade_id: int, 
    trade: TradeUpdate, 
    db: Session = Depends(get_db), 
    user: User = Depends(is_admin)
):
    trade_service = TradeService(db)
    return trade_service.update_trade(trade_id, trade)

@router.delete("/{trade_id}")
def delete_trade(
    trade_id: int, 
    db: Session = Depends(get_db), 
    user: User = Depends(is_admin)
):
    trade_service = TradeService(db)
    trade_service.delete_trade(trade_id)
    return {"message": "Trade deleted successfully"}

@router.get("/pending/", response_model=List[TradeResponse])
def get_pending_trades(
    db: Session = Depends(get_db), 
    user: User = Depends(is_admin)
):
    trade_service = TradeService(db)
    return trade_service.get_pending_trades()

@router.get("/pending/{phonezalo}", response_model=UserTradeResponse)
def get_pending_trades_by_phonezalo(
    phonezalo: str, 
    db: Session = Depends(get_db), 
    user: User = Depends(is_admin)
):
    trade_service = TradeService(db)
    return trade_service.get_pending_trades_by_phonezalo(phonezalo)