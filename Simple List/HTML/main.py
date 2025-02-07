from flask import Flask, render_template
from binance_utils import obter_pares_futuros, obter_precos_futuros_concorrentes
from file_utils import salvar_dados_json

app = Flask(__name__)

@app.route('/')
def home():
    # Obter os pares futuros ativos
    pares_futuros = obter_pares_futuros()

    # Obter preços futuros
    precos = obter_precos_futuros_concorrentes(pares_futuros)

    # Salvar os dados em JSON
    salvar_dados_json(precos, 'precos_futuros_threads.json')

    # Renderizar a página com os dados
    return render_template('index.html', precos=precos)


if __name__ == "__main__":
    app.run(debug=True)
