from flask import Flask, render_template
from binance.client import Client
from secrets_1 import api_key, api_secret
from concurrent.futures import ThreadPoolExecutor, as_completed
import json

app = Flask(__name__)

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
    with ThreadPoolExecutor(max_workers=50) as executor:
        futures = {executor.submit(obter_preco_kline, par): par for par in pares}
        for future in as_completed(futures):
            resultado = future.result()
            if resultado:
                precos.append(resultado)
    return precos


@app.route('/')
def home():
    # Obter os pares futuros ativos
    pares_futuros = obter_pares_futuros()

    # Obter preços futuros
    precos = obter_precos_futuros_concorrentes(pares_futuros)

    # Salvar os dados em JSON
    with open('precos_futuros_threads.json', 'w') as json_file:
        json.dump(precos, json_file, indent=4)

    # Renderizar a página com os dados
    return render_template('index.html', precos=precos)


if __name__ == "__main__":
    app.run(debug=True)
