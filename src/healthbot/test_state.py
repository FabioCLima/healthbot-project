"""Testa o Estado do HealthBot.
Execute: python src/healthbot/test_state.py
"""

from healthbot.state import HealthBotState


def main():
    """Testa a criação do estado."""
    print("=" * 60)
    print("🧪 TESTANDO O ESTADO DO MVP1")
    print("=" * 60)
    print()

    # Cria um estado de exemplo
    state: HealthBotState = {
        "topic": "diabetes",
        "results": "Resultados de exemplo do Tavily...",
        "summary": "Resumo de exemplo do LLM...",
    }

    print("✅ Estado criado com sucesso!")
    print()
    print("📋 Conteúdo do estado:")
    for key, value in state.items():
        value_str: str = str(value)  # Garante que value seja string
        preview = value_str[:50] + "..." if len(value_str) > 50 else value_str
        print(f"   {key}: {preview}")
    print()
    print("=" * 60)
    print("🎉 Estado funcionando!")
    print("=" * 60)


if __name__ == "__main__":
    main()
