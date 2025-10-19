"""HealthBot Graph Nodes.

This module contains all the node functions that process the HealthBot graph state.
Each function represents a specific step in the conversation workflow, from initial
user interaction to quiz generation and evaluation.

The nodes are organized into three main categories:
- User Interaction Nodes: Handle communication with the user
- Processing Nodes: Perform core functionality (search, summarize)
- Quiz System Nodes: Generate and evaluate educational quizzes

All nodes follow the LangGraph pattern of receiving a HealthBotState and returning
a dictionary with state updates.
"""

import json
from typing import Any

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

from healthbot.state import HealthBotState
from healthbot.utils import extract_message_content, get_llm, get_tavily


# ============================================
# USER INTERACTION NODES
# ============================================


def ask_topic(_: HealthBotState) -> dict[str, Any]:
    """Node 1: Asks the user which health topic they want to learn about.

    This is the entry point of the interactive flow, initiating the
    conversation and setting user expectations.

    Args:
        _: Current graph state (unused in this node).

    Returns:
        Dictionary containing an AI message asking for the health topic.
    """
    message = AIMessage(
        content=(
            "Hello! I'm HealthBot, your health education assistant. 🏥\n\n"
            "I'm here to help you better understand medical conditions "
            "and health care.\n\n"
            "What health topic would you like to learn about today?\n"
            "(Examples: diabetes, hypertension, asthma, anxiety)"
        )
    )

    print("🤖 HealthBot: Asking user for topic...")

    return {"messages": [message]}


def receive_topic(state: HealthBotState) -> dict[str, Any]:
    """Node 2: Receives and processes the topic provided by the user.

    Extracts the health topic from the last human message in the
    conversation history and confirms understanding.

    Args:
        state: Current state (must have at least 1 HumanMessage).

    Returns:
        Dictionary containing the extracted topic and confirmation message.
    """
    # Get the last message (should be from user)
    last_message = state["messages"][-1]

    if isinstance(last_message, HumanMessage):
        # Extract message content safely
        topic = extract_message_content(last_message).strip()

        print(f"✅ Topic received: {topic}")

        confirmation = AIMessage(
            content=f"Got it! I'll search for reliable information about **{topic}**. "
            f"Please wait a moment... 🔍"
        )

        return {
            "topic": topic,
            "messages": [confirmation],
        }

    # Fallback (shouldn't reach here)
    print("⚠️  Warning: Message is not HumanMessage type")
    return {"topic": "general health"}


# ============================================
# PROCESSING NODES
# ============================================


def search_tavily(state: HealthBotState) -> dict[str, Any]:
    """Node 3: Searches for information about the topic using Tavily.

    Performs a targeted search for medical information using the extracted
    topic, optimizing queries for reliable health sources.

    Args:
        state: Current state (requires 'topic' field).

    Returns:
        Dictionary containing formatted search results.
    """
    topic = state["topic"]

    # Validation: if no topic, return error
    if not topic:
        print("❌ Error: No topic provided")
        return {"results": "Error: No topic provided."}

    print(f"🔍 Searching for information about: {topic}")

    # Create optimized query for medical sources
    query = f"{topic} reliable medical information"

    # Search with Tavily
    tavily = get_tavily()
    results = tavily.invoke({"query": query})  # type: ignore[misc]

    # Check if we got results
    if not results or len(results) == 0:
        print("⚠️  Warning: No results found from Tavily")
        return {
            "results": "No reliable information found for this topic. Please try a different or more specific health topic.",
            "has_results": False
        }

    # Format the results
    formatted_results = ""
    for i, result in enumerate(results, 1):
        formatted_results += f"\n--- Source {i} ---\n"
        formatted_results += f"URL: {result.get('url', 'N/A')}\n"
        formatted_results += f"Content: {result.get('content', 'N/A')}\n"

    print(f"✅ Found {len(results)} sources")

    return {
        "results": formatted_results,
        "has_results": True,
        "sources_count": len(results)
    }


