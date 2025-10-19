"""HealthBot Main Application.

This is the main entry point for the HealthBot application. It provides
an interactive console interface for users to learn about health topics
through an AI-powered educational system.

The application uses LangGraph to orchestrate a multi-step conversation
flow that includes information retrieval, summarization, quiz generation,
and evaluation.

Usage:
    python -m healthbot.main
    
    or
    
    python src/healthbot/main.py
"""

from typing import cast

from langchain_core.messages import BaseMessage, HumanMessage
from langchain_core.runnables import RunnableConfig

from healthbot.graph import create_healthbot_graph
from healthbot.settings import settings


def print_banner() -> None:
    """Displays the HealthBot welcome banner."""
    print("\n" + "=" * 70)
    print("  🏥 HEALTHBOT - AI-Powered Patient Education System")
    print("=" * 70)
    print("  Version: 1.0.0 (MVP4 Complete)")
    print("  Powered by: LangGraph + LangChain + OpenAI + Tavily")
    print("=" * 70 + "\n")


def print_separator(title: str = "") -> None:
    """Prints a visual separator with optional title.
    
    Args:
        title: Optional title to display in the separator.
    """
    print("\n" + "=" * 70)
    if title:
        print(f"  {title}")
        print("=" * 70)
    print()


def validate_configuration() -> bool:
    """Validates that all required API keys are configured.
    
    Returns:
        True if configuration is valid, False otherwise.
    """
    print("🔧 Validating configuration...")
    
    is_valid, errors = settings.validate_required_keys()
    
    if not is_valid:
        print("\n❌ Configuration Error!\n")
        print("Missing required API keys:")
        for error in errors:
            print(f"  - {error}")
        print("\n💡 Please configure your .env file with the required keys.")
        print("   See .env.example for reference.\n")
        return False
    
    print("✅ Configuration valid!\n")
    return True


def get_user_input(prompt: str) -> str:
    """Gets input from the user with a formatted prompt.
    
    Args:
        prompt: The prompt message to display to the user.
        
    Returns:
        User's input as a string.
    """
    print(f"👤 {prompt}")
    print("   > ", end="", flush=True)
    return input().strip()


def display_messages(messages: list[BaseMessage]) -> None:
    """Displays messages from the conversation in a formatted way.
    
    Args:
        messages: List of messages to display.
    """
    if not messages:
        return
    
    # Display only the last AI message (avoid repetition)
    last_message = messages[-1]
    content = getattr(last_message, 'content', '')
    
    # Skip if it's a system message or empty
    if not content or str(content).startswith("Got it!"):
        return
    
    print(f"\n🤖 HealthBot:\n")
    print(content)
    print()


def run_interactive_session() -> None:
    """Runs an interactive HealthBot session.
    
    This is the main application loop that:
    1. Creates the conversation graph
    2. Starts the conversation
    3. Handles user interactions at interrupt points
    4. Continues the flow until completion or exit
    """
    print_separator("STARTING INTERACTIVE SESSION")
    
    # Create the compiled graph
    print("🔨 Building HealthBot graph...")
    app = create_healthbot_graph()
    print("✅ HealthBot ready!\n")
    
    # Create a unique thread ID for this session
    import uuid
    thread_id = f"session-{uuid.uuid4().hex[:8]}"
    config: RunnableConfig = {"configurable": {"thread_id": thread_id}}
    
    print(f"📝 Session ID: {thread_id}\n")
    print_separator()
    
    # Start the conversation with empty state
    print("🚀 Starting conversation...\n")
    result = app.invoke({"messages": []}, config)
    
    # Display initial message
    if result.get("messages"):
        display_messages(cast(list[BaseMessage], result["messages"]))
    
    # Main interaction loop
    while True:
        # Check if we're at an interrupt point
        state_snapshot = app.get_state(config)
        
        # If no more nodes to execute, we're done
        if not state_snapshot.next:
            print_separator("SESSION COMPLETED")
            print("👋 Thank you for using HealthBot!")
            print("   We hope you learned something new today!\n")
            break
        
        next_node = state_snapshot.next[0]
        
        # Determine what kind of input we need based on the next node
        if next_node == "receive_topic":
            # User needs to provide a health topic
            user_input = get_user_input(
                "Enter a health topic you'd like to learn about:"
            )
            
            # Check for exit command
            if user_input.lower() in ["exit", "quit", "bye"]:
                print("\n👋 Goodbye! Take care!\n")
                break
            
            # Update state with user's topic
            # Don't use as_node - let LangGraph execute receive_topic naturally
            app.update_state(
                config,
                {"messages": [HumanMessage(content=user_input)]}
            )
            
            print(f"\n🔄 Processing '{user_input}'...\n")
            
        elif next_node == "receive_answer":
            # User needs to answer the quiz question
            user_input = get_user_input(
                "Enter your answer (A, B, C, or D):"
            )
            
            # Validate quiz answer format
            if user_input.upper() not in ["A", "B", "C", "D"]:
                print("\n⚠️  Please enter a valid option: A, B, C, or D\n")
                continue
            
            # Update state with user's answer
            # Don't use as_node - let LangGraph execute receive_answer naturally
            app.update_state(
                config,
                {"messages": [HumanMessage(content=user_input)]}
            )
            
            print(f"\n📊 Evaluating your answer...\n")
            
        elif next_node == "receive_continue":
            # User needs to decide if they want to continue
            user_input = get_user_input(
                "Would you like to learn about another topic? (yes/no):"
            )
            
            # Update state with continuation decision
            # Don't use as_node - let LangGraph execute receive_continue naturally
            app.update_state(
                config,
                {"messages": [HumanMessage(content=user_input)]}
            )
            
            if user_input.lower() not in ["yes", "y", "sim", "s"]:
                print("\n🔄 Ending session...\n")
            else:
                print("\n🔄 Starting new topic...\n")
        
        # Continue execution from current point
        result = app.invoke(None, config)
        
        # Display any new messages
        if result.get("messages"):
            display_messages(cast(list[BaseMessage], result["messages"]))


def main() -> None:
    """Main entry point for the HealthBot application.
    
    Validates configuration, displays welcome banner, and starts
    the interactive session.
    """
    print_banner()
    
    # Validate configuration before starting
    if not validate_configuration():
        return
    
    try:
        # Run the interactive session
        run_interactive_session()
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Session interrupted by user.")
        print("👋 Goodbye!\n")
        
    except Exception as e:
        print(f"\n\n❌ An error occurred: {e}")
        print("Please check your configuration and try again.\n")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()