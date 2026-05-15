from datetime import datetime, timezone
from sqlalchemy import Column, DateTime, Float, Integer, String
from database import Base

class WalletBalance(Base):
    __tablename__ = "wallet_balances"

    id = Column(Integer, primary_key=True, index=True)
    wallet_address = Column(String, index=True, nullable=False)
    token_symbol = Column(String, index=True, nullable=False)
    balance = Column(Float, nullable=False)
    collected_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
