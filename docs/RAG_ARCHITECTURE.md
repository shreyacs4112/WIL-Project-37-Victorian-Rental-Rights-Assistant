# Baseline RAG Architecture — Victorian Rental Rights Assistant

## Objective
Define the end-to-end RAG architecture for the Victorian Rental Rights
Assistant, from a user's question through to a generated, source-grounded
answer.

## Pipeline flow (as currently implemented in `rag/pipeline.py`)
User question
|
v
Rule-based scope check (is_rental_rights_question)

rejects questions naming a non-Victorian Australian jurisdiction
(NSW, QLD, SA, WA, TAS, NT, ACT)
accepts only if a rental-related keyword is present
(rent, tenancy, landlord, bond, repair, inspection, etc.)
|
| in scope \ out of scope
v v
BM25 retrieval Fixed fallback response
(retrieval/bm25_ ("I can only help with questions about
retrieval.py) Victorian rental rights...")
|
v
Top-5 knowledge-base chunks (with similarity scores)
|
v
Context construction
(join chunk text; source metadata carried separately)
|
v
LLM: meta-llama/Llama-3.1-8B-Instruct
(via Hugging Face Inference API, prompted to answer only
from provided context, with graceful failure fallback)
|
v
Generated answer + supporting source list
(source_url, topic/doc_id, similarity score per retrieved chunk)


**Note:** the LLM is called via the Hugging Face hosted Inference API
(not run fully locally), using a token (`HF_TOKEN`). This should be
reflected in the project's cost/reproducibility discussion.

## Retrieval interface

Component: `retrieval/bm25_retrieval.py` — `BM25Retriever.search(query, top_k)`
(interface pattern shared by `retrieval/dense_retrieval.py` — see Retriever
decision below)

- **Input:** a user's natural-language question (string), `top_k` (int)
- **Output:** a list of `(Chunk, score)` tuples, ranked by descending score
- Each `Chunk` carries: `chunk_id`, `doc_id`, `title`, `category`,
  `authority`, `source_url`, `section_number`, `section_title`, `text`

## Top-K decision

**Top-K = 5.** Chosen because team evaluation (`evaluation/retrieval_evaluation_results.md`)
shows Dense Hit@5 = 28/28 (100%) — the smallest K at which every in-scope
evaluation question retrieves its correct chunk. Confirmed by Shreya as the
value used in the ongoing dense retrieval integration
(`feature/dense-retrieval-integration`).

## Retriever decision

**Dense (FAISS) retrieval has been evaluated and selected as the intended
production retriever**, based on its consistent NDCG/Hit@K advantage over
BM25 in both independent evaluations (see `retrieval/RETRIEVAL_FINDINGS.md`
and `evaluation/retrieval_evaluation_results.md`).

**Current status:** as of this writing, the `test`/`prod` pipeline
(`rag/pipeline.py`) still calls `BM25Retriever`. The switch to
`DenseRetriever` is in progress on branch `feature/dense-retrieval-integration`.
This document will be updated once that integration is merged.

## Source metadata and attribution

Every retrieved chunk carries its original `source_url`, `doc_id`, and
similarity `score`. These are passed through to the pipeline's `sources`
output alongside the generated answer, so responses can be traced back to
their source section.

## Handling unsupported / out-of-scope questions

**Implemented as a rule-based check** (`is_rental_rights_question` in
`rag/pipeline.py`), run before retrieval:
- Explicitly rejects questions naming a non-Victorian Australian
  jurisdiction (e.g. "NSW", "Queensland")
- Otherwise accepts the question only if it contains a recognised
  rental-related keyword

This directly implements the recommendation from `retrieval/RETRIEVAL_FINDINGS.md`,
which found that a similarity-score threshold alone could not reliably
distinguish genuinely in-scope questions from topically adjacent
out-of-scope ones (e.g. a question naming a different jurisdiction can
still score highly on semantic similarity to Victorian content).
`retrieval/threshold_test.py` documents the specific cases that motivated
this rule-based approach over a pure similarity threshold.

**Known limitation:** the rule-based keyword list is not exhaustive and may
require expansion as real usage surfaces new phrasings or edge cases.

## Evaluation note

Two evaluation sets exist in this project:
- `retrieval/test_questions.json` (44 questions) — used during initial
  BM25 vs dense development and iteration (see `retrieval/RETRIEVAL_FINDINGS.md`)
- `evaluation/evaluation_set.json` (28 in-scope + 5 out-of-scope
  questions) — the team's shared evaluation set, used for the figures
  reported in `evaluation/retrieval_evaluation_results.md` and in the
  final report/presentation

The 28-question set is the authoritative source for reported evaluation
figures going forward.

## Status

Retrieval finalised (dense selected, top-K=5). BM25→dense integration and
rule-based scope detection are implemented; dense retrieval integration
into the live pipeline is in progress.