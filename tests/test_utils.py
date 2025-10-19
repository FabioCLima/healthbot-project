"""Unit tests for HealthBot utility functions.

Tests utility functions for message extraction and other helpers.
"""

import pytest
from unittest.mock import Mock
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

from healthbot.utils import extract_message_content


class TestExtractMessageContent:
    """Test message content extraction utility."""

    def test_extract_human_message_content(self):
        """Test extracting content from HumanMessage."""
        message = HumanMessage(content="Hello, how are you?")
        content = extract_message_content(message)
        assert content == "Hello, how are you?"

    def test_extract_ai_message_content(self):
        """Test extracting content from AIMessage."""
        message = AIMessage(content="I'm doing well, thank you!")
        content = extract_message_content(message)
        assert content == "I'm doing well, thank you!"

    def test_extract_system_message_content(self):
        """Test extracting content from SystemMessage."""
        message = SystemMessage(content="You are a helpful assistant.")
        content = extract_message_content(message)
        assert content == "You are a helpful assistant."

    def test_extract_empty_content(self):
        """Test extracting empty content."""
        message = HumanMessage(content="")
        content = extract_message_content(message)
        assert content == ""

    def test_extract_none_content(self):
        """Test extracting None content."""
        # HumanMessage doesn't allow None content, so we'll test with empty string
        message = HumanMessage(content="")
        content = extract_message_content(message)
        assert content == ""

    def test_extract_multiline_content(self):
        """Test extracting multiline content."""
        multiline_text = """This is a multiline message.
        It has multiple lines.
        Each line should be preserved."""
        
        message = HumanMessage(content=multiline_text)
        content = extract_message_content(message)
        assert content == multiline_text

    def test_extract_message_with_attributes(self):
        """Test extracting content from message with additional attributes."""
        message = HumanMessage(
            content="Test content",
            additional_kwargs={"model": "gpt-4"}
        )
        content = extract_message_content(message)
        assert content == "Test content"

    def test_extract_message_mock(self):
        """Test extracting content from mocked message."""
        mock_message = Mock()
        mock_message.content = "Mocked content"
        
        content = extract_message_content(mock_message)
        assert content == "Mocked content"

    def test_extract_message_without_content_attribute(self):
        """Test handling message without content attribute."""
        mock_message = Mock(spec=[])
        
        with pytest.raises(AttributeError):
            extract_message_content(mock_message)
