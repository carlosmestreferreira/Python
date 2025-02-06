from flask import Flask, render_template_string, request
from emas import get_trading_symbols, fetch_symbol_data
from concurrent.futures import ThreadPoolExecutor
import pandas as pd
from secrets_1 import api_key, api_secret
from binance.client import Client

# Inicializa o cliente da Binance
client = Client(api_key, api_secret)

# Inicializa o Flask
app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    # Obtém os símbolos de futuros da Binance
    symbols = get_trading_symbols(client)

    # Função auxiliar para obter dados do símbolo
    def fetch_symbol_data_paralelo(symbol_name):
        return fetch_symbol_data(symbol_name, client)

    # Coleta dados em paralelo para todos os símbolos
    with ThreadPoolExecutor(max_workers=10) as executor:
        results = list(executor.map(fetch_symbol_data_paralelo, symbols))

    # Filtra resultados válidos
    data = [result for result in results if result]

    # Cria um DataFrame com os dados
    df = pd.DataFrame(data)

    # Processa o filtro de valores se houver submissão do formulário
    min_price = request.form.get('min_price', type=float, default=0)
    max_price = request.form.get('max_price', type=float, default=float('inf'))

    if not df.empty:
        df = df[(df['Preço M5'] >= min_price) & (df['Preço M5'] <= max_price)]

    # Gera uma tabela HTML manualmente com estilização por condição
    table_rows = ""
    for _, row in df.iterrows():
        color = 'lightgreen' if row['Condition'] == 'green' else 'lightcoral'
        # Link para o gráfico do símbolo na Binance
        symbol_link = f"https://www.binance.com/en/futures/{row['Símbolo']}"
        table_rows += f"<tr style='background-color: {color};'>"
        table_rows += f"<td><a href='{symbol_link}' target='_blank'>{row['Símbolo']}</a></td>"
        table_rows += f"<td>{row['Preço M5']}</td>"
        table_rows += f"<td>{row['EMA8']:.2f}</td>"
        table_rows += f"<td>{row['EMA21']:.2f}</td>"
        table_rows += f"<td>{row['EMA233']:.2f}</td>"
        table_rows += f"<td>{row['Modo']}</td>"
        table_rows += "</tr>"

    html_table = f"""
    <table class='table table-striped'>
        <thead>
            <tr>
                <th>Símbolo</th>
                <th>Preço M5</th>
                <th>EMA8</th>
                <th>EMA21</th>
                <th>EMA233</th>
                <th>Modo</th>
            </tr>
        </thead>
        <tbody>
            {table_rows}
        </tbody>
    </table>
    """

    # Renderiza a tabela no navegador
    return render_template_string('''
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Binance Futures - Símbolos e Preços M5</title>
            <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css">
        </head>
        <body>
            <div class="container">
                <h1 class="mt-5">Símbolos e Preços M5 (TRADING)</h1>
                <form method="POST" class="my-3">
                    <div class="form-row">
                        <div class="col">
                            <input type="number" step="0.01" name="min_price" class="form-control" placeholder="Preço Mínimo" value="{{ request.form.min_price }}">
                        </div>
                        <div class="col">
                            <input type="number" step="0.01" name="max_price" class="form-control" placeholder="Preço Máximo" value="{{ request.form.max_price }}">
                        </div>
                        <div class="col">
                            <button type="submit" class="btn btn-primary">Filtrar</button>
                        </div>
                    </div>
                </form>
                {{ table|safe }}
                <div class="mt-4">
                    <h4>Observação:</h4>
                    <ul>
                        <li><strong>Fundo verde:</strong> EMA8 acima de EMA21 (Modo LONG).</li>
                        <li><strong>Fundo vermelho:</strong> EMA8 abaixo de EMA21 (Modo SHORT).</li>
                    </ul>
                </div>
            </div>
        </body>
        </html>
    ''', table=html_table)

if __name__ == '__main__':
    app.run(debug=True)
