from sqlalchemy.orm import Session
from ..models.wallet import Wallet
from ..schemas.wallet import WalletCreate, WalletUpdate

class WalletService:
    def __init__(self, db: Session):
        self.db = db

    def create_wallet(self, wallet: WalletCreate):
        db_wallet = Wallet(userId=wallet.userId, current_balance=wallet.current_balance)
        self.db.add(db_wallet)
        self.db.commit()
        self.db.refresh(db_wallet)
        return db_wallet

    def get_wallet(self, wallet_id: int):
        return self.db.query(Wallet).filter(Wallet.id == wallet_id).first()

    def get_wallet_by_user_id(self, user_id: str):
        return self.db.query(Wallet).filter(Wallet.userId == user_id).first()

    def update_wallet(self, wallet_id: int, wallet: WalletUpdate):
        db_wallet = self.get_wallet(wallet_id)
        if db_wallet:
            if wallet.current_balance is not None:
                db_wallet.current_balance = wallet.current_balance
            self.db.commit()
            self.db.refresh(db_wallet)
        return db_wallet

    def delete_wallet(self, wallet_id: int):
        db_wallet = self.get_wallet(wallet_id)
        if db_wallet:
            self.db.delete(db_wallet)
            self.db.commit()
        return db_wallet