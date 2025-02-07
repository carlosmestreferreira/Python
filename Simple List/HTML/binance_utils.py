from binance.client import Client
from secrets_1 import api_key, api_secret
from concurrent.futures import ThreadPoolExecutor, as_completed

# Criação do cliente da Binance
client = Client(api_key, api_secret)

def obter_pares_futuros():
    """Obtém todos os pares de futuros ativos."""
    futures_exchange_info = client.futures_exchange_info()
    return [symbol['symbol'] for symbol in futures_exchange_info['symbols'] if symbol['status'] == 'TRADING']

def obter_preco_kline(par):
    """Obtém o preço de fechamento do último Kline para um par específico."""
    try:
        kline = client.futures_klines(symbol=par, interval=Client.KLINE_INTERVAL_1MINUTE, limit=1)
        if kline:
            return {'symbol': par, 'price': kline[0][4]}  # Preço de fechamento
    except Exception as e:
        print(f"Erro ao obter Kline para {par}: {e}")
    return None

def obter_precos_futuros_concorrentes(pares):
    """Obtém preços futuros usando threads para melhor desempenho."""
    precos = []
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = {executor.submit(obter_preco_kline, par): par for par in pares}
        for future in as_completed(futures):
            resultado = future.result()
            if resultado:
                precos.append(resultado)
    return precos