def handle_no_results(state: HealthBotState) -> dict[str, Any]:
    """Node 4a: Handles cases where no search results were found.
    
    Provides a helpful message when Tavily doesn't return any results
    and suggests alternative approaches.
    
    Args:
        state: Current state (requires 'topic' field).
        
    Returns:
        Dictionary containing a helpful message for the user.
    """
    topic = state["topic"]
    
    print(f"⚠️  Handling no results for topic: {topic}")
    
    message = AIMessage(
        content=(
            f"I couldn't find reliable medical information about **{topic}**. 😔\n\n"
            "This might be because:\n"
            "• The topic name is too specific or uncommon\n"
            "• There might be a typo in the topic name\n"
            "• The topic might need to be more general\n\n"
            "**Suggestions:**\n"
            "• Try a more general term (e.g., 'diabetes' instead of 'diabetes type 1 management in elderly patients')\n"
            "• Check for spelling errors\n"
            "• Try related health topics\n\n"
            "Would you like to try a different health topic? 🤔"
        )
    )
    
    return {"messages": [message]}


def summarize(state: HealthBotState) -> dict[str, Any]:
    """Node 4: Summarizes search results in accessible language.

    Uses an LLM to create an educational summary that translates complex
    medical information into patient-friendly language.

    Args:
        state: Current state (requires 'topic' and 'results' fields).

    Returns:
        Dictionary containing the generated educational summary.
    """
    topic = state["topic"]
    results = state["results"]

    # Validation
    if not topic or not results:
        print("❌ Error: Missing data for summarization")
        return {"summary": "Error: Missing data for summarization."}

    print(f"📄 Generating summary about: {topic}")

    # Prompt for the LLM
    system_msg = SystemMessage(
        content=(
            "You are a health educator specialized in communicating "
            "medical information in clear and accessible language for patients.\n\n"
            "Create an educational summary that:\n"
            "- Uses simple language (avoid medical jargon)\n"
            "- Is accurate and based ONLY on the provided sources\n"
            "- Is between 200-250 words\n"
            "- Is informative and practical\n\n"
            "CRITICAL INSTRUCTION:\n"
            "- Use ONLY the provided results; do NOT use outside knowledge\n"
            "- Base your summary exclusively on the sources given\n"
            "- Do not add information not present in the provided sources"
        )
    )

    user_msg = HumanMessage(
        content=(
            f"Create an educational summary about **{topic}** "
            f"based on these sources:\n\n{results}"
        )
    )

    # Generate the summary
    llm = get_llm()
    response = llm.invoke([system_msg, user_msg])
    summary = extract_message_content(response)

    print(f"✅ Summary generated ({len(summary)} characters)")

    return {"summary": summary}


def present_summary(state: HealthBotState) -> dict[str, Any]:
    """Node 5: Presents the educational summary to the user.

    Formats and displays the generated summary as the main educational
    content for the user.

    Args:
        state: Current state (requires 'summary' field).

    Returns:
        Dictionary containing messages with the educational summary.
    """
    summary = state["summary"]

    # Validation
    if not summary:
        print("❌ Error: No summary available")
        return {"messages": [AIMessage(content="Error: No summary available.")]}

    # Display in console (for debug)
    print("\n" + "=" * 70)
    print("📋 FINAL SUMMARY")
    print("=" * 70)
    print()
    print(summary)
    print()
    print("=" * 70)

    print("\n📄 Presenting summary to user...")

    # Return only the summary (quiz will come later)
    return {
        "messages": [AIMessage(content=summary)],
    }


# ============================================
# QUIZ SYSTEM NODES
# ============================================


