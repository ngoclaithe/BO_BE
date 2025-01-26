from sqlalchemy import Column, Integer, String, Enum, DateTime, Float
from sqlalchemy.sql import func
from ..database import Base

class Money(Base):
    __tablename__ = "moneys"

    id = Column(Integer, primary_key=True, autoincrement=True)
    userId = Column(Integer)
    type_trans = Column(String)
    number_moneys = Column(Integer)
    name_bank = Column(String)
    number_bank = Column(Integer)
    type_bank = Column(String)
    code = Column(String)
    time = Column(DateTime, default=func.now())
    result = Column(String, default="pending")