"""
threshold_test.py
Tests dense retrieval's top-1 similarity score against both generic
off-topic queries and realistic, topically-adjacent out-of-scope queries
(from the team's evaluation set), to assess whether a similarity threshold
alone can reliably detect unanswerable questions.

See retrieval/RETRIEVAL_FINDINGS.md for the conclusion this motivated:
a pure similarity threshold is not reliable, so scope detection was
implemented as a rule-based check in rag/pipeline.py instead
(is_rental_rights_question).
"""

from load_kb import load_knowledge_base
from dense_retrieval import DenseRetriever

chunks = load_knowledge_base()
retriever = DenseRetriever(chunks)

on_topic_queries = [
    "How much can I spend on an urgent repair myself?",
    "What reasons can a rental provider use to claim my bond?",
    "How much notice does my landlord need to give before a routine inspection?",
    "Does my rental property need to have heating?",
    "How much notice do I need to give if I want to move out?",
]

generic_off_topic_queries = [
    "What's the capital of France?",
    "How do I cook a lasagna?",
    "What's the weather like today?",
    "Who won the last World Cup?",
    "How do I fix a flat tire on my car?",
]

# Realistic out-of-scope queries, matching evaluation/evaluation_set.json
# Q029-Q033 (topically adjacent but explicitly out of scope)
realistic_off_topic_queries = [
    "Which Melbourne suburb is the best place to buy an investment property?",
    "What home loan interest rate should I choose?",
    "How much is my house worth?",
    "Can you recommend a real estate agent to sell my property?",
    "What are the rental laws in New South Wales?",
]


def run_group(label, queries):
    print(f"=== {label} ===")
    for q in queries:
        results = retriever.search(q, top_k=1)
        chunk, score = results[0]
        print(f"{score:.3f}  |  {q}")
    print()


if __name__ == "__main__":
    run_group("ON-TOPIC QUERIES (expected HIGH)", on_topic_queries)
    run_group("GENERIC OFF-TOPIC QUERIES (expected LOW)", generic_off_topic_queries)
    run_group(
        "REALISTIC OUT-OF-SCOPE QUERIES (evaluation_set.json Q029-Q033) "
        "— expected to overlap with on-topic scores, motivating the "
        "rule-based scope check instead of a pure threshold",
        realistic_off_topic_queries,
    )