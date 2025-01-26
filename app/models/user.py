from sqlalchemy import Column, Integer, String, Enum
from ..database import Base
import enum

class UserRole(str, enum.Enum):
    ADMIN = "admin"
    GUEST = "guest"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String, unique=True, index=True)
    password = Column(String)
    phone = Column(String)
    email = Column(String, unique=True, index=True)
    phonezalo = Column(String)
    role = Column(Enum(UserRole), default=UserRole.GUEST)