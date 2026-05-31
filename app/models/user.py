from sqlalchemy import Column, Integer, String
from app.database import Base


class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    fernet_key_hash = Column(String, nullable=True)

    @property
    def has_fernet_key(self) -> bool:
        return bool(self.fernet_key_hash)
