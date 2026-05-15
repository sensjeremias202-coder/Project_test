import os
from datetime import datetime, timezone
from dotenv import load_dotenv
from sqlalchemy.orm import Session
from web3 import Web3

# Importações do nosso próprio projeto
from database import SessionLocal, engine
import models
from models import WalletBalance

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '.env'))

BSC_RPC_URL = os.getenv("BSC_RPC_URL")

# 3 Wallets Públicas da Binance para Monitoramento
WALLETS = [
    "0xF977814e90dA44bFA03b6295A0616a897441aceC",
    "0x28C6c06298d514Db089934071355E5743bf21d60",
    "0x8894E0a0c962CB723c1976a4421c95949bE2D4E3"
]

# Endereço do contrato do USDT na rede BSC
USDT_ADDRESS = Web3.to_checksum_address("0x55d398326f99059fF775485246999027B3197955")

# ABI Mínima para interagir com o token
MIN_ABI = [
    {"constant": True, "inputs": [{"name": "_owner", "type": "address"}], "name": "balanceOf", "outputs": [{"name": "balance", "type": "uint256"}], "type": "function"},
    {"constant": True, "inputs": [], "name": "decimals", "outputs": [{"name": "", "type": "uint8"}], "type": "function"},
    {"constant": True, "inputs": [], "name": "symbol", "outputs": [{"name": "", "type": "string"}], "type": "function"}
]

def run_collector():
    # CRIA A TABELA NO POSTGRESQL SE ELA NÃO EXISTIR
    models.Base.metadata.create_all(bind=engine)

    # Conecta à rede blockchain
    w3 = Web3(Web3.HTTPProvider(BSC_RPC_URL))
    if not w3.is_connected():
        print("Erro: Não foi possível conectar à RPC do BSC.")
        return

    db: Session = SessionLocal()
    contract = w3.eth.contract(address=USDT_ADDRESS, abi=MIN_ABI)
    
    try:
        # Busca metadados do token (decimais e símbolo)
        decimals = contract.functions.decimals().call()
        symbol = contract.functions.symbol().call()
        
        # Coleta o saldo de cada carteira da lista
        for wallet in WALLETS:
            checksum_wallet = Web3.to_checksum_address(wallet)
            balance_wei = contract.functions.balanceOf(checksum_wallet).call()
            balance_human = balance_wei / (10 ** decimals)
            
            # Prepara o registro para salvar no banco
            new_record = WalletBalance(
                wallet_address=checksum_wallet,
                token_symbol=symbol,
                balance=balance_human,
                collected_at=datetime.now(timezone.utc)
            )
            db.add(new_record)
            print(f"[{datetime.now()}] Coletado: {checksum_wallet} | {balance_human:.2f} {symbol}")
            
        # Salva em definitivo no PostgreSQL
        db.commit()
        print("Sucesso: Todos os saldos foram gravados no banco de dados!")
        
    except Exception as e:
        db.rollback()
        print(f"Erro durante a coleta: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    run_collector()
