"""Estado do HealthBot Graph - MVP2.

Define o schema de estado para o grafo de conversação do HealthBot.
"""

from typing import Annotated, TypedDict

from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages


class HealthBotState(TypedDict):
    """Representa o estado do grafo do HealthBot.

    Este estado é passado entre os nós do grafo, acumulando informações
    ao longo do fluxo da conversa.

    Attributes:
        messages: A lista de mensagens da conversa. Acumula o histórico.
        topic: O tópico de saúde extraído da pergunta do usuário.
            Pode ser `None` no início do fluxo.
        results: Os resultados da pesquisa obtidos da ferramenta de busca (Tavily).
            Pode ser `None` até a execução do nó de busca.
        summary: O resumo conciso gerado pelo LLM com base nos resultados da pesquisa.
            Pode ser `None` até a execução do nó de sumarização.

    """

    # O `add_messages` garante que novas mensagens sejam anexadas à lista existente
    # em vez de substituí-la.
    messages: Annotated[list[BaseMessage], add_messages]

    # Campos que são populados durante a execução do grafo.
    topic: str | None
    results: str | None
    summary: str | None
