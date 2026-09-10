from typing import List, Dict


def retrieve_context(question: str) -> List[Dict]:
    """
    Mock retrieval used for integration testing.

    This will be replaced by the team's real retrieval component.
    """

    return [
        {
            "text": "Example retrieved rental-rights passage for prototype testing.",
            "source": "Mock Victorian rental-rights source",
            "topic": "KB01_REPAIRS",
            "score": 0.95
        }
    ]


def build_context(retrieved_chunks: List[Dict]) -> str:
    """
    Combine retrieved chunks into a context string for generation.
    """
    if not retrieved_chunks:
        return ""

    return "\n\n".join(
        chunk.get("text", "")
        for chunk in retrieved_chunks
    )


def generate_answer(question: str, context: str) -> str:
    """
    Temporary generation interface.

    This will later be connected to the chosen LLM.
    """
    if not context:
        return (
            "No relevant knowledge-base evidence was retrieved yet. "
            "The retrieval and generation components are still being integrated."
        )

    return (
        "A source-grounded answer will be generated here using "
        "the retrieved rental-rights context."
    )


def run_rag_pipeline(question: str) -> Dict:
    """
    Baseline end-to-end RAG pipeline.
    """

    retrieved_chunks = retrieve_context(question)

    context = build_context(retrieved_chunks)

    answer = generate_answer(
        question=question,
        context=context
    )

    sources = [
        {
            "source": chunk.get("source", "Unknown source"),
            "topic": chunk.get("topic", "Unknown topic"),
            "score": chunk.get("score")
        }
        for chunk in retrieved_chunks
    ]

    return {
        "question": question,
        "answer": answer,
        "retrieved_chunks": retrieved_chunks,
        "context": context,
        "sources": sources
    }


if __name__ == "__main__":
    result = run_rag_pipeline(
        "What can I do if my landlord does not repair a broken heater?"
    )

    print(result)