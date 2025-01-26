from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..database import get_db
from ..schemas.wallet import WalletCreate, WalletUpdate, Wallet
from ..services.wallet_service import WalletService
from ..utils.auth import get_current_user
from typing import List

router = APIRouter(prefix="/api/wallets", tags=["Wallets"])

@router.post("/", response_model=Wallet)
def create_wallet(wallet: WalletCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin can create wallets",
        )
    wallet_service = WalletService(db)
    existing_wallet = wallet_service.get_wallet_by_user_id(wallet.userId)
    if existing_wallet:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Wallet already exists for this user",
        )
    return wallet_service.create_wallet(wallet)

@router.get("/me", response_model=Wallet)
def get_my_wallet(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    wallet_service = WalletService(db)
    wallet = wallet_service.get_wallet_by_user_id(current_user.id)
    if not wallet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Wallet not found",
        )
    return wallet

@router.put("/me", response_model=Wallet)
def update_my_wallet(wallet: WalletUpdate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin can update wallets",
        )
    wallet_service = WalletService(db)
    db_wallet = wallet_service.get_wallet_by_user_id(current_user.id)
    if not db_wallet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Wallet not found",
        )
    return wallet_service.update_wallet(db_wallet.id, wallet)

@router.delete("/me", response_model=Wallet)
def delete_my_wallet(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin can delete wallets",
        )
    wallet_service = WalletService(db)
    db_wallet = wallet_service.get_wallet_by_user_id(current_user.id)
    if not db_wallet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Wallet not found",
        )
    return wallet_service.delete_wallet(db_wallet.id)

@router.get("/{user_id}", response_model=Wallet)
def get_wallet_by_user_id(user_id: str, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin can access this endpoint",
        )
    wallet_service = WalletService(db)
    wallet = wallet_service.get_wallet_by_user_id(user_id)
    if not wallet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Wallet not found",
        )
    return wallet

@router.get("/", response_model=List[Wallet])
def get_all_wallets(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin can access this endpoint",
        )
    wallet_service = WalletService(db)
    return wallet_service.get_all_wallets()