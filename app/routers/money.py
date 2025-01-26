from fastapi import APIRouter, Depends, HTTPException
from typing import List
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.money_service import MoneyService
from app.utils.auth import get_current_user
from ..models.user import User
from ..schemas.money import MoneyCreate, MoneyResponse, MoneyUpdate

router = APIRouter(prefix="/api/moneys", tags=["Moneys"])

def is_admin(user: User = Depends(get_current_user)):
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admins can perform this action")
    return user

@router.post("/", response_model=MoneyResponse)
def create_money(
    money: MoneyCreate, 
    db: Session = Depends(get_db)
):
    money_service = MoneyService(db)
    return money_service.create_money(money)

@router.get("/", response_model=List[MoneyResponse])
def get_all_moneys(
    skip: int = 0, 
    limit: int = 10, 
    db: Session = Depends(get_db)
):
    money_service = MoneyService(db)
    return money_service.get_all_moneys(skip, limit)

@router.get("/{money_id}", response_model=MoneyResponse)
def get_money(
    money_id: int, 
    db: Session = Depends(get_db)
):
    money_service = MoneyService(db)
    db_money = money_service.get_money_by_id(money_id)
    if not db_money:
        raise HTTPException(status_code=404, detail="Money not found")
    return db_money
@router.get("/user/{userId}", response_model=List[MoneyResponse])
def get_all_moneys(
    userId: int,
    db: Session = Depends(get_db)
):
    money_service = MoneyService(db)
    return money_service.get_money_by_user_id(userId)
@router.put("/{money_id}", response_model=MoneyResponse)
def update_money(
    money_id: int, 
    money: MoneyUpdate, 
    db: Session = Depends(get_db), 
    user: User = Depends(is_admin)
):
    money_service = MoneyService(db)
    db_money = money_service.update_money(money_id, money)
    if not db_money:
        raise HTTPException(status_code=404, detail="Money not found")
    return db_money

@router.delete("/{money_id}", response_model=bool)
def delete_money(
    money_id: int, 
    db: Session = Depends(get_db), 
    user: User = Depends(is_admin)
):
    money_service = MoneyService(db)
    success = money_service.delete_money(money_id)
    if not success:
        raise HTTPException(status_code=404, detail="Money not found")
    return success