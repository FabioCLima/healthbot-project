"""Teste simples dos nós do HealthBot - MVP1.

Execute: python src/healthbot/test_nodes_simple.py
"""

import inspect
import sys
from typing import TYPE_CHECKING

from healthbot.nodes import (
    get_llm,
    get_tavily,
    print_summary,
    search_tavily,
    set_topic,
    summarize,
)

if TYPE_CHECKING:
    from healthbot.state import HealthBotState


def test_factories() -> None:
    """Testa as funções factory."""
    print("🔧 Testando factories...")

    # Teste get_llm
    llm = get_llm()
    if llm is None:
        raise ValueError("get_llm retornou None")
    if not hasattr(llm, "invoke"):
        raise ValueError("get_llm não tem método invoke")
    print("  ✅ get_llm() funcionando")

    # Teste get_tavily
    tavily = get_tavily()
    if tavily is None:
        raise ValueError("get_tavily retornou None")
    if not hasattr(tavily, "invoke"):
        raise ValueError("get_tavily não tem método invoke")
    print("  ✅ get_tavily() funcionando")


def test_set_topic() -> None:
    """Testa o nó set_topic."""
    print("\n📝 Testando set_topic...")

    state: HealthBotState = {"topic": "", "results": "", "summary": ""}
    result = set_topic(state)

    if result != {"topic": "diabetes"}:
        raise ValueError(f"set_topic retornou {result}, esperado {{'topic': 'diabetes'}}")
    if not isinstance(result, dict):
        raise ValueError(f"set_topic retornou {type(result)}, esperado dict")
    print("  ✅ set_topic retorna 'diabetes' corretamente")


def test_search_tavily_structure() -> None:
    """Testa a estrutura do search_tavily (sem chamada real)."""
    print("\n🔍 Testando estrutura do search_tavily...")

    # Verifica se a função existe e tem a assinatura correta
    sig = inspect.signature(search_tavily)
    if "state" not in sig.parameters:
        raise ValueError("search_tavily não tem parâmetro 'state'")
    print("  ✅ search_tavily tem parâmetro 'state'")

    # Verifica se pode ser chamada (mas não vamos fazer chamada real para economizar API)
    if not callable(search_tavily):
        raise ValueError("search_tavily não é chamável")
    print("  ✅ search_tavily é chamável")


def test_summarize_structure() -> None:
    """Testa a estrutura do summarize (sem chamada real)."""
    print("\n📄 Testando estrutura do summarize...")

    sig = inspect.signature(summarize)
    if "state" not in sig.parameters:
        raise ValueError("summarize não tem parâmetro 'state'")
    print("  ✅ summarize tem parâmetro 'state'")

    if not callable(summarize):
        raise ValueError("summarize não é chamável")
    print("  ✅ summarize é chamável")


def test_print_summary() -> None:
    """Testa o print_summary."""
    print("\n📋 Testando print_summary...")

    state: HealthBotState = {
        "topic": "diabetes",
        "results": "resultados de teste...",
        "summary": "Este é um resumo de teste sobre diabetes."
    }

    result = print_summary(state)
    if result != {}:
        raise ValueError(f"print_summary retornou {result}, esperado {{}}")
    print("  ✅ print_summary retorna dict vazio")


def test_state_flow() -> None:
    """Testa o fluxo básico do estado."""
    print("\n🔄 Testando fluxo do estado...")

    # Estado inicial
    state: HealthBotState = {"topic": "", "results": "", "summary": ""}
    print(f"  Estado inicial: {state}")

    # Aplica set_topic
    state.update(set_topic(state))
    if state["topic"] != "diabetes":
        raise ValueError(f"topic = '{state['topic']}', esperado 'diabetes'")
    print(f"  Após set_topic: topic = '{state['topic']}'")

    # Simula resultado do search_tavily
    state.update({"results": "Resultados simulados do Tavily..."})
    if len(state["results"]) <= 0:
        raise ValueError("results está vazio")
    print(f"  Após search_tavily: results tem {len(state['results'])} caracteres")

    # Simula resultado do summarize
    state.update({"summary": "Resumo simulado do LLM..."})
    if len(state["summary"]) <= 0:
        raise ValueError("summary está vazio")
    print(f"  Após summarize: summary tem {len(state['summary'])} caracteres")

    print("  ✅ Fluxo do estado funcionando corretamente")


def main() -> int:
    """Executa todos os testes.

    Returns:
        0 se todos os testes passaram, 1 caso contrário

    """
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

    except Exception as e:
        print(f"\n❌ ERRO: {e}")
        return 1
    else:
        return 0


if __name__ == "__main__":
    sys.exit(main())