def create_quiz(state: HealthBotState) -> dict[str, Any]:
    """Node 6: Generates a quiz question based on the summary.

    Creates a multiple-choice question that tests the user's understanding
    of the educational content presented.

    Args:
        state: Current state (requires 'summary' and 'topic' fields).

    Returns:
        Dictionary containing the generated quiz question.
    """
    summary = state["summary"]
    topic = state["topic"]

    # Validation
    if not summary or not topic:
        print("❌ Error: Missing data for quiz creation")
        return {"quiz_question": "Error: Could not create quiz."}

    print(f"❓ Generating quiz question about: {topic}")

    # Prompt to generate quiz
    system_msg = SystemMessage(
        content=(
            "You are a medical educator specialized in creating "
            "educational assessment questions.\n\n"
            "Your task is to create ONE multiple choice question that:\n"
            "- Tests understanding of the presented content\n"
            "- Is clear and objective\n"
            "- Has 4 alternatives (A, B, C, D)\n"
            "- Has only ONE correct answer\n"
            "- Is moderate difficulty\n\n"
            "CRITICAL INSTRUCTIONS:\n"
            "- Use ONLY the provided summary; do NOT use outside knowledge\n"
            "- Base the question and all alternatives exclusively on the summary\n"
            "- DO NOT reveal which answer is correct in your response\n"
            "- DO NOT include phrases like 'Correct Answer:', 'The answer is', etc.\n"
            "- ONLY provide the question and the four alternatives\n\n"
            "Required format (NOTHING ELSE):\n"
            "Question: [question text]\n"
            "A) [alternative A]\n"
            "B) [alternative B]\n"
            "C) [alternative C]\n"
            "D) [alternative D]"
        )
    )

    user_msg = HumanMessage(
        content=(
            f"Create a multiple choice question about **{topic}** "
            f"based on this summary:\n\n{summary}\n\n"
            "Remember: Only output the question and four alternatives. "
            "Do NOT reveal the correct answer!"
        )
    )

    # Generate the question
    llm = get_llm()
    response = llm.invoke([system_msg, user_msg])
    quiz_question = extract_message_content(response)

    print(f"✅ Quiz question generated ({len(quiz_question)} characters)")

    return {"quiz_question": quiz_question}


def present_quiz(state: HealthBotState) -> dict[str, Any]:
    """Node 7: Presents the quiz question to the user.

    Formats and displays the generated quiz question with clear
    instructions for the user.

    Args:
        state: Current state (requires 'quiz_question' field).

    Returns:
        Dictionary containing messages with the quiz question and instructions.
    """
    quiz_question = state["quiz_question"]

    # Validation
    if not quiz_question:
        print("❌ Error: No quiz question available")
        return {
            "messages": [AIMessage(content="Error: Could not create quiz.")]
        }

    print("📝 Presenting quiz question...")

    # Return the question and instructions
    return {
        "messages": [
            AIMessage(
                content="\n---\n\n"
                "Now let's test your understanding! 📝\n\n"
                f"{quiz_question}\n\n"
                "Type the letter of the alternative you consider correct (A, B, C or D):"
            ),
        ]
    }


def receive_answer(state: HealthBotState) -> dict[str, Any]:
    """Node 8: Receives and processes the user's quiz answer.

    Extracts the user's answer from the last message and normalizes
    it for evaluation. Handles various input formats (A, a, 1, "option A", etc.).

    Args:
        state: Current state (should have user's answer in the last message).

    Returns:
        Dictionary containing the user's normalized answer.
    """
    # Get the last message (should be from user)
    last_message = state["messages"][-1]

    if isinstance(last_message, HumanMessage):
        # Extract and normalize the answer
        raw_answer = extract_message_content(last_message).strip()
        normalized_answer = _normalize_quiz_answer(raw_answer)

        print(f"✅ Answer received: {raw_answer} → normalized to: {normalized_answer}")

        return {"quiz_answer": normalized_answer}

    # Fallback
    print("⚠️  Warning: Message is not HumanMessage type")
    return {"quiz_answer": ""}


def _normalize_quiz_answer(raw_answer: str) -> str:
    """Normalize user input to standard quiz answer format.
    
    Converts various input formats to standard A, B, C, D format.
    
    Args:
        raw_answer: Raw user input
        
    Returns:
        Normalized answer (A, B, C, or D)
    """
    # Convert to uppercase and strip whitespace
    answer = raw_answer.upper().strip()
    
    # Handle various formats
    if answer in ["A", "1"]:
        return "A"
    elif answer in ["B", "2"]:
        return "B"
    elif answer in ["C", "3"]:
        return "C"
    elif answer in ["D", "4"]:
        return "D"
    elif "OPTION A" in answer or "ALTERNATIVE A" in answer:
        return "A"
    elif "OPTION B" in answer or "ALTERNATIVE B" in answer:
        return "B"
    elif "OPTION C" in answer or "ALTERNATIVE C" in answer:
        return "C"
    elif "OPTION D" in answer or "ALTERNATIVE D" in answer:
        return "D"
    else:
        # Default to the first character if it's a valid option
        if len(answer) > 0 and answer[0] in ["A", "B", "C", "D"]:
            return answer[0]
        # Fallback to empty string if no valid answer found
        return ""


