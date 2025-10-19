"""Debug utilities for HealthBot.

This module provides debugging capabilities including streaming visualization
and trace logging for development and troubleshooting.
"""

import json
from typing import Any, Dict, List
from langchain_core.messages import BaseMessage, HumanMessage

from healthbot.graph import create_healthbot_graph


def stream_debug_session(topic: str, max_steps: int = 50) -> None:
    """Run a debug session with streaming visualization.
    
    This function provides a visual trace of the graph execution,
    showing each step, tool calls, and state changes.
    
    Args:
        topic: The health topic to research
        max_steps: Maximum number of steps to execute
    """
    print("🔍 DEBUG MODE - Streaming HealthBot Execution")
    print("=" * 60)
    print(f"Topic: {topic}")
    print(f"Max Steps: {max_steps}")
    print("=" * 60)
    
    # Create the graph
    app = create_healthbot_graph()
    
    # Initial state
    initial_state = {
        "messages": [HumanMessage(content=topic)],
        "run_id": f"debug-{topic.replace(' ', '-')}"
    }
    
    # Configuration with thread_id for checkpointer
    config = {"configurable": {"thread_id": f"debug-{topic.replace(' ', '-')}"}}
    
    step_count = 0
    
    try:
        # Stream the execution with proper config
        for chunk in app.stream(initial_state, config):
            step_count += 1
            
            if step_count > max_steps:
                print(f"\n⚠️  Stopped after {max_steps} steps")
                break
                
            print(f"\n--- Step {step_count} ---")
            
            # Print chunk information
            if isinstance(chunk, dict):
                for node_name, node_output in chunk.items():
                    print(f"Node: {node_name}")
                    
                    if isinstance(node_output, dict):
                        # Print state updates
                        for key, value in node_output.items():
                            if key == "messages":
                                print(f"  Messages: {len(value) if isinstance(value, list) else 'N/A'}")
                            elif key in ["topic", "summary", "quiz_question"]:
                                # Truncate long content
                                content = str(value)[:100] + "..." if len(str(value)) > 100 else str(value)
                                print(f"  {key}: {content}")
                            elif key == "grade":
                                if isinstance(value, dict):
                                    score = value.get("score", "N/A")
                                    print(f"  grade: score={score}")
                                else:
                                    print(f"  grade: {value}")
                            else:
                                print(f"  {key}: {value}")
                    else:
                        print(f"  Output: {node_output}")
            else:
                print(f"Chunk: {chunk}")
                
    except Exception as e:
        print(f"\n❌ Error during streaming: {e}")
        
    print(f"\n🏁 Debug session completed after {step_count} steps")


def simulate_complete_session(topic: str) -> None:
    """Simulate a complete HealthBot session for debugging.
    
    This function simulates user interactions to show the complete flow
    without requiring actual user input.
    
    Args:
        topic: The health topic to research
    """
    print("🎭 SIMULATION MODE - Complete Session Flow")
    print("=" * 60)
    print(f"Topic: {topic}")
    print("=" * 60)
    
    # Create the graph
    app = create_healthbot_graph()
    
    # Configuration
    config = {"configurable": {"thread_id": f"sim-{topic.replace(' ', '-')}"}}
    
    try:
        # Step 1: Start conversation
        print("\n🚀 Starting conversation...")
        result = app.invoke({"messages": []}, config)
        print("✅ Initial message sent")
        
        # Step 2: Provide topic
        print(f"\n📝 Providing topic: {topic}")
        app.update_state(config, {"messages": [HumanMessage(content=topic)]})
        result = app.invoke(None, config)
        print("✅ Topic processed")
        
        # Step 3: Provide quiz answer (simulate)
        print("\n📝 Providing quiz answer: B")
        app.update_state(config, {"messages": [HumanMessage(content="B")]})
        result = app.invoke(None, config)
        print("✅ Quiz answered")
        
        # Step 4: End session
        print("\n👋 Ending session")
        app.update_state(config, {"messages": [HumanMessage(content="no")]})
        result = app.invoke(None, config)
        print("✅ Session ended")
        
        print(f"\n🎉 Simulation completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Error during simulation: {e}")
        import traceback
        traceback.print_exc()


def trace_state_changes(state_history: List[Dict[str, Any]]) -> None:
    """Trace state changes throughout execution.
    
    Args:
        state_history: List of state snapshots
    """
    print("\n📊 STATE CHANGE TRACE")
    print("=" * 40)
    
    for i, state in enumerate(state_history):
        print(f"\n--- State {i+1} ---")
        
        # Show key fields
        key_fields = ["topic", "has_results", "sources_count", "quiz_answer", "continue_learning"]
        
        for field in key_fields:
            if field in state and state[field] is not None:
                print(f"  {field}: {state[field]}")
                
        # Show message count
        if "messages" in state:
            msg_count = len(state["messages"]) if isinstance(state["messages"], list) else 0
            print(f"  messages: {msg_count} messages")


def print_tool_calls(messages: List[BaseMessage]) -> None:
    """Print tool calls from message history.
    
    Args:
        messages: List of messages to analyze
    """
    print("\n🔧 TOOL CALLS TRACE")
    print("=" * 30)
    
    tool_call_count = 0
    
    for i, message in enumerate(messages):
        if hasattr(message, 'tool_calls') and message.tool_calls:
            tool_call_count += 1
            print(f"\nMessage {i+1}: {len(message.tool_calls)} tool calls")
            
            for j, tool_call in enumerate(message.tool_calls):
                print(f"  Tool Call {j+1}:")
                print(f"    Function: {tool_call.get('name', 'Unknown')}")
                print(f"    Args: {tool_call.get('args', {})}")
                
    if tool_call_count == 0:
        print("No tool calls found in message history")


def debug_graph_structure() -> None:
    """Print the graph structure for debugging."""
    print("\n🏗️  GRAPH STRUCTURE")
    print("=" * 30)
    
    app = create_healthbot_graph()
    
    # Get graph info
    if hasattr(app, 'get_graph'):
        graph_info = app.get_graph()
        print(f"Nodes: {list(graph_info.nodes.keys())}")
        print(f"Edges: {len(graph_info.edges)}")
        
        # Print node connections
        for node_name, node_data in graph_info.nodes.items():
            print(f"\nNode: {node_name}")
            if hasattr(node_data, 'next'):
                print(f"  Next: {node_data.next}")
            if hasattr(node_data, 'interrupt_before'):
                print(f"  Interrupt: {node_data.interrupt_before}")
    else:
        print("Graph structure not available")


def run_quick_debug_test() -> None:
    """Run a quick debug test with a simple topic."""
    print("🧪 Running Quick Debug Test")
    print("=" * 40)
    
    # Test with a simple topic
    test_topic = "diabetes"
    
    try:
        stream_debug_session(test_topic, max_steps=10)
    except Exception as e:
        print(f"Debug test failed: {e}")
        
    # Show graph structure
    debug_graph_structure()


if __name__ == "__main__":
    # Run quick debug test when executed directly
    run_quick_debug_test()
