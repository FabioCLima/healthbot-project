"""Unit tests for HealthBot nodes.

Tests the core node functionality including user interaction,
processing, and quiz system nodes.
"""

import pytest
from unittest.mock import Mock, patch
from langchain_core.messages import AIMessage, HumanMessage

from healthbot.nodes import (
    _normalize_quiz_answer,
    receive_answer,
    should_continue,
    handle_no_results,
)
from healthbot.state import HealthBotState


class TestAnswerNormalization:
    """Test quiz answer normalization functionality."""

    def test_normalize_single_letters(self):
        """Test normalization of single letter answers."""
        assert _normalize_quiz_answer("A") == "A"
        assert _normalize_quiz_answer("a") == "A"
        assert _normalize_quiz_answer("B") == "B"
        assert _normalize_quiz_answer("b") == "B"
        assert _normalize_quiz_answer("C") == "C"
        assert _normalize_quiz_answer("c") == "C"
        assert _normalize_quiz_answer("D") == "D"
        assert _normalize_quiz_answer("d") == "D"

    def test_normalize_numbers(self):
        """Test normalization of number answers."""
        assert _normalize_quiz_answer("1") == "A"
        assert _normalize_quiz_answer("2") == "B"
        assert _normalize_quiz_answer("3") == "C"
        assert _normalize_quiz_answer("4") == "D"

    def test_normalize_option_formats(self):
        """Test normalization of 'option X' formats."""
        assert _normalize_quiz_answer("option A") == "A"
        assert _normalize_quiz_answer("OPTION B") == "B"
        assert _normalize_quiz_answer("Alternative C") == "C"
        assert _normalize_quiz_answer("ALTERNATIVE D") == "D"

    def test_normalize_with_whitespace(self):
        """Test normalization with whitespace."""
        assert _normalize_quiz_answer("  A  ") == "A"
        assert _normalize_quiz_answer("\tB\n") == "B"
        assert _normalize_quiz_answer("  C  ") == "C"

    def test_normalize_invalid_inputs(self):
        """Test normalization of invalid inputs."""
        assert _normalize_quiz_answer("") == ""
        assert _normalize_quiz_answer("X") == ""
        assert _normalize_quiz_answer("5") == ""
        assert _normalize_quiz_answer("invalid") == ""

    def test_normalize_first_character_fallback(self):
        """Test fallback to first character."""
        assert _normalize_quiz_answer("A is correct") == "A"
        assert _normalize_quiz_answer("B seems right") == "B"


class TestReceiveAnswer:
    """Test the receive_answer node."""

    def test_receive_valid_answer(self):
        """Test receiving a valid answer from user."""
        state: HealthBotState = {
            "messages": [HumanMessage(content="A")],
            "topic": "diabetes",
            "results": "Some results",
            "summary": "Some summary",
            "quiz_question": "Test question?",
            "quiz_answer": None,
            "grade": None,
            "continue_learning": None,
            "has_results": True,
            "sources_count": 3,
            "run_id": "test-run-123",
        }

        result = receive_answer(state)
        
        assert result["quiz_answer"] == "A"

    def test_receive_normalized_answer(self):
        """Test receiving and normalizing an answer."""
        state: HealthBotState = {
            "messages": [HumanMessage(content="b")],
            "topic": "diabetes",
            "results": "Some results",
            "summary": "Some summary",
            "quiz_question": "Test question?",
            "quiz_answer": None,
            "grade": None,
            "continue_learning": None,
            "has_results": True,
            "sources_count": 3,
            "run_id": "test-run-123",
        }

        result = receive_answer(state)
        
        assert result["quiz_answer"] == "B"

    def test_receive_non_human_message(self):
        """Test handling non-human messages."""
        state: HealthBotState = {
            "messages": [AIMessage(content="This is AI")],
            "topic": "diabetes",
            "results": "Some results",
            "summary": "Some summary",
            "quiz_question": "Test question?",
            "quiz_answer": None,
            "grade": None,
            "continue_learning": None,
            "has_results": True,
            "sources_count": 3,
            "run_id": "test-run-123",
        }

        result = receive_answer(state)
        
        assert result["quiz_answer"] == ""


class TestShouldContinue:
    """Test the should_continue routing function."""

    def test_continue_learning_true(self):
        """Test routing when user wants to continue."""
        state: HealthBotState = {
            "messages": [],
            "topic": "diabetes",
            "results": "Some results",
            "summary": "Some summary",
            "quiz_question": "Test question?",
            "quiz_answer": "A",
            "grade": {"score": 8, "feedback": "Good", "citations": []},
            "continue_learning": True,
            "has_results": True,
            "sources_count": 3,
            "run_id": "test-run-123",
        }

        result = should_continue(state)
        assert result == "ask_topic"

    def test_continue_learning_false(self):
        """Test routing when user wants to end."""
        state: HealthBotState = {
            "messages": [],
            "topic": "diabetes",
            "results": "Some results",
            "summary": "Some summary",
            "quiz_question": "Test question?",
            "quiz_answer": "A",
            "grade": {"score": 8, "feedback": "Good", "citations": []},
            "continue_learning": False,
            "has_results": True,
            "sources_count": 3,
            "run_id": "test-run-123",
        }

        result = should_continue(state)
        assert result == "end"

    def test_continue_learning_none(self):
        """Test routing when continue_learning is None."""
        state: HealthBotState = {
            "messages": [],
            "topic": "diabetes",
            "results": "Some results",
            "summary": "Some summary",
            "quiz_question": "Test question?",
            "quiz_answer": "A",
            "grade": {"score": 8, "feedback": "Good", "citations": []},
            "continue_learning": None,
            "has_results": True,
            "sources_count": 3,
            "run_id": "test-run-123",
        }

        result = should_continue(state)
        assert result == "end"


class TestHandleNoResults:
    """Test the handle_no_results node."""

    def test_handle_no_results_message(self):
        """Test handling no search results."""
        state: HealthBotState = {
            "messages": [],
            "topic": "rare disease",
            "results": None,
            "summary": None,
            "quiz_question": None,
            "quiz_answer": None,
            "grade": None,
            "continue_learning": None,
            "has_results": False,
            "sources_count": 0,
            "run_id": "test-run-123",
        }

        result = handle_no_results(state)
        
        assert "messages" in result
        assert len(result["messages"]) == 1
        assert isinstance(result["messages"][0], AIMessage)
        assert "rare disease" in result["messages"][0].content
        assert "couldn't find reliable medical information" in result["messages"][0].content

    def test_handle_no_results_suggestions(self):
        """Test that suggestions are included in no results message."""
        state: HealthBotState = {
            "messages": [],
            "topic": "xyz disease",
            "results": None,
            "summary": None,
            "quiz_question": None,
            "quiz_answer": None,
            "grade": None,
            "continue_learning": None,
            "has_results": False,
            "sources_count": 0,
            "run_id": "test-run-123",
        }

        result = handle_no_results(state)
        message_content = result["messages"][0].content
        
        assert "Suggestions" in message_content
        assert "typo" in message_content
        assert "more general" in message_content
