"""Visualiza o fluxo do grafo HealthBot MVP2.

Execute: python src/healthbot/visualize_graph.py
"""

from graph import create_graph, GraphNodes


def visualize_graph_structure() -> None:
    """Visualiza a estrutura do grafo e explica o fluxo."""
    print("=" * 80)
    print("🔍 VISUALIZAÇÃO DO GRAFO HEALTHBOT MVP2")
    print("=" * 80)
    print()
    
    # Cria o grafo
    app = create_graph()
    graph_info = app.get_graph()
    
    print("📊 ESTRUTURA DO GRAFO:")
    print(f"   • Nós: {len(graph_info.nodes)} nós")
    print(f"   • Arestas: {len(graph_info.edges)} conexões")
    print()
    
    print("🔄 FLUXO LINEAR:")
    print("   START → ask_topic → [INTERRUPT] → receive_topic → search_tavily")
    print("   → summarize → present_summary → [INTERRUPT] → wait_for_ready → END")
    print()
    
    print("⚠️  PONTOS DE INTERRUPÇÃO:")
    print("   1. Antes de 'receive_topic' - Aguarda input do usuário")
    print("   2. Antes de 'wait_for_ready' - Aguarda confirmação para continuar")
    print()
    
    print("📋 DETALHES DOS NÓS:")
    nodes_info = {
        "ask_topic": "Pergunta ao usuário qual tópico quer aprender",
        "receive_topic": "Processa a resposta do usuário",
        "search_tavily": "Busca informações no Tavily",
        "summarize": "Gera resumo com LLM",
        "present_summary": "Apresenta resumo e pergunta se está pronto",
        "wait_for_ready": "Aguarda confirmação do usuário"
    }
    
    for node, description in nodes_info.items():
        print(f"   • {node}: {description}")
    print()
    
    print("🎯 CARACTERÍSTICAS DO FLUXO:")
    print("   ✅ Fluxo linear (sem condicionais)")
    print("   ✅ Human-in-the-Loop (2 pontos de interrupção)")
    print("   ✅ Checkpoints para persistir estado")
    print("   ✅ Mensagens conversacionais")
    print()
    
    print("💡 COMO FUNCIONA:")
    print("   1. Bot pergunta o tópico")
    print("   2. [PAUSA] - Usuário responde")
    print("   3. Bot busca informações")
    print("   4. Bot gera resumo")
    print("   5. Bot apresenta resumo")
    print("   6. [PAUSA] - Usuário confirma")
    print("   7. Bot finaliza")
    print()
    
    print("=" * 80)


def show_mermaid_diagram() -> None:
    """Mostra o código Mermaid para o diagrama."""
    print("📈 CÓDIGO MERMAID PARA O DIAGRAMA:")
    print()
    
    mermaid_code = """
graph TD
    START([START]) --> ask_topic[ask_topic<br/>Pergunta tópico]
    ask_topic --> |INTERRUPT| receive_topic[receive_topic<br/>Processa resposta]
    receive_topic --> search_tavily[search_tavily<br/>Busca Tavily]
    search_tavily --> summarize[summarize<br/>Gera resumo]
    summarize --> present_summary[present_summary<br/>Apresenta resumo]
    present_summary --> |INTERRUPT| wait_for_ready[wait_for_ready<br/>Aguarda confirmação]
    wait_for_ready --> END([END])
    
    classDef interrupt fill:#ffeb3b,stroke:#f57f17,stroke-width:3px
    classDef process fill:#4caf50,stroke:#2e7d32,stroke-width:2px
    classDef startend fill:#2196f3,stroke:#1565c0,stroke-width:3px
    
    class ask_topic,receive_topic,search_tavily,summarize,present_summary,wait_for_ready process
    class START,END startend
    """
    
    print(mermaid_code)
    print()
    print("💡 Para usar este diagrama:")
    print("   1. Copie o código acima")
    print("   2. Cole em https://mermaid.live/")
    print("   3. Ou use em documentação Markdown")


if __name__ == "__main__":
    visualize_graph_structure()
    print()
    show_mermaid_diagram()