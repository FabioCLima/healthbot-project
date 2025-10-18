"""Nós do HealthBot Graph - MVP2.

Cada função representa um nó que processa o estado.
MVP2 adiciona interação com usuário através de mensagens.
"""

from typing import Any

from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

from healthbot.settings import settings
from healthbot.state import HealthBotState

# ============================================
# FUNÇÕES AUXILIARES
# ============================================


def extract_message_content(message: BaseMessage) -> str:
    """Extrai o conteúdo de uma mensagem de forma segura.

    Args:
        message: Mensagem do LangChain

    Returns:
        Conteúdo como string, garantindo compatibilidade com tipos complexos

    """
    content = message.content  # type: ignore[misc]

    # Se já é string, retorna diretamente
    if isinstance(content, str):
        return content

    # Se é lista, tenta extrair texto dos elementos
    if isinstance(content, list):  # type: ignore[misc]
        text_parts: list[str] = []
        for item in content:  # type: ignore[misc]
            if isinstance(item, str):
                text_parts.append(item)  # type: ignore[misc]
            elif isinstance(item, dict):  # type: ignore[misc]
                # Tenta extrair texto de dicionários (ex: conteúdo multimodal)
                if "text" in item:
                    text_parts.append(str(item["text"]))  # type: ignore[misc]
                else:
                    text_parts.append(str(item))  # type: ignore[misc]
            else:
                text_parts.append(str(item))  # type: ignore[misc]
        return " ".join(text_parts)  # type: ignore[misc]

    # Fallback: converte para string
    return str(content)  # type: ignore[misc]


# ============================================
# CONFIGURAÇÃO DAS FERRAMENTAS
# ============================================


def get_llm() -> ChatOpenAI:
    """Retorna uma instância do LLM OpenAI.

    Usamos gpt-4o-mini por ser mais barato e rápido.

    Returns:
        Instância configurada do ChatOpenAI

    """
    return ChatOpenAI(
        model=settings.openai_model,
        temperature=0.7,  # Criatividade moderada
    )


def get_tavily() -> TavilySearchResults:
    """Retorna a ferramenta de busca Tavily.

    Configurada para focar em fontes médicas confiáveis.

    Returns:
        Instância configurada do TavilySearchResults

    """
    return TavilySearchResults(
        max_results=3,  # Pega os 3 melhores resultados
        search_depth="advanced",  # Busca mais profunda
        include_answer=True,  # Inclui resposta resumida
        include_raw_content=False,  # Não precisa do HTML completo
    )


# ============================================
# NÓS DE INTERAÇÃO COM USUÁRIO (MVP2)
# ============================================

def ask_topic(_: HealthBotState) -> dict[str, Any]:
    """Nó 1 (MVP2): Pergunta ao usuário qual tópico de saúde quer aprender.

    Este é o ponto de entrada do fluxo interativo.

    Args:
        state: Estado atual do grafo

    Returns:
        Dict com mensagem perguntando o tópico

    """
    message = AIMessage(
        content=(
            "Olá! Sou o HealthBot, seu assistente de educação em saúde. 🏥\n\n"
            "Estou aqui para ajudá-lo a entender melhor sobre condições médicas "
            "e cuidados com a saúde.\n\n"
            "Sobre qual tema de saúde você gostaria de aprender hoje?\n"
            "(Exemplos: diabetes, hipertensão, asma, ansiedade)"
        )
    )

    print("🤖 HealthBot: Perguntando tópico ao usuário...")

    return {"messages": [message]}


