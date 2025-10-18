"""Estado do HealthBot Graph - MVP1.

Define a estrutura de dados que circula entre os nós do grafo.
"""

from typing import TypedDict


class HealthBotState(TypedDict):
    """Estado do MVP1 - Fluxo linear básico.
    
    Attributes:
        topic: Tópico de saúde (ex: "diabetes", "hipertensão")
        results: Resultados brutos da busca no Tavily
        summary: Resumo em linguagem acessível gerado pelo LLM

    """

    topic: str
    results: str
    summary: str
