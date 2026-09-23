"""
diagnose_failures.py
Investigates the 5 questions that dense retrieval failed to rank correctly
within top-K in the team's evaluation (Q002, Q008, Q014, Q020, Q027).
Shows full top-5 ranked results with scores, so we can see where the
correct chunk actually landed and why.
"""

from load_kb import load_knowledge_base
from dense_retrieval import DenseRetriever

chunks = load_knowledge_base()
retriever = DenseRetriever(chunks)

failed_cases = [
    {
        "id": "Q002",
        "query": "My heater has stopped working. Would this normally be considered an urgent repair?",
        "expected": ["KB01_S2"],
    },
    {
        "id": "Q008",
        "query": "How long does the rental provider have to start a bond claim after I move out?",
        "expected": ["KB02_S7"],
    },
    {
        "id": "Q014",
        "query": "Can my property manager come for an inspection at 7 pm?",
        "expected": ["KB04_S4"],
    },
    {
        "id": "Q020",
        "query": "What can I do if the property does not meet the minimum rental standards?",
        "expected": ["KB05_S18"],
    },
    {
        "id": "Q027",
        "query": "What should a renter do before moving out?",
        "expected": ["KB07_S10"],
    },
]

for case in failed_cases:
    print(f"\n{'='*70}")
    print(f"{case['id']}: {case['query']}")
    print(f"Expected: {case['expected']}")
    print(f"{'-'*70}")
    results = retriever.search(case["query"], top_k=5)
    for rank, (chunk, score) in enumerate(results, start=1):
        marker = " <-- EXPECTED" if chunk.chunk_id in case["expected"] else ""
        print(f"  {rank}. [{chunk.chunk_id}] {chunk.section_title}  (score={score:.3f}){marker}")