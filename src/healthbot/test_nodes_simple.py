"""Teste simples dos nós do HealthBot - MVP1.

Execute: python src/healthbot/test_nodes_simple.py
"""

import sys

from healthbot.nodes import (
    get_llm,
    get_tavily,
    print_summary,
    search_tavily,
    set_topic,
    summarize,
)
from healthbot.state import HealthBotState


def test_factories():
    """Testa as funções factory."""
    print("🔧 Testando factories...")

    # Teste get_llm
    llm = get_llm()
    assert llm is not None
    assert hasattr(llm, "invoke")
    print("  ✅ get_llm() funcionando")

    # Teste get_tavily
    tavily = get_tavily()
    assert tavily is not None
    assert hasattr(tavily, "invoke")
    print("  ✅ get_tavily() funcionando")


def test_set_topic():
    """Testa o nó set_topic."""
    print("\n📝 Testando set_topic...")

    state: HealthBotState = {"topic": "", "results": "", "summary": ""}
    result = set_topic(state)

    assert result == {"topic": "diabetes"}
    assert isinstance(result, dict)
    print("  ✅ set_topic retorna 'diabetes' corretamente")


def test_search_tavily_structure():
    """Testa a estrutura do search_tavily (sem chamada real)."""
    print("\n🔍 Testando estrutura do search_tavily...")

    # Verifica se a função existe e tem a assinatura correta
    import inspect
    sig = inspect.signature(search_tavily)
    assert "state" in sig.parameters
    print("  ✅ search_tavily tem parâmetro 'state'")

    # Verifica se pode ser chamada (mas não vamos fazer chamada real para economizar API)
    state: HealthBotState = {"topic": "diabetes", "results": "", "summary": ""}
    assert callable(search_tavily)
    print("  ✅ search_tavily é chamável")


def test_summarize_structure():
    """Testa a estrutura do summarize (sem chamada real)."""
    print("\n📄 Testando estrutura do summarize...")

    import inspect
    sig = inspect.signature(summarize)
    assert "state" in sig.parameters
    print("  ✅ summarize tem parâmetro 'state'")

    assert callable(summarize)
    print("  ✅ summarize é chamável")


def test_print_summary():
    """Testa o print_summary."""
    print("\n📋 Testando print_summary...")

    state: HealthBotState = {
        "topic": "diabetes",
        "results": "resultados de teste...",
        "summary": "Este é um resumo de teste sobre diabetes."
    }

    result = print_summary(state)
    assert result == {}
    print("  ✅ print_summary retorna dict vazio")


def test_state_flow():
    """Testa o fluxo básico do estado."""
    print("\n🔄 Testando fluxo do estado...")

    # Estado inicial
    state: HealthBotState = {"topic": "", "results": "", "summary": ""}
    print(f"  Estado inicial: {state}")

    # Aplica set_topic
    state.update(set_topic(state))
    assert state["topic"] == "diabetes"
    print(f"  Após set_topic: topic = '{state['topic']}'")

    # Simula resultado do search_tavily
    state.update({"results": "Resultados simulados do Tavily..."})
    assert len(state["results"]) > 0
    print(f"  Após search_tavily: results tem {len(state['results'])} caracteres")

    # Simula resultado do summarize
    state.update({"summary": "Resumo simulado do LLM..."})
    assert len(state["summary"]) > 0
    print(f"  Após summarize: summary tem {len(state['summary'])} caracteres")

    print("  ✅ Fluxo do estado funcionando corretamente")


def main():
    """Executa todos os testes."""
    print("=" * 60)
    print("🧪 TESTANDO NODES.PY - MVP1 (VERSÃO SIMPLES)")
    print("=" * 60)

    try:
        test_factories()
        test_set_topic()
        test_search_tavily_structure()
        test_summarize_structure()
        test_print_summary()
        test_state_flow()

        print("\n" + "=" * 60)
        print("🎉 TODOS OS TESTES PASSARAM!")
        print("=" * 60)
        print("\n💡 Para testes mais avançados com mocks, use:")
        print("   pytest tests/test_nodes.py -v")

        return 0

    except Exception as e:
        print(f"\n❌ ERRO: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
