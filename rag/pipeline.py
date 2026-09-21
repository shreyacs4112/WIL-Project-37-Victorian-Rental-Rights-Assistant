import os
from typing import List, Dict
from huggingface_hub import InferenceClient

from retrieval.bm25_retrieval import BM25Retriever
from retrieval.load_kb import load_knowledge_base

_chunks = load_knowledge_base()
_retriever = BM25Retriever(_chunks)
_hf_client = InferenceClient(
    model="Qwen/Qwen3-4B-Instruct-2507",
    token=os.getenv("HF_TOKEN"),
)

def retrieve_context(question: str, top_k: int = 5) -> List[Dict]:
    """
    Retrieve the most relevant rental-rights knowledge-base chunks
    using the BM25 retriever.
    """
    results = _retriever.search(question, top_k=top_k)

    return [
        {
            "text": chunk.text,
            "source": chunk.source_url,
            "topic": chunk.doc_id,
            "section": chunk.section_title,
            "chunk_id": chunk.chunk_id,
            "score": float(score),
        }
        for chunk, score in results
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
    Generate a grounded answer using the retrieved rental-rights context.
    """
    if not context:
        return (
            "I could not find enough relevant information in the Victorian "
            "rental-rights knowledge base to answer this question."
        )

    system_prompt = """
You are a Victorian Rental Rights Assistant.

Answer the user's question using ONLY the information contained in the
retrieved context provided to you.

Rules:
- Do not use outside knowledge.
- Do not invent legal requirements, timeframes, amounts, rights, or procedures.
- If the retrieved context does not contain enough information to answer the
  question, clearly say that there is not enough information in the available
  evidence.
- Keep the answer clear and concise.
- Do not claim to provide personalised legal advice.
- Do not invent sources or citations. Sources are displayed separately by
  the application.
"""

    user_prompt = f"""
Retrieved context:

{context}

User question:
{question}

Provide a helpful answer based only on the retrieved context.
"""

    response = _hf_client.chat_completion(
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        max_tokens=400,
        temperature=0.2,
    )

    return response.choices[0].message.content.strip()


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