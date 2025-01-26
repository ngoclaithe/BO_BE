from sqlalchemy.orm import Session
from ..models.trade import Trade
from ..models.user import User  
from ..schemas.trade import TradeCreate, TradeUpdate, TradeResponse, UserTradeResponse 
from datetime import datetime
from ..services.wallet_service import WalletService

class TradeService:
    def __init__(self, db: Session):
        self.db = db
        self.wallet_service = WalletService(db)  

    def create_trade(self, trade: TradeCreate) -> TradeResponse:
        db_trade = Trade(
            symbol=trade.symbol,
            userId=trade.userId,
            time_predict=trade.time_predict,
            type_predict=trade.type_predict,
            deposit=trade.deposit,
            current_price=trade.current_price,
            result=trade.result
        )
        self.db.add(db_trade)
        self.db.commit()
        self.db.refresh(db_trade)
        return db_trade

    def get_trade(self, trade_id: int) -> TradeResponse:
        db_trade = self.db.query(Trade).filter(Trade.id == trade_id).first()
        if not db_trade:
            raise ValueError(f"Trade with ID {trade_id} not found")
        return db_trade

    def get_trades_by_user(self, user_id: str) -> list[TradeResponse]:
        db_trades = self.db.query(Trade).filter(Trade.userId == user_id).all()
        return db_trades

    def update_trade(self, trade_id: int, trade: TradeUpdate) -> TradeResponse:
        db_trade = self.db.query(Trade).filter(Trade.id == trade_id).first()
        if not db_trade:
            raise ValueError(f"Trade with ID {trade_id} not found")

        if trade.result:
            db_trade.result = trade.result

            if trade.result in ["win", "lose"]:
                wallet = self.wallet_service.get_wallet_by_user_id(db_trade.userId)
                if not wallet:
                    raise ValueError(f"Wallet for user ID {db_trade.userId} not found")

                deposit_amount = float(db_trade.deposit)  
                if trade.result == "win":
                    wallet.current_balance += deposit_amount
                elif trade.result == "lose":
                    wallet.current_balance -= deposit_amount

                self.db.commit()

        self.db.commit()
        self.db.refresh(db_trade)
        return db_trade

    def delete_trade(self, trade_id: int) -> None:
        db_trade = self.db.query(Trade).filter(Trade.id == trade_id).first()
        if not db_trade:
            raise ValueError(f"Trade with ID {trade_id} not found")
        self.db.delete(db_trade)
        self.db.commit()

    def get_pending_trades(self) -> list[TradeResponse]:
        db_trades = self.db.query(Trade).filter(Trade.result == "pending").all()
        return db_trades

    def get_pending_trades_by_phonezalo(self, phonezalo: str) -> UserTradeResponse:
        user = self.db.query(User).filter(User.phonezalo == phonezalo).first()
        if not user:
            raise ValueError(f"User with phonezalo {phonezalo} not found")

        db_trades = self.db.query(Trade).filter(Trade.userId == user.id, Trade.result == "pending").all()

        return UserTradeResponse(
            id=user.id,
            phonezalo=user.phonezalo,
            email=user.email,
            pending_trades=db_trades
        )