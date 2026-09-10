"""
eval_retrieval.py
Compares BM25 vs Dense (FAISS) retrieval on the Victorian Rental Rights
knowledge base using NDCG@1/3/5.
"""

import json
import math
import os

from load_kb import load_knowledge_base
from bm25_retrieval import BM25Retriever
from dense_retrieval import DenseRetriever


def dcg_at_k(relevances, k):
    return sum(
        rel / math.log2(idx + 2)
        for idx, rel in enumerate(relevances[:k])
    )


def ndcg_at_k(ranked_chunk_ids, relevant_ids, k):
    relevances = [1 if cid in relevant_ids else 0 for cid in ranked_chunk_ids]
    dcg = dcg_at_k(relevances, k)
    ideal_relevances = sorted(relevances, reverse=True)
    idcg = dcg_at_k(ideal_relevances, k)
    return dcg / idcg if idcg > 0 else 0.0


def evaluate(retriever, test_set, k_values=(1, 3, 5)):
    scores = {k: [] for k in k_values}
    for item in test_set:
        query = item["query"]
        relevant_ids = set(item["relevant_chunk_ids"])
        results = retriever.search(query, top_k=max(k_values))
        ranked_ids = [chunk.chunk_id for chunk, _ in results]
        for k in k_values:
            scores[k].append(ndcg_at_k(ranked_ids, relevant_ids, k))
    return {k: sum(v) / len(v) for k, v in scores.items()}


if __name__ == "__main__":
    chunks = load_knowledge_base()
    with open(os.path.join(os.path.dirname(__file__), "test_questions.json")) as f:
        test_set = json.load(f)

    print(f"Evaluating on {len(test_set)} test questions over {len(chunks)} chunks.\n")

    bm25 = BM25Retriever(chunks)
    bm25_scores = evaluate(bm25, test_set)
    print("BM25 retrieval:")
    for k, score in bm25_scores.items():
        print(f"  NDCG@{k} = {score:.4f}")

    dense = DenseRetriever(chunks)
    dense_scores = evaluate(dense, test_set)
    print("\nDense (FAISS) retrieval:")
    for k, score in dense_scores.items():
        print(f"  NDCG@{k} = {score:.4f}")