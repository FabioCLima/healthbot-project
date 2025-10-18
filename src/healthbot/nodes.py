"""Nós do HealthBot Graph - MVP1.

Cada função representa um nó que processa o estado.
"""

from typing import Any

from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

from healthbot.settings import settings
from healthbot.state import HealthBotState

# ============================================
# CONFIGURAÇÃO DAS FERRAMENTAS
# ============================================


def get_llm() -> ChatOpenAI:
    """Retorna uma instância do LLM OpenAI.
    
    Usamos gpt-4o-mini por ser mais barato e rápido.
    """
    return ChatOpenAI(
        model=settings.openai_model,
        temperature=0.7,  # Criatividade moderada
    )


def get_tavily() -> TavilySearchResults:
    """Retorna a ferramenta de busca Tavily.
    
    Configurada para focar em fontes médicas confiáveis.
    """
    return TavilySearchResults(
        max_results=3,  # Pega os 3 melhores resultados
        search_depth="advanced",  # Busca mais profunda
        include_answer=True,  # Inclui resposta resumida
        include_raw_content=False,  # Não precisa do HTML completo
    )


# ============================================
# NÓS DO GRAFO
# ============================================

def set_topic(state: HealthBotState) -> dict[str, Any]:
    """Nó 1: Define o tópico de saúde (hardcoded para MVP1).
    
    Args:
        state: Estado atual do grafo
        
    Returns:
        Dict com o tópico atualizado

    """
    topic = "diabetes"

    print(f"📝 Tópico definido: {topic}")

    return {"topic": topic}


def search_tavily(state: HealthBotState) -> dict[str, Any]:
    """Nó 2: Busca informações sobre o tópico no Tavily.
    
    Args:
        state: Estado atual (precisa ter 'topic')
        
    Returns:
        Dict com os resultados da busca

    """
    topic = state["topic"]

    print(f"🔍 Buscando informações sobre: {topic}")

    # Cria query otimizada para fontes médicas
    query = f"{topic} informações médicas confiáveis"

    # Busca no Tavily
    tavily = get_tavily()
    results = tavily.invoke({"query": query})  # type: ignore

    # Formata os resultados
    formatted_results = ""
    for i, result in enumerate(results, 1):
        formatted_results += f"\n--- Fonte {i} ---\n"
        formatted_results += f"URL: {result.get('url', 'N/A')}\n"
        formatted_results += f"Conteúdo: {result.get('content', 'N/A')}\n"

    print(f"✅ Encontradas {len(results)} fontes")

    return {"results": formatted_results}


def summarize(state: HealthBotState) -> dict[str, Any]:
    """Nó 3: Resume os resultados em linguagem acessível.
    
    Args:
        state: Estado atual (precisa ter 'topic' e 'results')
        
    Returns:
        Dict com o resumo gerado

    """
    topic = state["topic"]
    results = state["results"]

    print(f"📄 Gerando resumo sobre: {topic}")

    # Prompt para o LLM
    system_msg = SystemMessage(
        content=(
            "Você é um educador de saúde especializado em comunicar "
            "informações médicas de forma clara e acessível para pacientes.\n\n"
            "Crie um resumo educacional que:\n"
            "- Use linguagem simples (evite jargão médico)\n"
            "- Seja preciso e baseado nas fontes\n"
            "- Tenha entre 200-250 palavras\n"
            "- Seja informativo e prático"
        )
    )

    user_msg = HumanMessage(
        content=(
            f"Crie um resumo educacional sobre **{topic}** "
            f"baseado nestas fontes:\n\n{results}"
        )
    )

    # Gera o resumo
    llm = get_llm()
    response = llm.invoke([system_msg, user_msg])
    summary = str(response.content)  # type: ignore  # Garante que seja string

    print(f"✅ Resumo gerado ({len(summary)} caracteres)")

    return {"summary": summary}


def print_summary(state: HealthBotState) -> dict[str, Any]:
    """Nó 4: Exibe o resumo final.
    
    Args:
        state: Estado atual (precisa ter 'summary')
        
    Returns:
        Dict vazio (não atualiza o estado)

    """
    summary = state["summary"]

    print("\n" + "=" * 70)
    print("📋 RESUMO FINAL")
    print("=" * 70)
    print()
    print(summary)
    print()
    print("=" * 70)

    return {}  # Não precisa atualizar nada
