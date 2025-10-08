# main.py

import os
from dotenv import load_dotenv

def setup_environment():
    """
    Carrega as variáveis de ambiente do arquivo config.env e valida as chaves essenciais.
    """
    # Carrega o arquivo config.env da raiz do projeto
    load_dotenv('config.env')

    # Validação das chaves de API
    required_keys = [
        'OPENAI_API_KEY',
        'TAVILY_API_KEY',
        'LANGCHAIN_API_KEY'
    ]

    for key in required_keys:
        if not os.getenv(key):
            raise ValueError(f"Chave API '{key}' não encontrada no ambiente. Verifique seu arquivo config.env.")

    # Garante que o projeto LangSmith seja definido
    if not os.getenv('LANGCHAIN_PROJECT'):
        os.environ['LANGCHAIN_PROJECT'] = 'HealthBot Prototype'

    print("✅ Ambiente configurado com sucesso.")

if __name__ == "__main__":
    setup_environment()
    # Aqui é onde a lógica principal da nossa aplicação irá rodar.
    print("🚀 HealthBot iniciado.")