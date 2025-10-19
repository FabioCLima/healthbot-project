"""HealthBot Utility Functions.

This module contains helper functions and tool configurations used across
the HealthBot application. It provides reusable utilities for message handling
and tool initialization.
"""

from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.messages import BaseMessage
from langchain_openai import ChatOpenAI

from healthbot.settings import settings


def extract_message_content(message: BaseMessage) -> str:
    """Safely extracts content from a LangChain message.

    This function handles various message content types including strings,
    lists, and complex multimodal content, ensuring compatibility across
    different message formats.

    Args:
        message: LangChain message object to extract content from.

    Returns:
        Extracted content as a string, handling complex content types
        gracefully.

    Example:
        ```python
        message = HumanMessage(content="Hello, world!")
        content = extract_message_content(message)
        # Returns: "Hello, world!"
        ```

    Note:
        This function handles edge cases where message content might be
        a list of mixed types or complex dictionaries from multimodal
        content.
    """
    content = message.content  # type: ignore[misc]

    # If already a string, return directly
    if isinstance(content, str):
        return content

    # If it's a list, try to extract text from elements
    if isinstance(content, list):  # type: ignore[misc]
        text_parts: list[str] = []
        for item in content:  # type: ignore[misc]
            if isinstance(item, str):
                text_parts.append(item)  # type: ignore[misc]
            elif isinstance(item, dict):  # type: ignore[misc]
                # Try to extract text from dictionaries (e.g., multimodal content)
                if "text" in item:
                    text_parts.append(str(item["text"]))  # type: ignore[misc]
                else:
                    text_parts.append(str(item))  # type: ignore[misc]
            else:
                text_parts.append(str(item))  # type: ignore[misc]
        return " ".join(text_parts)  # type: ignore[misc]

    # Fallback: convert to string
    return str(content)  # type: ignore[misc]


def get_llm() -> ChatOpenAI:
    """Returns a configured OpenAI LLM instance.

    Uses gpt-4o-mini for cost-effectiveness and speed while maintaining
    good quality for educational content generation.

    Returns:
        Configured ChatOpenAI instance with moderate creativity settings.

    Example:
        ```python
        llm = get_llm()
        response = llm.invoke([SystemMessage(content="Hello")])
        ```

    Note:
        Temperature is set to 0.7 to balance creativity with consistency
        for educational content.
    """
    return ChatOpenAI(
        model=settings.openai_model,
        temperature=0.7,  # Moderate creativity
    )


def get_tavily() -> TavilySearchResults:
    """Returns a configured Tavily search tool.

    Configured to focus on reliable medical sources and provide
    comprehensive search results for health education.

    Returns:
        Configured TavilySearchResults instance optimized for medical
        information retrieval.

    Example:
        ```python
        tavily = get_tavily()
        results = tavily.invoke({"query": "diabetes prevention"})
        ```

    Note:
        Configuration prioritizes quality over quantity with advanced
        search depth and answer inclusion for better educational content.
    """
    return TavilySearchResults(
        max_results=3,  # Get the 3 best results
        search_depth="advanced",  # Deeper search
        include_answer=True,  # Include summarized answer
        include_raw_content=False,  # Don't need complete HTML
    )
