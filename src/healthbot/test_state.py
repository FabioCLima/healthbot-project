"""Testa o Estado do HealthBot - MVP2.

Execute: python src/healthbot/test_state.py
"""

from typing import TYPE_CHECKING

from langchain_core.messages import AIMessage, HumanMessage

if TYPE_CHECKING:
    from healthbot.state import HealthBotState


def main() -> None:
    """Testa a criação do estado com mensagens."""
    print("=" * 60)
    print("🧪 TESTANDO O ESTADO DO MVP2")
    print("=" * 60)
    print()

    # Cria um estado com mensagens
    state: HealthBotState = {
        "messages": [
            AIMessage(content="Olá! Qual tópico?"),
            HumanMessage(content="Diabetes"),
            AIMessage(content="Entendi! Buscando..."),
        ],
        "topic": "diabetes",
        "results": "Resultados de exemplo...",
        "summary": "Resumo de exemplo...",
    }

    print("✅ Estado criado com sucesso!")
    print()
    print("📋 Mensagens no histórico:")
    for i, msg in enumerate(state["messages"], 1):
        msg_type = "🤖 AI" if isinstance(msg, AIMessage) else "👤 Human"
        print(f"   {i}. {msg_type}: {msg.content}")
    print()
    print(f"📝 Topic: {state['topic']}")
    print()

    # Testa estado inicial (com None)
    print("🧪 Testando estado inicial (com None):")
    initial_state: HealthBotState = {
        "messages": [],
        "topic": None,
        "results": None,
        "summary": None,
    }
    print(f"   ✅ Estado inicial válido: {initial_state}")
    print()

    print("=" * 60)
    print("🎉 Estado MVP2 funcionando!")
    print("=" * 60)


if __name__ == "__main__":
    main()
