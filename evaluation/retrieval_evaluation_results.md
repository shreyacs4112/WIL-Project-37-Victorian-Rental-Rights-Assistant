# Retrieval Evaluation Results

Evaluation set: 28 in-scope questions  
Knowledge base: 109 chunks

## Retrieval Metrics

| Retriever | NDCG@1 | NDCG@3 | NDCG@5 | Hit@1 | Hit@3 | Hit@5 |
|---|---:|---:|---:|---:|---:|---:|
| BM25 | 0.5714 | 0.7631 | 0.7631 | 0.5714 | 0.8929 | 0.8929 |
| Dense (FAISS) | 0.7857 | 0.8527 | 0.8819 | 0.7857 | 0.9286 | 1.0000 |

## Failed Retrieval Cases

### BM25

- Failed@1: Q001, Q002, Q004, Q006, Q007, Q008, Q012, Q013, Q014, Q020, Q024, Q027
- Failed@3: Q002, Q008, Q027
- Failed@5: Q002, Q008, Q027

Successful retrieval counts:
- Hit@1: 16/28
- Hit@3: 25/28
- Hit@5: 25/28

### Dense (FAISS)

- Failed@1: Q002, Q004, Q008, Q014, Q020, Q021
- Failed@3: Q014, Q020
- Failed@5: None

Successful retrieval counts:
- Hit@1: 22/28
- Hit@3: 26/28
- Hit@5: 28/28

## Observations

- Dense retrieval produced higher NDCG and Hit@K values than BM25 at all evaluated cutoffs.
- Dense retrieval achieved Hit@5 = 1.0000, meaning every in-scope evaluation question had at least one relevant chunk in the top five results.
- BM25 failed to retrieve a relevant chunk within the top five for Q002, Q008, and Q027.
- Dense retrieval still missed Q014 and Q020 within the top three, but retrieved a relevant chunk for both within the top five.
- The failed cases can be inspected further to understand where lexical BM25 retrieval or semantic dense retrieval needs refinement.