def receive_topic(state: HealthBotState) -> dict[str, Any]:
    """Nó 2 (MVP2): Recebe e processa o tópico informado pelo usuário.

    Extrai o tópico da última mensagem humana no histórico.

    Args:
        state: Estado atual (deve ter pelo menos 1 HumanMessage)

    Returns:
        Dict com o tópico extraído

    """
    # Pega a última mensagem (deve ser do usuário)
    last_message = state["messages"][-1]

    if isinstance(last_message, HumanMessage):
        # Extrai o conteúdo da mensagem de forma segura
        topic = extract_message_content(last_message).strip()

        print(f"✅ Tópico recebido: {topic}")

        confirmation = AIMessage(
            content=f"Entendi! Vou buscar informações confiáveis sobre **{topic}**. "
            f"Aguarde um momento... 🔍"
        )

        return {
            "topic": topic,
            "messages": [confirmation],
        }

    # Fallback (não deveria chegar aqui)
    print("⚠️  Aviso: Mensagem não é do tipo HumanMessage")
    return {"topic": "saúde geral"}


# ============================================
# NÓS DE PROCESSAMENTO (mantidos do MVP1)
# ============================================

def search_tavily(state: HealthBotState) -> dict[str, Any]:
    """Nó 3: Busca informações sobre o tópico no Tavily.

    Args:
        state: Estado atual (precisa ter 'topic')

    Returns:
        Dict com os resultados da busca

    """
    topic = state["topic"]

    # Validação: se não tem tópico, retorna erro
    if not topic:
        print("❌ Erro: Nenhum tópico fornecido")
        return {"results": "Erro: Nenhum tópico fornecido."}

    print(f"🔍 Buscando informações sobre: {topic}")

    # Cria query otimizada para fontes médicas
    query = f"{topic} informações médicas confiáveis"

    # Busca no Tavily
    tavily = get_tavily()
    results = tavily.invoke({"query": query})  # type: ignore[misc]

    # Formata os resultados
    formatted_results = ""
    for i, result in enumerate(results, 1):
        formatted_results += f"\n--- Fonte {i} ---\n"
        formatted_results += f"URL: {result.get('url', 'N/A')}\n"
        formatted_results += f"Conteúdo: {result.get('content', 'N/A')}\n"

    print(f"✅ Encontradas {len(results)} fontes")

    return {"results": formatted_results}


def summarize(state: HealthBotState) -> dict[str, Any]:
    """Nó 4: Resume os resultados em linguagem acessível.

    Args:
        state: Estado atual (precisa ter 'topic' e 'results')

    Returns:
        Dict com o resumo gerado

    """
    topic = state["topic"]
    results = state["results"]

    # Validação
    if not topic or not results:
        print("❌ Erro: Faltam dados para resumir")
        return {"summary": "Erro: Faltam dados para resumir."}

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
    summary = extract_message_content(response)

    print(f"✅ Resumo gerado ({len(summary)} caracteres)")

    return {"summary": summary}


def present_summary(state: HealthBotState) -> dict[str, Any]:
    """Nó 5: Apresenta o resumo E pergunta se está pronto para continuar.

    Args:
        state: Estado atual (precisa ter 'summary')

    Returns:
        Dict com mensagens contendo o resumo e a pergunta

    """
    summary = state["summary"]

    # Validação
    if not summary:
        print("❌ Erro: Nenhum resumo disponível")
        return {"messages": [AIMessage(content="Erro: Nenhum resumo disponível.")]}

    # Exibe no console (para debug)
    print("\n" + "=" * 70)
    print("📋 RESUMO FINAL")
    print("=" * 70)
    print()
    print(summary)
    print()
    print("=" * 70)

    print("\n📄 Apresentando resumo ao usuário...")

    # Retorna 2 mensagens: o resumo e a pergunta
    return {
        "messages": [
            AIMessage(content=summary),
            AIMessage(
                content="\n---\n\n"
                "Quando estiver pronto para testar sua compreensão com um quiz, "
                "digite 'pronto' ou 'continuar'. ✅"
            ),
        ]
    }


def wait_for_ready(_: HealthBotState) -> dict[str, Any]:
    """Nó 6 (MVP2): Aguarda confirmação do usuário para continuar.

    Este nó não faz nada além de validar que o usuário confirmou.
    O grafo vai pausar ANTES deste nó (interrupt_before).

    Args:
        state: Estado atual

    Returns:
        Dict vazio (não atualiza o estado)

    """
    print("✅ Usuário confirmou prontidão")
    return {}
