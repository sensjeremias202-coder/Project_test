from datetime import datetime
from pydantic import BaseModel, ConfigDict

class BalanceResponse(BaseModel):
    id: int
    wallet_address: str
    token_symbol: str
    balance: float
    collected_at: datetime

    model_config = ConfigDict(from_attributes=True)

class WalletStats(BaseModel):
    highest_balance_wallet: str
    highest_balance: float
    total_monitored_wallets: int
