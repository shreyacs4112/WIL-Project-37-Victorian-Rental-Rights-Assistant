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
    relevances = [1 if cid in relevant_ids else 0 for cid in ranked_chunk_ids[:k]]
    dcg = dcg_at_k(relevances, k)

    ideal_relevances = [1] * min(len(relevant_ids), k)
    idcg = dcg_at_k(ideal_relevances, k)

    return dcg / idcg if idcg > 0 else 0.0


def hit_at_k(ranked_chunk_ids, relevant_ids, k):
    return int(
        any(
            chunk_id in relevant_ids
            for chunk_id in ranked_chunk_ids[:k]
        )
    )

def evaluate(retriever, test_set, k_values=(1, 3, 5)):
    scores = {k: [] for k in k_values}
    hit_scores = {k: [] for k in k_values}
    failed_questions = {k: [] for k in k_values}
    for item in test_set:
        query = item.get("question", item.get("query"))
        relevant_ids = set(item["relevant_chunk_ids"])
        results = retriever.search(query, top_k=max(k_values))
        ranked_ids = [chunk.chunk_id for chunk, _ in results]
        for k in k_values:
            scores[k].append(ndcg_at_k(ranked_ids, relevant_ids, k))
            hit_scores[k].append(hit_at_k(ranked_ids, relevant_ids, k))

        if hit_scores[k][-1] == 0:
            failed_questions[k].append(item["question_id"])
    return (
    {k: sum(v) / len(v) for k, v in scores.items()},
    {k: sum(v) / len(v) for k, v in hit_scores.items()},
    failed_questions,
)


if __name__ == "__main__":
    chunks = load_knowledge_base()
    
    evaluation_path = os.path.join(
        os.path.dirname(__file__),
        "..",
        "evaluation",
        "evaluation_set.json"
    )
    with open(evaluation_path, encoding="utf-8") as f:
      test_set = json.load(f)
       
    test_set = [
      item for item in test_set
      if item["in_scope"]
]

    print(f"Evaluating on {len(test_set)} test questions over {len(chunks)} chunks.\n")

    bm25 = BM25Retriever(chunks)
    bm25_scores, bm25_hits, bm25_failed = evaluate(bm25, test_set)
    print("BM25 retrieval:")
    for k, score in bm25_scores.items():
        print(f"  NDCG@{k} = {score:.4f}")
    for k, score in bm25_hits.items():
        print(f"  Hit@{k} = {score:.4f}")
    for k, failed in bm25_failed.items():
        print(f"  Failed@{k}: {failed}")

    dense = DenseRetriever(chunks)
    dense_scores, dense_hits, dense_failed = evaluate(dense, test_set)
    print("\nDense (FAISS) retrieval:")
    for k, score in dense_scores.items():
        print(f"  NDCG@{k} = {score:.4f}")
    for k, score in dense_hits.items():
        print(f"  Hit@{k} = {score:.4f}")
    for k, failed in dense_failed.items():
        print(f"  Failed@{k}: {failed}")
