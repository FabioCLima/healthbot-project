"""HealthBot Graph Construction.

This module is responsible for creating and configuring the LangGraph
workflow that orchestrates the HealthBot conversation flow.

The graph manages a stateful conversation with human-in-the-loop
interactions, allowing users to learn about health topics through
an interactive educational experience.
"""

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, StateGraph
from langgraph.graph.state import CompiledStateGraph

from healthbot.nodes import (
    ask_continue,
    ask_topic,
    create_quiz,
    grade_answer,
    present_grade,
    present_quiz,
    present_summary,
    receive_answer,
    receive_continue,
    receive_topic,
    search_tavily,
    should_continue,
    summarize,
)
from healthbot.state import HealthBotState


def create_healthbot_graph() -> CompiledStateGraph:
    """Creates and compiles the HealthBot conversation graph.

    Builds a stateful graph that manages the complete educational flow
    with continuation loop:
    
    1. Ask for health topic
    2. Search for information with Tavily
    3. Generate educational summary
    4. Create and present quiz
    5. Evaluate user's answer
    6. Present results
    7. Ask if user wants to continue
    8. Either restart for new topic or end session

    The graph includes strategic interrupts to wait for user input at:
    - Topic selection (after ask_topic)
    - Quiz answer (after present_quiz)
    - Continuation decision (after ask_continue)

    Returns:
        Compiled StateGraph with checkpointer for state persistence.

    Example:
        ```python
        app = create_healthbot_graph()
        config = {"configurable": {"thread_id": "session-123"}}

        # Start conversation
        result = app.invoke({"messages": []}, config)

        # Continue with user input
        app.update_state(config, {"messages": [HumanMessage(content="diabetes")]})
        result = app.invoke(None, config)

        # Answer quiz
        app.update_state(config, {"messages": [HumanMessage(content="B")]})
        result = app.invoke(None, config)

        # Continue or end
        app.update_state(config, {"messages": [HumanMessage(content="yes")]})
        result = app.invoke(None, config)  # Loops back to ask_topic
        ```

    Note:
        The graph uses MemorySaver for state persistence, enabling
        conversation continuation across interrupts.
    """
    # ============================================
    # CREATE THE GRAPH
    # ============================================
    workflow = StateGraph(HealthBotState)

    # ============================================
    # ADD ALL NODES
    # ============================================

    # Main flow nodes
    workflow.add_node("ask_topic", ask_topic)  # type: ignore[misc]
    workflow.add_node("receive_topic", receive_topic)  # type: ignore[misc]
    workflow.add_node("search_tavily", search_tavily)  # type: ignore[misc]
    workflow.add_node("summarize", summarize)  # type: ignore[misc]
    workflow.add_node("present_summary", present_summary)  # type: ignore[misc]

    # Quiz system nodes
    workflow.add_node("create_quiz", create_quiz)  # type: ignore[misc]
    workflow.add_node("present_quiz", present_quiz)  # type: ignore[misc]
    workflow.add_node("receive_answer", receive_answer)  # type: ignore[misc]
    workflow.add_node("grade_answer", grade_answer)  # type: ignore[misc]
    workflow.add_node("present_grade", present_grade)  # type: ignore[misc]

    # Continuation loop nodes
    workflow.add_node("ask_continue", ask_continue)  # type: ignore[misc]
    workflow.add_node("receive_continue", receive_continue)  # type: ignore[misc]

    # ============================================
    # DEFINE EDGES (FLOW CONNECTIONS)
    # ============================================

    # Entry point
    workflow.set_entry_point("ask_topic")

    # Main learning flow
    workflow.add_edge("ask_topic", "receive_topic")
    workflow.add_edge("receive_topic", "search_tavily")
    workflow.add_edge("search_tavily", "summarize")
    workflow.add_edge("summarize", "present_summary")

    # Quiz flow
    workflow.add_edge("present_summary", "create_quiz")
    workflow.add_edge("create_quiz", "present_quiz")
    workflow.add_edge("present_quiz", "receive_answer")
    workflow.add_edge("receive_answer", "grade_answer")
    workflow.add_edge("grade_answer", "present_grade")

    # Continuation loop
    workflow.add_edge("present_grade", "ask_continue")
    workflow.add_edge("ask_continue", "receive_continue")

    # Conditional edge: Continue learning or end session
    workflow.add_conditional_edges(
        "receive_continue",
        should_continue,
        {
            "ask_topic": "ask_topic",  # Loop back to start new topic
            "end": END,  # End the session
        },
    )

    # ============================================
    # COMPILE WITH CHECKPOINTER AND INTERRUPTS
    # ============================================
    checkpointer = MemorySaver()

    return workflow.compile(  # type: ignore[misc]
        checkpointer=checkpointer,
        interrupt_before=[
            "receive_topic",  # Pause to receive user's topic
            "receive_answer",  # Pause to receive quiz answer
            "receive_continue",  # Pause to receive continuation decision
        ],
    )
