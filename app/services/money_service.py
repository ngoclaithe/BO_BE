from sqlalchemy.orm import Session
from ..models.money import Money
from ..schemas.money import MoneyCreate, MoneyResponse, MoneyUpdate
from datetime import datetime
from ..models.wallet import Wallet
from typing import Optional, List

class MoneyService:
    def __init__(self, db: Session):
        self.db = db

    def create_money(self, money: MoneyCreate) -> MoneyResponse:

        db_money = Money(
            userId=money.userId,
            type_trans=money.type_trans,
            number_moneys=money.number_moneys,
            name_bank=money.name_bank,
            number_bank=money.number_bank,
            type_bank=money.type_bank,
            time=money.time,
            code=money.code,
            result="pending"
        )
        self.db.add(db_money)
        self.db.commit()
        self.db.refresh(db_money)
        return db_money

    def get_money_by_id(self, money_id: int) -> MoneyResponse:

        return self.db.query(Money).filter(Money.id == money_id).first()
    def get_money_by_user_id(self, userId: int) -> List[MoneyResponse]:

        return self.db.query(Money).filter(Money.userId == userId).all()

    def update_money(self, money_id: int, money: MoneyUpdate) -> MoneyResponse:

        db_money = self.db.query(Money).filter(Money.id == money_id).first()
        if not db_money:
            return None

        for key, value in money.dict(exclude_unset=True).items():
            setattr(db_money, key, value)

        if db_money.type_trans == "nap" and db_money.result == "success":
            self._update_wallet_balance(db_money.userId, db_money.number_moneys, "add")
        elif db_money.type_trans == "rut" and db_money.result == "success":
            self._update_wallet_balance(db_money.userId, db_money.number_moneys, "subtract")

        self.db.commit()
        self.db.refresh(db_money)
        return db_money

    def delete_money(self, money_id: int) -> bool:

        db_money = self.db.query(Money).filter(Money.id == money_id).first()
        if not db_money:
            return False

        self.db.delete(db_money)
        self.db.commit()
        return True

    def _update_wallet_balance(self, user_id: int, amount: float, operation: str):

        db_wallet = self.db.query(Wallet).filter(Wallet.userId == user_id).first()
        if not db_wallet:
            raise ValueError(f"Ví của người dùng với ID {user_id} không tồn tại.")

        if operation == "add":
            db_wallet.current_balance += amount
        elif operation == "subtract":
            if db_wallet.current_balance < amount:
                raise ValueError("Số dư ví không đủ để thực hiện giao dịch rút tiền.")
            db_wallet.current_balance -= amount
        else:
            raise ValueError("Phép toán không hợp lệ.")

        self.db.commit()
        self.db.refresh(db_wallet)