def grade_answer(state: HealthBotState) -> dict[str, Any]:
    """Node 9: Evaluates the user's answer with score and feedback.

    Uses an LLM to assess the correctness of the user's answer and
    provide educational feedback with citations from the summary.

    Args:
        state: Current state (requires quiz_question, quiz_answer, summary).

    Returns:
        Dictionary containing evaluation results (score, feedback, citations).
    """
    quiz_question = state["quiz_question"]
    quiz_answer = state["quiz_answer"]
    summary = state["summary"]

    # Validation
    if not quiz_question or not quiz_answer or not summary:
        print("❌ Error: Missing data for evaluation")
        return {
            "grade": {
                "score": 0,
                "feedback": "Error: Could not evaluate the answer.",
                "citations": [],
            }
        }

    print(f"📊 Evaluating answer: {quiz_answer}")

    # Prompt for evaluation
    system_msg = SystemMessage(
        content=(
            "You are an educational evaluator specialist.\n\n"
            "Your task is to evaluate the student's answer and provide educational feedback.\n\n"
            "CRITICAL INSTRUCTION:\n"
            "- Use ONLY the educational summary provided; do NOT use outside knowledge\n"
            "- Base your evaluation exclusively on the summary content\n"
            "- Do not reference information not present in the provided summary\n\n"
            "Analyze if the answer is correct based on the educational summary provided.\n\n"
            "Return the evaluation in the FOLLOWING JSON FORMAT:\n"
            "{\n"
            '  "score": [number from 0 to 10],\n'
            '  "feedback": "[detailed explanation if correct or incorrect and why]",\n'
            '  "citations": ["excerpt 1 from summary that justifies", "excerpt 2..."]\n'
            "}\n\n"
            "EXAMPLE OUTPUT:\n"
            "{\n"
            '  "score": 8,\n'
            '  "feedback": "Correct! Your answer demonstrates understanding of the key concept mentioned in the summary.",\n'
            '  "citations": ["The summary states that...", "According to the information provided..."]\n'
            "}\n\n"
            "SCORING:\n"
            "- If answer is correct: score 8-10\n"
            "- If partially correct: score 5-7\n"
            "- If incorrect: score 0-4\n"
            "- Always cite specific excerpts from the summary that justify the evaluation"
        )
    )

    user_msg = HumanMessage(
        content=(
            f"QUESTION:\n{quiz_question}\n\n"
            f"STUDENT'S ANSWER: {quiz_answer}\n\n"
            f"EDUCATIONAL SUMMARY (basis for evaluation):\n{summary}\n\n"
            "Evaluate the answer and return in JSON format."
        )
    )

    # Generate the evaluation
    llm = get_llm()
    response = llm.invoke([system_msg, user_msg])
    evaluation_text = extract_message_content(response)

    # Try to extract JSON from response
    try:
        # Remove markdown code blocks if they exist
        if "```json" in evaluation_text:
            evaluation_text = evaluation_text.split("```json")[1].split("```")[0]
        elif "```" in evaluation_text:
            evaluation_text = evaluation_text.split("```")[1].split("```")[0]

        grade_data = json.loads(evaluation_text.strip())

        # Validate structure
        if not all(k in grade_data for k in ["score", "feedback", "citations"]):
            raise ValueError("Invalid JSON structure")  # noqa: TRY301

        print(f"✅ Evaluation completed - Score: {grade_data['score']}/10")

        return {"grade": grade_data}

    except (json.JSONDecodeError, ValueError) as e:
        print(f"⚠️  Error parsing evaluation: {e}")
        # Fallback: create basic structure
        return {
            "grade": {
                "score": 5,
                "feedback": evaluation_text,
                "citations": [],
            }
        }


