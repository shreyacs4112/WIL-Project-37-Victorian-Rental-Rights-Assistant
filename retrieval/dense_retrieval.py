"""
dense_retrieval.py
Dense retrieval over the rental knowledge base chunks using sentence-transformer
embeddings indexed with FAISS.
"""

import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from load_kb import load_knowledge_base

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


class DenseRetriever:
    def __init__(self, chunks, model_name: str = MODEL_NAME):
        self.chunks = chunks
        self.model = SentenceTransformer(model_name)
        texts = [c.section_title + ". " + c.text for c in chunks]
        embeddings = self.model.encode(texts, normalize_embeddings=True)
        self.embeddings = np.asarray(embeddings, dtype="float32")

        self.index = faiss.IndexFlatIP(self.embeddings.shape[1])
        self.index.add(self.embeddings)

    def search(self, query: str, top_k: int = 5):
        q_emb = self.model.encode([query], normalize_embeddings=True).astype("float32")
        scores, idxs = self.index.search(q_emb, top_k)
        results = [(self.chunks[i], float(s)) for i, s in zip(idxs[0], scores[0])]
        return results


if __name__ == "__main__":
    chunks = load_knowledge_base()
    retriever = DenseRetriever(chunks)

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