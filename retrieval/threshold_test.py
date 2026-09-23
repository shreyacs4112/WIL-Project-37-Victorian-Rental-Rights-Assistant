"""
threshold_test.py
Runs a mix of on-topic (rental-rights) and off-topic (unrelated) queries
through dense retrieval to find a sensible confidence threshold for
detecting "unanswerable" questions.
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

off_topic_queries = [
    "Which Melbourne suburb is the best place to buy an investment property?",
    "What home loan interest rate should I choose?",
    "How much is my house worth?",
    "Can you recommend a real estate agent to sell my property?",
    "What are the rental laws in New South Wales?",
]

print("=== ON-TOPIC QUERIES (top score expected HIGH) ===")
for q in on_topic_queries:
    results = retriever.search(q, top_k=1)
    chunk, score = results[0]
    print(f"{score:.3f}  |  {q}")

print("\n=== OFF-TOPIC QUERIES (top score expected LOW) ===")
for q in off_topic_queries:
    results = retriever.search(q, top_k=1)
    chunk, score = results[0]
    print(f"{score:.3f}  |  {q}")