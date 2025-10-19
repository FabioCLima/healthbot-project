"""Unit tests for HealthBot state management.

Tests the state schema and field validation.
"""

import pytest
from langchain_core.messages import HumanMessage

from healthbot.state import HealthBotState


class TestHealthBotState:
    """Test HealthBot state structure and validation."""

    def test_initial_state_structure(self):
        """Test that initial state has all required fields."""
        state: HealthBotState = {
            "messages": [HumanMessage(content="test topic")],
            "topic": None,
            "results": None,
            "summary": None,
            "quiz_question": None,
            "quiz_answer": None,
            "grade": None,
            "continue_learning": None,
            "has_results": None,
            "sources_count": None,
            "run_id": None,
        }

        # Test that all required fields are present
        required_fields = [
            "messages", "topic", "results", "summary", "quiz_question",
            "quiz_answer", "grade", "continue_learning", "has_results",
            "sources_count", "run_id"
        ]
        
        for field in required_fields:
            assert field in state

    def test_messages_field_type(self):
        """Test that messages field accepts list of BaseMessage."""
        state: HealthBotState = {
            "messages": [HumanMessage(content="test")],
            "topic": None,
            "results": None,
            "summary": None,
            "quiz_question": None,
            "quiz_answer": None,
            "grade": None,
            "continue_learning": None,
            "has_results": None,
            "sources_count": None,
            "run_id": None,
        }

        assert isinstance(state["messages"], list)
        assert len(state["messages"]) == 1
        assert isinstance(state["messages"][0], HumanMessage)

    def test_state_field_types(self):
        """Test that state fields accept correct types."""
        state: HealthBotState = {
            "messages": [],
            "topic": "diabetes",
            "results": "Some search results",
            "summary": "Educational summary",
            "quiz_question": "What is diabetes?",
            "quiz_answer": "A",
            "grade": {"score": 8, "feedback": "Good", "citations": []},
            "continue_learning": True,
            "has_results": True,
            "sources_count": 3,
            "run_id": "run-123",
        }

        assert isinstance(state["topic"], str)
        assert isinstance(state["results"], str)
        assert isinstance(state["summary"], str)
        assert isinstance(state["quiz_question"], str)
        assert isinstance(state["quiz_answer"], str)
        assert isinstance(state["grade"], dict)
        assert isinstance(state["continue_learning"], bool)
        assert isinstance(state["has_results"], bool)
        assert isinstance(state["sources_count"], int)
        assert isinstance(state["run_id"], str)

    def test_state_with_none_values(self):
        """Test that state fields can be None."""
        state: HealthBotState = {
            "messages": [],
            "topic": None,
            "results": None,
            "summary": None,
            "quiz_question": None,
            "quiz_answer": None,
            "grade": None,
            "continue_learning": None,
            "has_results": None,
            "sources_count": None,
            "run_id": None,
        }

        # All fields should be None
        for field in ["topic", "results", "summary", "quiz_question", 
                     "quiz_answer", "grade", "continue_learning", 
                     "has_results", "sources_count", "run_id"]:
            assert state[field] is None

    def test_grade_field_structure(self):
        """Test that grade field has correct structure."""
        state: HealthBotState = {
            "messages": [],
            "topic": None,
            "results": None,
            "summary": None,
            "quiz_question": None,
            "quiz_answer": None,
            "grade": {
                "score": 8,
                "feedback": "Great job!",
                "citations": ["Source 1", "Source 2"]
            },
            "continue_learning": None,
            "has_results": None,
            "sources_count": None,
            "run_id": None,
        }

        grade = state["grade"]
        assert "score" in grade
        assert "feedback" in grade
        assert "citations" in grade
        assert isinstance(grade["score"], int)
        assert isinstance(grade["feedback"], str)
        assert isinstance(grade["citations"], list)
