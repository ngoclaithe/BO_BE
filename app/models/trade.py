from sqlalchemy import Column, Integer, String, Enum, DateTime, Float
from sqlalchemy.sql import func
from ..database import Base

class Trade(Base):
    __tablename__ = "trades"

    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String)
    userId = Column(Integer)
    time_predict = Column(DateTime, default=func.now())  
    type_predict = Column(String)
    current_price = Column(Float)
    deposit = Column(String)
    result = Column(String, default="pending")