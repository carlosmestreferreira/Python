import json

def salvar_dados_json(dados, nome_ficheiro):
    """Salva os dados fornecidos em um arquivo JSON."""
    try:
        with open(nome_ficheiro, 'w') as json_file:
            json.dump(dados, json_file, indent=4)
        print(f"Dados salvos com sucesso em {nome_ficheiro}.")
    except Exception as e:
        print(f"Erro ao salvar dados no ficheiro {nome_ficheiro}: {e}")
