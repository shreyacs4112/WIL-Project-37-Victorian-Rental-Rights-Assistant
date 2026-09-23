# Baseline RAG Architecture — Victorian Rental Rights Assistant

## Objective
Define the end-to-end RAG architecture for the Victorian Rental Rights
Assistant, from a user's question through to a generated, source-grounded
answer.

## Pipeline flow

```
User question
      |
      v
Dense retrieval (FAISS, sentence-transformers/all-MiniLM-L6-v2)
      |
      v
Top-5 knowledge-base chunks (with similarity scores)
      |
      v
Scope check: is top-1 score high enough to be answerable?
      |            \
      | yes          \ no
      v               v
Context construction   Safe fallback response
(join chunk text +      ("outside knowledge base scope")
 source metadata)
      |
      v
LLM (Llama 3.1 8B Instruct, prompted to answer only from
 provided context)
      |
      v
Generated answer + supporting source list
 (source_url, document title, section title per cited chunk)
```

## Retrieval interface

Component: `retrieval/dense_retrieval.py` — `DenseRetriever.search(query, top_k)`

- **Input:** a user's natural-language question (string), `top_k` (int)
- **Output:** a list of `(Chunk, score)` tuples, ranked by descending
  similarity score
- Each `Chunk` carries: `chunk_id`, `doc_id`, `title`, `category`,
  `authority`, `source_url`, `section_number`, `section_title`, `text`

This interface is consumed directly by `rag/pipeline.py`, which was
integrated first with BM25 and has since been finalised on dense retrieval
(see Decision section below).

## Top-K decision

**Top-K = 5.** Chosen because team evaluation (`evaluation/retrieval_evaluation_results.md`)
shows Dense Hit@5 = 28/28 (100%) — the smallest K at which every in-scope
evaluation question retrieves its correct chunk. Missing the correct chunk
entirely is a harder failure than passing one or two extra chunks of
context to the LLM.

## Retriever decision

**Dense (FAISS) retrieval**, not BM25. Dense outperformed BM25 across every
NDCG and Hit@K cutoff in both independent evaluations run by the team (see
`retrieval/RETRIEVAL_FINDINGS.md` and `evaluation/retrieval_evaluation_results.md`).
BM25 is retained in the codebase as a documented comparison baseline, not
used in production.

## Source metadata and attribution

Every retrieved chunk carries its original `source_url`, document `title`,
`authority` (Consumer Affairs Victoria), and `section_title`. These are
passed through context construction and surfaced alongside the generated
answer, so every chatbot response can be traced back to the specific
authoritative source section it was grounded in. This directly supports the
project's traceability and source-attribution requirement.

## Handling unsupported questions

A similarity-score threshold on the top-1 retrieved chunk is used to detect
when a question falls outside the knowledge base's scope. Testing found
that a single global threshold does not reliably separate genuinely
in-scope questions from topically adjacent but out-of-scope ones (e.g.
"rental laws in NSW" scored higher than some genuine in-scope questions —
see `retrieval/RETRIEVAL_FINDINGS.md`). This is documented as a known
limitation; a rule-based keyword safety net (flagging non-Victorian
jurisdictions or clearly non-tenancy requests) is recommended as a
follow-up refinement.

## Status

Architecture implemented and deployed to `prod`. Retrieval, context
construction, and LLM answer generation are integrated in `rag/pipeline.py`.
Reviewed by the team via ongoing PR review (BM25 integration, dense
retrieval finalisation, evaluation cross-checks).