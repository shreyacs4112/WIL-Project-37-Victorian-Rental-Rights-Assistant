# Retrieval Findings — BM25 vs Dense Retrieval

## Purpose
This document records specific ranking-error cases identified while comparing
BM25 and dense (FAISS) retrieval on the Victorian Rental Rights knowledge
base, as part of finalising the retrieval approach used by the chatbot.

## Overall comparison (NDCG, 44 test questions, 109 chunks)

| Metric  | BM25   | Dense (FAISS) |
|---------|--------|---------------|
| NDCG@1  | 0.5455 | 0.7273        |
| NDCG@3  | 0.6974 | 0.7912        |
| NDCG@5  | 0.7356 | 0.8206        |

Dense retrieval outperforms BM25 across every cutoff, with the largest gap
at rank 1 (+18 points). This is the basis for finalising dense retrieval as
the production approach (see Decision section below).

## Case study: cross-document and within-document confusion

**Query:** "What happens if my landlord doesn't fix something within 14 days?"
**Ground truth:** KB01_S6 ("Non-Urgent Repairs Not Completed")

### BM25 result
1. KB02_S8 — "Rental Provider-Initiated Claim" (bond) — **incorrect**
2. KB01_S6 — "Non-Urgent Repairs Not Completed" — correct answer, rank 2
3. KB02_S7 — "Claiming a Bond Through the RTBA" — incorrect

**Cause:** KB01 (repairs) and KB02 (bond) both use the phrase "14 days" in
different legal contexts — repair completion deadlines vs bond-claim
deadlines. BM25 is a purely lexical/keyword-matching method, so it cannot
distinguish these two contexts and ranks by term overlap alone. This is a
genuine cross-document confusion caused by shared vocabulary across
unrelated topics.

### Dense (FAISS) result
1. KB01_S8 — "When the Renter Caused the Damage" — **incorrect, but stays
   within the correct document (KB01)**
2. KB01_S6 — "Non-Urgent Repairs Not Completed" — correct answer, rank 2
3. KB06_S10 — "If the Property Does Not Meet Minimum Standards" — incorrect

**Cause:** dense retrieval avoids the BM25 cross-document error entirely —
its top-3 stays anchored to the Repairs document. However, it still cannot
perfectly distinguish two within-document sections that are topically very
close: KB01_S6 (landlord fails to complete a repair within 14 days) and
KB01_S8 (renter is given 14 days to complete a repair they caused). Both
discuss "14 days" and repair obligations, differing only in **which party**
the obligation falls on — a distinction that is semantically subtle and not
fully captured by sentence embedding similarity.

## Interpretation

- Dense retrieval's improvement over BM25 is not just a general quality gain —
  it specifically eliminates the *cross-document* keyword-overlap failure mode
  that BM25 is structurally prone to.
- Neither method fully solves *within-document* ambiguity where two sections
  share near-identical vocabulary but differ in a legally significant detail
  (obligation direction). This is a known limitation worth flagging in the
  final report as an area for future improvement (e.g. reranking, or
  explicitly encoding "who is obligated" as a feature).

## Decision

**Dense (FAISS) retrieval is finalised as the production retrieval method**
for the chatbot, based on its consistent NDCG advantage across all cutoffs
and its avoidance of the cross-document confusion BM25 exhibits. BM25 is
retained in the codebase as a documented comparison baseline.



## Confidence threshold for unsupported questions

To detect questions the knowledge base cannot answer, we tested dense
retrieval's top-1 similarity score on 5 on-topic queries and, initially,
5 generic off-topic queries (e.g. "capital of France"), which showed a
clean separation (on-topic 0.52–0.81, off-topic 0.10–0.26) with no overlap.

However, testing against the team's more realistic out-of-scope evaluation
questions (evaluation/evaluation_set.json, Q029–Q033) revealed this
separation does not hold for topically adjacent but out-of-scope questions:

