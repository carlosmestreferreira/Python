import pandas as pd
from binance.client import Client

def calculate_ema(symbol, period, client, interval='5m'):
    """
    Calcula a Exponential Moving Average (EMA) de um símbolo com o período dado para o gráfico de 5 minutos.
    :param symbol: O símbolo do ativo (ex: 'BTCUSDT')
    :param period: O período da EMA (ex: 8, 21, 233)
    :param client: Cliente da Binance
    :param interval: Intervalo de tempo (default é '5m' para 5 minutos)
    :return: O valor da EMA
    """
    # Obtém os dados históricos (candlesticks) do símbolo com o intervalo de 5 minutos
    klines = client.futures_klines(symbol=symbol, interval=interval, limit=1000)
    
    # Converte para um DataFrame
    df = pd.DataFrame(klines, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'quote_asset_volume', 'number_of_trades', 'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'])
    
    # Converte o timestamp para datetime
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    
    # Converte os preços de fechamento para float
    df['close'] = df['close'].astype(float)
    
    # Calcula a EMA para o período desejado
    ema = df['close'].ewm(span=period, adjust=False).mean().iloc[-1]
    
    return ema

def get_emas(symbol, client, interval='5m'):
    """
    Calcula as EMAs para os períodos 8, 21 e 233 para o gráfico de 5 minutos.
    :param symbol: O símbolo do ativo (ex: 'BTCUSDT')
    :param client: Cliente da Binance
    :param interval: Intervalo de tempo (default é '5m' para 5 minutos)
    :return: Um dicionário com os valores das EMAs
    """
    emas = {
        'EMA_8': calculate_ema(symbol, 8, client, interval),
        'EMA_21': calculate_ema(symbol, 21, client, interval),
        'EMA_233': calculate_ema(symbol, 233, client, interval)
    }
    return emas

def get_trading_symbols(client):
    """
    Obtém os símbolos de futuros da Binance que estão em operação (status 'TRADING').
    :param client: Cliente da Binance
    :return: Lista de símbolos que estão em operação
    """
    futures_exchange_info = client.futures_exchange_info()
    return [symbol['symbol'] for symbol in futures_exchange_info['symbols'] if symbol['status'] == 'TRADING']

def fetch_symbol_data(symbol_name, client):
    """
    Obtém os dados de um símbolo, calcula as EMAs e retorna as informações.
    :param symbol_name: O nome do símbolo (ex: 'BTCUSDT')
    :param client: Cliente da Binance
    :return: Um dicionário com as informações calculadas para o símbolo
    """
    try:
        # Obtém as EMAs
        emas = get_emas(symbol_name, client)

        # Obtém o preço atual (último fechamento)
        klines = client.futures_klines(symbol=symbol_name, interval='5m', limit=200)
        close_prices = [float(kline[4]) for kline in klines]
        current_price = close_prices[-1]
        
        # Determina a condição e o modo
        condition = 'green' if emas['EMA_8'] > emas['EMA_21'] else 'red'
        market_mode = 'LONG' if emas['EMA_8'] > emas['EMA_21'] else 'SHORT'

        return {
            'Símbolo': symbol_name,
            'Preço M5': current_price,
            'EMA8': emas['EMA_8'],
            'EMA21': emas['EMA_21'],
            'EMA233': emas['EMA_233'],
            'Condition': condition,
            'Modo': market_mode
        }
    except Exception as e:
        print(f"Erro ao processar {symbol_name}: {e}")
        return None
