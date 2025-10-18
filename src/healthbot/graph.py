"""Grafo do HealthBot - MVP2.

Define a estrutura do workflow interativo com Human-in-the-Loop.
"""

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, StateGraph
from langgraph.graph.state import CompiledStateGraph

from healthbot.nodes import (
    ask_topic,
    present_summary,
    receive_topic,
    search_tavily,
    summarize,
    wait_for_ready,
)
from healthbot.state import HealthBotState


class GraphNodes:
    """Constantes para os nós do grafo MVP2."""

    ASK_TOPIC = "ask_topic"
    RECEIVE_TOPIC = "receive_topic"
    SEARCH_TAVILY = "search_tavily"
    SUMMARIZE = "summarize"
    PRESENT_SUMMARY = "present_summary"
    WAIT_FOR_READY = "wait_for_ready"


def create_graph() -> CompiledStateGraph:
    """Cria e compila o grafo do MVP2 com Human-in-the-Loop.

    Fluxo:
        START → ask_topic → [INTERRUPT] → receive_topic → search_tavily
        → summarize → present_summary → [INTERRUPT] → wait_ready → END

    Os pontos de [INTERRUPT] pausam a execução para aguardar input do usuário.

    Returns:
        Grafo compilado com checkpointer e interrupções configuradas

    """
    # Cria o grafo com o tipo do estado
    workflow = StateGraph(HealthBotState)

    # ============================================
    # ADICIONA OS NÓS
    # ============================================
    workflow.add_node(GraphNodes.ASK_TOPIC, ask_topic)  # type: ignore[misc]
    workflow.add_node(GraphNodes.RECEIVE_TOPIC, receive_topic)  # type: ignore[misc]
    workflow.add_node(GraphNodes.SEARCH_TAVILY, search_tavily)  # type: ignore[misc]
    workflow.add_node(GraphNodes.SUMMARIZE, summarize)  # type: ignore[misc]
    workflow.add_node(GraphNodes.PRESENT_SUMMARY, present_summary)  # type: ignore[misc]
    workflow.add_node(GraphNodes.WAIT_FOR_READY, wait_for_ready)  # type: ignore[misc]

    # ============================================
    # DEFINE O PONTO DE ENTRADA
    # ============================================
    workflow.set_entry_point(GraphNodes.ASK_TOPIC)

    # ============================================
    # DEFINE AS CONEXÕES (ARESTAS)
    # ============================================
    workflow.add_edge(GraphNodes.ASK_TOPIC, GraphNodes.RECEIVE_TOPIC)
    workflow.add_edge(GraphNodes.RECEIVE_TOPIC, GraphNodes.SEARCH_TAVILY)
    workflow.add_edge(GraphNodes.SEARCH_TAVILY, GraphNodes.SUMMARIZE)
    workflow.add_edge(GraphNodes.SUMMARIZE, GraphNodes.PRESENT_SUMMARY)
    workflow.add_edge(GraphNodes.PRESENT_SUMMARY, GraphNodes.WAIT_FOR_READY)
    workflow.add_edge(GraphNodes.WAIT_FOR_READY, END)

    # ============================================
    # COMPILA O GRAFO COM CHECKPOINTER E INTERRUPTS
    # ============================================
    checkpointer = MemorySaver()

    return workflow.compile(  # type: ignore[return-value]
        checkpointer=checkpointer,
        interrupt_before=[GraphNodes.RECEIVE_TOPIC, GraphNodes.WAIT_FOR_READY],
    )


def run_mvp2_interactive() -> None:
    """Executa o fluxo interativo do MVP2 com Human-in-the-Loop.

    Esta função demonstra como usar o grafo compilado com checkpoints
    e interrupções para criar uma experiência conversacional.
    """
    print("=" * 70)
    print("🚀 EXECUTANDO MVP2 - HEALTHBOT INTERATIVO")
    print("=" * 70)
    print()

    # Cria o grafo
    app = create_graph()

    print("💡 Para usar este exemplo de forma completa, você precisaria:")
    print("1. Executar o grafo em um ambiente que suporte input do usuário")
    print("2. Capturar as mensagens de interrupção")
    print("3. Permitir que o usuário forneça input")
    print("4. Continuar a execução com o input fornecido")
    print()
    print("📋 Exemplo de configuração:")
    print("   thread_config = {'configurable': {'thread_id': 'healthbot-session-1'}}")
    print(
        "   initial_state = {'messages': [], 'topic': None, "
        "'results': None, 'summary': None}"
    )
    print()
    print("Este é o grafo configurado e pronto para execução interativa!")
    print(f"📊 Nós configurados: {len(app.get_graph().nodes)} nós")
    print(f"🔗 Conexões: {len(app.get_graph().edges)} arestas")
    print(
        f"⚠️  Pontos de interrupção: {GraphNodes.RECEIVE_TOPIC}, "
        f"{GraphNodes.WAIT_FOR_READY}"
    )
