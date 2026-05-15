from typing import List
from datetime import datetime, timezone
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

# Importações dos módulos locais do projeto
from database import engine, get_db
import models
import schemas

# Inicializa e cria as tabelas no banco de dados se não existirem
models.Base.metadata.create_all(bind=engine)

# DEFINIÇÃO DA VARIÁVEL EXIGIDA PELO UVICORN (main:app)
app = FastAPI(
    title="Crypto Wallet Monitor API",
    description="API para monitoramento de saldos de tokens na rede BSC.",
    version="1.0.0"
)

@app.get("/balances/latest", response_model=List[schemas.BalanceResponse])
def get_latest_balances(db: Session = Depends(get_db)):
    """Retorna o registro mais recente de cada carteira monitorada."""
    subquery = (
        db.query(
            models.WalletBalance.wallet_address,
            func.max(models.WalletBalance.collected_at).label("max_date")
        )
        .group_by(models.WalletBalance.wallet_address)
        .subquery()
    )

    latest_balances = (
        db.query(models.WalletBalance)
        .join(
            subquery,
            (models.WalletBalance.wallet_address == subquery.c.wallet_address) &
            (models.WalletBalance.collected_at == subquery.c.max_date)
        )
        .all()
    )
    return latest_balances

@app.get("/balances/{wallet}/history", response_model=List[schemas.BalanceResponse])
def get_wallet_history(wallet: str, db: Session = Depends(get_db)):
    """Retorna o histórico completo de coletas de uma carteira específica."""
    history = (
        db.query(models.WalletBalance)
        .filter(models.WalletBalance.wallet_address == wallet)
        .order_by(models.WalletBalance.collected_at.desc())
        .all()
    )
    if not history:
        raise HTTPException(status_code=404, detail="Carteira não encontrada ou sem histórico.")
    return history

@app.get("/stats", response_model=schemas.WalletStats)
def get_stats(db: Session = Depends(get_db)):
    """Retorna métricas consolidadas das carteiras monitoradas."""
    subquery = (
        db.query(
            models.WalletBalance.wallet_address,
            func.max(models.WalletBalance.collected_at).label("max_date")
        )
        .group_by(models.WalletBalance.wallet_address)
        .subquery()
    )

    current_balances = (
        db.query(models.WalletBalance)
        .join(
            subquery,
            (models.WalletBalance.wallet_address == subquery.c.wallet_address) &
            (models.WalletBalance.collected_at == subquery.c.max_date)
        )
        .all()
    )

    if not current_balances:
        raise HTTPException(status_code=404, detail="Sem dados suficientes para gerar estatísticas.")

    highest = max(current_balances, key=lambda x: x.balance)
    total_wallets = len(set(b.wallet_address for b in current_balances))

    return schemas.WalletStats(
        highest_balance_wallet=highest.wallet_address,
        highest_balance=highest.balance,
        total_monitored_wallets=total_wallets
    )
