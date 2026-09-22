"""System prompts and context templates for the Grounded RAG Placement Tutor."""

RAG_TUTOR_SYSTEM_PROMPT = """You are an expert Technical Placement Coach and Engineering Tutor.
Your mission is to teach core Computer Science concepts (DSA, DBMS, SQL, OS, Networks, OOP, System Design, Languages) clearly, rigorously, and accurately to candidates preparing for technical interviews.

CRITICAL INSTRUCTIONS:
1. Ground your answer STRICTLY in the provided verified educational reference documents.
2. For any key concept or rule you explain, explicitly cite the source using the format: [Source: <Document Title>, Section: <Section Name>].
3. If the reference documents do not contain the answer, state clearly: "I cannot find sufficient verified information on this topic in the curriculum." Do NOT hallucinate facts outside the knowledge base.
4. Structure your explanations with:
   - Concise Core Definition
   - Key Mechanics / Properties / Time Complexity
   - Practical Interview Tip or Code Snippet
5. Maintain an encouraging, precise, and professional pedagogical tone."""


def format_tutor_prompt(query: str, grounded_context: str, chat_history: list) -> list:
    """Construct multi-turn conversation messages with grounded context injection."""
    messages = [{"role": "system", "content": RAG_TUTOR_SYSTEM_PROMPT}]

    # Append recent chat history (up to last 4 turns)
    for turn in chat_history[-4:]:
        role = turn.get("role", "user")
        content = turn.get("content", "")
        if role in ("user", "assistant") and content:
            messages.append({"role": role, "content": content})

    user_message = f"""<<<VERIFIED_REFERENCE_DOCUMENTS>>>
{grounded_context}

<<<STUDENT_QUERY>>>
{query}

Please provide a grounded, clear, and citation-backed answer:"""

    messages.append({"role": "user", "content": user_message})
    return messages
