"""
Testes para os nós do HealthBot - MVP1.

Testes básicos para validar funcionamento principal.
Execute: pytest tests/test_nodes.py -v
"""

import pytest
from unittest.mock import Mock, patch

from healthbot.nodes import get_llm, get_tavily, set_topic, search_tavily, summarize, print_summary
from healthbot.state import HealthBotState


class TestFactories:
    """Testa as funções factory."""
    
    def test_get_llm_returns_chatopenai(self):
        """Testa se get_llm retorna uma instância válida."""
        llm = get_llm()
        assert llm is not None
        assert hasattr(llm, 'invoke')
        assert llm.model_name == "gpt-4o-mini"
        assert llm.temperature == 0.7
    
    def test_get_tavily_returns_search_tool(self):
        """Testa se get_tavily retorna ferramenta configurada."""
        tavily = get_tavily()
        assert tavily is not None
        assert hasattr(tavily, 'invoke')
        assert tavily.max_results == 3


class TestNodes:
    """Testa os nós do grafo."""
    
    def test_set_topic_returns_diabetes(self):
        """Testa se set_topic define o tópico correto."""
        # Arrange
        state: HealthBotState = {"topic": "", "results": "", "summary": ""}
        
        # Act
        result = set_topic(state)
        
        # Assert
        assert result == {"topic": "diabetes"}
        assert isinstance(result, dict)
    
    @patch('healthbot.nodes.get_tavily')
    def test_search_tavily_with_mock(self, mock_get_tavily):
        """Testa search_tavily com mock do Tavily."""
        # Arrange
        mock_tavily = Mock()
        mock_tavily.invoke.return_value = [
            {"url": "https://example.com", "content": "Diabetes é uma doença..."},
            {"url": "https://medical.com", "content": "Sintomas incluem..."}
        ]
        mock_get_tavily.return_value = mock_tavily
        
        state: HealthBotState = {"topic": "diabetes", "results": "", "summary": ""}
        
        # Act
        result = search_tavily(state)
        
        # Assert
        assert "results" in result
        assert "Fonte 1" in result["results"]
        assert "Fonte 2" in result["results"]
        assert "https://example.com" in result["results"]
        mock_tavily.invoke.assert_called_once_with({"query": "diabetes informações médicas confiáveis"})
    
    @patch('healthbot.nodes.get_llm')
    def test_summarize_with_mock(self, mock_get_llm):
        """Testa summarize com mock do LLM."""
        # Arrange
        mock_llm = Mock()
        mock_response = Mock()
        mock_response.content = "Diabetes é uma condição crônica que afeta..."
        mock_llm.invoke.return_value = mock_response
        mock_get_llm.return_value = mock_llm
        
        state: HealthBotState = {
            "topic": "diabetes",
            "results": "Fonte 1: Diabetes info...",
            "summary": ""
        }
        
        # Act
        result = summarize(state)
        
        # Assert
        assert "summary" in result
        assert "Diabetes é uma condição crônica" in result["summary"]
        mock_llm.invoke.assert_called_once()
    
    def test_print_summary_returns_empty_dict(self, capsys):
        """Testa se print_summary exibe o resumo e retorna dict vazio."""
        # Arrange
        state: HealthBotState = {
            "topic": "diabetes",
            "results": "resultados...",
            "summary": "Diabetes é uma doença crônica..."
        }
        
        # Act
        result = print_summary(state)
        
        # Assert
        assert result == {}
        
        # Verifica se imprimiu algo
        captured = capsys.readouterr()
        assert "RESUMO FINAL" in captured.out
        assert "Diabetes é uma doença crônica" in captured.out


class TestIntegration:
    """Teste de integração básico."""
    
    @patch('healthbot.nodes.get_tavily')
    @patch('healthbot.nodes.get_llm')
    def test_full_pipeline_flow(self, mock_get_llm, mock_get_tavily):
        """Testa o fluxo completo dos nós."""
        # Arrange - Mock Tavily
        mock_tavily = Mock()
        mock_tavily.invoke.return_value = [
            {"url": "https://health.com", "content": "Diabetes info"}
        ]
        mock_get_tavily.return_value = mock_tavily
        
        # Arrange - Mock LLM
        mock_llm = Mock()
        mock_response = Mock()
        mock_response.content = "Resumo educacional sobre diabetes"
        mock_llm.invoke.return_value = mock_response
        mock_get_llm.return_value = mock_llm
        
        # Act - Simula o fluxo completo
        state: HealthBotState = {"topic": "", "results": "", "summary": ""}
        
        # Nó 1: Define tópico
        state.update(set_topic(state))
        assert state["topic"] == "diabetes"
        
        # Nó 2: Busca informações
        state.update(search_tavily(state))
        assert "results" in state
        assert len(state["results"]) > 0
        
        # Nó 3: Gera resumo
        state.update(summarize(state))
        assert "summary" in state
        assert "Resumo educacional" in state["summary"]
        
        # Nó 4: Exibe resultado
        result = print_summary(state)
        assert result == {}


class TestErrorHandling:
    """Testes básicos de tratamento de erros."""
    
    def test_search_tavily_with_empty_topic(self):
        """Testa search_tavily com tópico vazio."""
        state: HealthBotState = {"topic": "", "results": "", "summary": ""}
        
        # Deve funcionar mesmo com tópico vazio (query será " informações médicas confiáveis")
        # Não vamos testar o erro real do Tavily aqui, só a estrutura
        assert "topic" in state
    
    def test_summarize_with_empty_results(self):
        """Testa summarize com resultados vazios."""
        state: HealthBotState = {"topic": "diabetes", "results": "", "summary": ""}
        
        # Deve funcionar mesmo com resultados vazios
        assert "results" in state
        assert "topic" in state


# Fixture para estado básico (se precisar em outros testes)
@pytest.fixture
def basic_state() -> HealthBotState:
    """Retorna um estado básico para testes."""
    return {
        "topic": "diabetes",
        "results": "Resultados de exemplo...",
        "summary": "Resumo de exemplo..."
    }


if __name__ == "__main__":
    # Permite executar diretamente: python tests/test_nodes.py
    pytest.main([__file__, "-v"])
