from web3 import Web3

# 1. Configurações Prontas (Carteira Pública Binance e Token USDT)
WALLET_ADDRESS = "0xF977814e90dA44bFA03b6295A0616a897441aceC"
TOKEN_ADDRESS = "0x55d398326f99059fF775485246999027B3197955"

# ABI Mínima para traduzir os dados do Token
MIN_ABI = [
    {"constant": True, "inputs": [{"name": "_owner", "type": "address"}], "name": "balanceOf", "outputs": [{"name": "balance", "type": "uint256"}], "type": "function"},
    {"constant": True, "inputs": [], "name": "decimals", "outputs": [{"name": "", "type": "uint8"}], "type": "function"},
    {"constant": True, "inputs": [], "name": "symbol", "outputs": [{"name": "", "type": "string"}], "type": "function"}
]

def main():
    # Conexão com o servidor público e atualizado da rede BSC
    bsc_url = "https://bsc-dataseed.binance.org"
    w3 = Web3(Web3.HTTPProvider(bsc_url))

    if not w3.is_connected():
        print("Erro ao conectar à rede BSC. Verifique sua internet ou tente outra RPC.")
        return

    # Ajusta os endereços para o formato correto exigido pela biblioteca (Checksum)
    wallet = Web3.to_checksum_address(WALLET_ADDRESS)
    token = Web3.to_checksum_address(TOKEN_ADDRESS)

    # 1. Busca o bloco atual da rede
    block = w3.eth.block_number

    # 2. Busca o saldo de BNB Nativo e transforma em valor legível
    bnb_wei = w3.eth.get_balance(wallet)
    bnb_balance = w3.from_wei(bnb_wei, 'ether')

    # 3. Conecta com o contrato do Token (USDT) para ver o saldo dele
    token_contract = w3.eth.contract(address=token, abi=MIN_ABI)
    
    token_wei = token_contract.functions.balanceOf(wallet).call()
    decimals = token_contract.functions.decimals().call()
    symbol = token_contract.functions.symbol().call()
    
    # Transforma o saldo do token em valor legível usando as casas decimais dele
    token_balance = token_wei / (10 ** decimals)

    # Mostra os resultados limpos na tela
    print("\n=========================================")
    print(f"Bloco Atual da BSC: {block}")
    print(f"Carteira Consultada: {wallet}")
    print("-----------------------------------------")
    print(f"Saldo de BNB Nativo: {bnb_balance:.4f} BNB")
    print(f"Saldo de {symbol}: {token_balance:.2f} {symbol}")
    print("=========================================\n")

if __name__ == "__main__":
    main()