def present_grade(state: HealthBotState) -> dict[str, Any]:
    """Node 10: Presents the evaluation to the user.

    Formats and displays the quiz evaluation with score, feedback,
    and relevant citations in a user-friendly format.

    Args:
        state: Current state (requires 'grade' field).

    Returns:
        Dictionary containing messages with the formatted evaluation.
    """
    grade = state["grade"]

    # Validation
    if not grade:
        print("❌ Error: No evaluation available")
        return {
            "messages": [AIMessage(content="Error: Could not evaluate your answer.")]
        }

    score = grade.get("score", 0)
    feedback = grade.get("feedback", "")
    citations = grade.get("citations", [])

    print(f"📊 Presenting evaluation - Score: {score}/10")

    # Build the evaluation message
    evaluation_message = (
        f"\n{'=' * 70}\n"
        f"📊 YOUR ANSWER EVALUATION\n"
        f"{'=' * 70}\n\n"
        f"**Score: {score}/10**\n\n"
        f"**Feedback:**\n{feedback}\n\n"
    )

    # Add citations if they exist
    if citations:
        evaluation_message += "**Relevant excerpts from the summary:**\n"
        for i, citation in enumerate(citations, 1):
            evaluation_message += f"{i}. \"{citation}\"\n"
        evaluation_message += "\n"

    evaluation_message += f"{'=' * 70}\n"

    # Closing message
    if score >= 7:
        closing = "🎉 Congratulations! You demonstrated good understanding of the topic!"
    elif score >= 5:
        closing = "👍 You're on the right track! Review some points."
    else:
        closing = "📚 Don't be discouraged! Review the summary and keep learning."

    evaluation_message += f"\n{closing}\n"

    return {
        "messages": [AIMessage(content=evaluation_message)],
    }


# ============================================
# CONTINUATION LOOP NODES
# ============================================


def ask_continue(_: HealthBotState) -> dict[str, Any]:
    """Node 11: Asks if the user wants to learn about another topic.

    After completing the quiz and evaluation, asks the user if they
    want to continue learning about another health topic or end the session.

    Args:
        _: Current state (evaluation completed).

    Returns:
        Dictionary containing message asking about continuation.
    """
    message = AIMessage(
        content=(
            "\n" + "=" * 70 + "\n\n"
            "Would you like to learn about another health topic? 🤔\n\n"
            "Type 'yes' to continue or 'no' to end the session."
        )
    )

    print("🔄 HealthBot: Asking if user wants to continue...")

    return {"messages": [message]}


def receive_continue(state: HealthBotState) -> dict[str, Any]:
    """Node 12: Receives and processes continuation response.

    Extracts the user's decision to continue or end the session and
    normalizes it to a boolean value.

    Args:
        state: Current state (should have user's response in last message).

    Returns:
        Dictionary containing the continuation decision and optional
        state reset for new topic.
    """
    # Get the last message (should be from user)
    last_message = state["messages"][-1]

    if isinstance(last_message, HumanMessage):
        # Extract and normalize the response
        response = extract_message_content(last_message).strip().lower()

        # Check if user wants to continue
        wants_to_continue = response in ["yes", "y", "sim", "s", "si", "yeah", "yep"]

        print(f"✅ Continuation response: {response} → {wants_to_continue}")

        if wants_to_continue:
            # Reset state for new topic while keeping conversation history
            print("🔄 Resetting state for new topic...")
            return {
                "continue_learning": True,
                # Reset fields for new topic, but keep messages
                "topic": None,
                "results": None,
                "summary": None,
                "quiz_question": None,
                "quiz_answer": None,
                "grade": None,
            }
        else:
            # User wants to end session
            print("👋 User ending session...")
            return {
                "continue_learning": False,
            }

    # Fallback
    print("⚠️  Warning: Message is not HumanMessage type")
    return {"continue_learning": False}


# ============================================
# ROUTING FUNCTION
# ============================================


def should_continue(state: HealthBotState) -> str:
    """Conditional edge function: Decides whether to continue or end.

    This is a routing function used in conditional edges to determine
    the next node based on the user's continuation decision.

    Args:
        state: Current state (must have 'continue_learning' field).

    Returns:
        String indicating next node: "ask_topic" to continue with new topic,
        or "end" to terminate the session.
    """
    continue_learning = state.get("continue_learning", False)

    if continue_learning:
        print("➡️  Routing to: ask_topic (new learning cycle)")
        return "ask_topic"
    else:
        print("➡️  Routing to: end (session termination)")
        return "end"
