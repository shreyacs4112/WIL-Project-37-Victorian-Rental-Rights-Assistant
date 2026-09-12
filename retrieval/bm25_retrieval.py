"""
bm25_retrieval.py
BM25 sparse retrieval over the rental knowledge base chunks.
"""

import re
from rank_bm25 import BM25Okapi
from load_kb import load_knowledge_base


def tokenize(text: str):
    return re.findall(r"[a-z0-9]+", text.lower())


class BM25Retriever:
    def __init__(self, chunks):
        self.chunks = chunks
        self.corpus_tokens = [tokenize(c.text + " " + c.section_title) for c in chunks]
        self.bm25 = BM25Okapi(self.corpus_tokens)

    def search(self, query: str, top_k: int = 5):
        scores = self.bm25.get_scores(tokenize(query))
        ranked = sorted(zip(self.chunks, scores), key=lambda x: x[1], reverse=True)
        return ranked[:top_k]


if __name__ == "__main__":
    chunks = load_knowledge_base()
    retriever = BM25Retriever(chunks)

    test_queries = [
        "How much can I spend on an urgent repair myself?",
        "Who pays for repairs if I damaged the property?",
        "What happens if my landlord doesn't fix something within 14 days?",
    ]

    for q in test_queries:
        print(f"\nQuery: {q}")
        results = retriever.search(q, top_k=3)
        for rank, (chunk, score) in enumerate(results, start=1):
            print(f"  {rank}. [{chunk.chunk_id}] {chunk.section_title}  (score={score:.3f})")