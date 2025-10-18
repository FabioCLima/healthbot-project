"""Grafo do HealthBot - MVP1.

Define a estrutura do workflow e conecta os nós.
"""

from typing import cast

from langgraph.graph import END, StateGraph
from langgraph.graph.state import CompiledStateGraph

from healthbot.nodes import print_summary, search_tavily, set_topic, summarize
from healthbot.state import HealthBotState


def create_graph() -> CompiledStateGraph:
    """Cria e compila o grafo do MVP1.

    Fluxo:
        START → set_topic → search_tavily → summarize → print_summary → END

    Returns:
        Grafo compilado pronto para execução

    """
    # Cria o grafo com o tipo do estado
    workflow = StateGraph(HealthBotState)

    # ============================================
    # ADICIONA OS NÓS
    # ============================================
    workflow.add_node("set_topic", set_topic)  # type: ignore[misc]
    workflow.add_node("search_tavily", search_tavily)  # type: ignore[misc]
    workflow.add_node("summarize", summarize)  # type: ignore[misc]
    workflow.add_node("print_summary", print_summary)  # type: ignore[misc]

    # ============================================
    # DEFINE O PONTO DE ENTRADA
    # ============================================
    workflow.set_entry_point("set_topic")

    # ============================================
    # DEFINE AS CONEXÕES (ARESTAS)
    # ============================================
    workflow.add_edge("set_topic", "search_tavily")
    workflow.add_edge("search_tavily", "summarize")
    workflow.add_edge("summarize", "print_summary")
    workflow.add_edge("print_summary", END)

    # ============================================
    # COMPILA O GRAFO
    # ============================================
    return workflow.compile()  # type: ignore[return-value]


def run_mvp1() -> HealthBotState:
    """Executa o fluxo completo do MVP1.

    Returns:
        Estado final após execução

    """
    print("=" * 70)
    print("🚀 EXECUTANDO MVP1 - HEALTHBOT")
    print("=" * 70)
    print()

    # Cria o grafo
    app = create_graph()

    # Estado inicial (vazio)
    initial_state: HealthBotState = {
        "topic": "",
        "results": "",
        "summary": "",
    }

    # Executa o grafo
    final_state: HealthBotState = cast("HealthBotState", app.invoke(initial_state))

    print()
    print("=" * 70)
    print("✅ MVP1 CONCLUÍDO COM SUCESSO!")
    print("=" * 70)

    return final_state