| Query | Score | Actually in scope? |
|---|---|---|
| "What are the rental laws in New South Wales?" | 0.571 | No (wrong jurisdiction) |
| "Can you recommend a real estate agent to sell my property?" | 0.474 | No |
| Lowest genuine on-topic question | 0.523 | Yes |

**Finding:** a single global similarity threshold cannot reliably separate
these cases, since jurisdiction-adjacent or property-related-but-out-of-scope
questions share enough vocabulary with genuine Victorian rental questions to
score similarly under dense embeddings. Generic off-topic tests (e.g.
unrelated topics like cooking or weather) are not representative of the
harder, realistic edge cases a chatbot will actually face.

**Revised approach:** similarity-based thresholding alone is insufficient.
Recommend combining it with a lightweight rule-based check (e.g. flagging
explicit non-Victorian jurisdiction keywords such as "NSW", "Queensland",
"interstate", or clearly non-tenancy request types such as "recommend an
agent") as a safety net layered on top of the similarity threshold, rather
than relying on similarity score alone.

This is flagged as a known limitation for the final report rather than a
solved problem — it reflects a genuine, realistic challenge in scope
detection for domain-specific RAG assistants.


## Top-K decision

Based on the team's retrieval evaluation (evaluation/retrieval_evaluation_results.md):

| Cutoff | Dense Hit@K |
|---|---|
| K=1 | 22/28 |
| K=3 | 26/28 |
| K=5 | 28/28 (100%) |

**Chosen top-K: 5** — this is the smallest K at which every in-scope evaluation
question retrieves the correct chunk. Since a missing correct chunk means the
LLM cannot generate a grounded answer regardless of prompt quality, full
coverage was prioritised over a smaller, less noisy context window.


## Investigation of failed retrieval cases (Q002, Q008, Q014, Q020, Q027)

The team's evaluation flagged 5 questions where dense retrieval did not
rank the expected chunk within the tested cutoff. Re-running each with
full top-5 results (`retrieval/diagnose_failures.py`) shows:

| ID | Expected chunk | Rank found | Top-5 hit? |
|---|---|---|---|
| Q002 | KB01_S2 | 3 | Yes |
| Q008 | KB02_S7 | 3 | Yes |
| Q014 | KB04_S4 | 5 | Yes |
| Q020 | KB05_S18 | 4 | Yes |
| Q027 | KB07_S10 | 1 | Yes (correctly ranked first) |

**Finding:** the correct chunk is present within top-5 for every case
(the cutoff actually used by the production pipeline, per the top-K=5
decision above). Q027 in particular is not a genuine failure — the
correct chunk is ranked first.

**Root cause for Q002, Q008, Q014, Q020:** these are not retrieval bugs,
but cases of legitimate content overlap across knowledge-base documents.
Several rental-rights rules are restated or cross-referenced in more than
one source document:

- Minimum-standards non-compliance appears in both KB05 (dedicated
  section) and KB06 (moving-in context)
- Bond-claim timing appears in both KB02 (dedicated section) and KB07
  (moving-out context)
- Property-showing timing (KB04_S7/S8) is semantically close to general
  entry-hours (KB04_S4), since both concern notice periods and timing

Dense retrieval is correctly surfacing topically relevant chunks; it is
not always selecting the single chunk the evaluation set designates as
canonical when multiple chunks legitimately contain relevant information.

**Ground-truth correction:** for Q008, `KB07_S13` ("Bond After Moving
Out") also directly and correctly answers the question and should be
added as an additional valid `relevant_chunk_id`, consistent with other
multi-answer questions already in the evaluation set (e.g. Q013, Q028).

**Conclusion:** since the correct evidence reaches the LLM in all cases
via the finalised top-K=5, this is not treated as a critical retrieval
bug requiring a code fix. It is documented here as a known content-overlap
characteristic of the knowledge base, with one ground-truth correction
recommended above.