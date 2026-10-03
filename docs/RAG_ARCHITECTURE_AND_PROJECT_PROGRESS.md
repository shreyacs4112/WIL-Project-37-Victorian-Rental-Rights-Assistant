# Victorian Rental Rights Assistant — RAG Architecture, Evaluation and Project Progress

**Group 37 | COSC2669/COSC2816 WIL Project**
**Status:** Final sprint, ahead of the final presentation

---

## 1. Project Overview

The Victorian Rental Rights Assistant is a Retrieval-Augmented Generation system that helps Victorian renters get accurate, source-grounded answers about common rental rights and responsibilities, without manually searching through tenancy legislation and guidance material.

- **Primary stakeholders:** Victorian residential renters
- **Jurisdiction:** Residential renting in Victoria, Australia only
- **Primary authority:** Consumer Affairs Victoria
- **Out of scope:** rental law outside Victoria, commercial leases, personalised legal advice, non-rental property law, automated legal decision-making, and questions the knowledge base does not support

---

## 2. Knowledge Base

The knowledge base consists of seven structured documents, KB01 to KB07, each sourced from Consumer Affairs Victoria.

| ID | Topic |
|---|---|
| KB01 | Repairs and Maintenance |
| KB02 | Bond Claims and Refunds |
| KB03 | Rent Increases |
| KB04 | Property Entry and Inspections |
| KB05 | Minimum Rental Standards |
| KB06 | Moving In and Condition Reports |
| KB07 | Ending Rental Agreements and Moving Out |

Sources were chosen for being authoritative, specific to Victoria, and relevant to common renter rights. Source URLs and access dates are kept for every document so answers stay traceable.

### Chunking approach

Each document is split with section-aware chunking. Every numbered semantic section becomes one retrieval chunk, such as KB01_S1 and KB01_S2. This keeps legally coherent units together instead of cutting text at arbitrary character or token boundaries.

- 109 retrieval chunks are produced across KB01 to KB07
- Average section length is about 61 words, ranging from about 9 to 133 words
- Supporting keyword list sections are excluded from retrieval
- Preprocessing only cleans formatting and never paraphrases legal content
- The output is `data/processed/kb_chunks.json`, checked by an automated test suite covering required metadata, duplicate or missing IDs, empty sections, and structural integrity
- The retrieval loader reads directly from this file, so a single chunking implementation is shared across the project

---

## 3. RAG Pipeline Architecture

```
User question
      |
      v
Rule-based scope check
      |                    \
      | in scope             \ out of scope
      v                       v
Retrieval, top 5          Message explaining the assistant
Dense on TEST, pending    only covers Victorian rental rights
verification, BM25 on PROD
      |
      v
Context construction from retrieved chunk text
      |
      v
LLM generation with a grounded prompt
      |
      v
Answer shown in the Streamlit chatbot
together with retrieved evidence and sources
```

### Retrieval

- **Decision:** dense retrieval with FAISS was selected over BM25, because it scored higher at every NDCG and Hit@K cutoff in both evaluations. Top-K is fixed at 5.
- **Why top 5:** dense retrieval reaches Hit@5 of 28 out of 28, so 5 is the smallest K at which every ground-truth question retrieves its correct chunk. Top 5 is also the set of chunks that actually reaches the LLM.
- **Current implementation status:** dense retrieval has been merged into the TEST environment. All 16 automated tests passed, and initial live chatbot smoke testing covered repairs, bond refunds, rent increases, property entry, an out-of-jurisdiction question and an unrelated question. Formal TEST deployment verification is still pending completion. The production environment has not yet been promoted and still runs BM25. Two ranking issues were found during the initial smoke testing and are noted below. Until TEST verification is complete and TEST is promoted, this document treats dense retrieval as the current TEST pipeline and BM25 as the current production pipeline.

### Scope detection

A rule-based check screens each question before retrieval.

- It rejects questions that name another Australian state or territory
- It accepts questions containing rental-related terms such as rent, bond, repair, lease, eviction and VCAT

This approach was adopted because testing showed that a similarity-score threshold cannot reliably separate genuine in-scope questions from out-of-scope ones that share vocabulary. See Section 5.

### Generation

- **Model:** Llama 3.1 8B Instruct, accessed through the Hugging Face Inference API
- **Why Hugging Face:** it avoids a paid API subscription and supports a reproducible setup, in line with the project brief. Hosted inference still has provider-dependent rate limits and could incur costs beyond free usage, so it is not guaranteed to be cost-free. An earlier choice of Qwen2.5-3B-Instruct was replaced because that model became unavailable.
- **Grounded prompting:** the prompt instructs the model to answer only from the retrieved context, never to invent legal requirements, timeframes or amounts, and to say clearly when the context is insufficient
- **Graceful failure handling:** if the LLM provider is unavailable, the pipeline returns a safe fallback message pointing the user to the retrieved evidence instead of crashing

### Source attribution

Every retrieved chunk carries its source URL, document title and category, issuing authority, and section title. The chatbot shows these in a retrieved evidence and sources panel, together with the relevance score, so each answer can be traced to its original source.

### Interface

The chatbot is built with Streamlit. Users type a question, read the generated answer, and expand a panel to inspect the evidence behind it.

---

## 4. Retrieval Evaluation Results

Two evaluation runs were completed, and they use different question sets.

- **Ground-truth evaluation, 28 in-scope questions.** This is the reference set for final results, run against the 109-chunk knowledge base.
- **Earlier comparison, 44 test questions.** This was an earlier, broader run used to choose between BM25 and dense retrieval.

### Ground-truth evaluation

| Retriever | NDCG@1 | NDCG@3 | NDCG@5 | Hit@1 | Hit@3 | Hit@5 |
|---|---:|---:|---:|---:|---:|---:|
| BM25 | 0.5714 | 0.7631 | 0.7631 | 16 of 28 | 25 of 28 | 25 of 28 |
| Dense | 0.7857 | 0.8527 | 0.8819 | 22 of 28 | 26 of 28 | 28 of 28 |

### Earlier comparison

| Metric | BM25 | Dense |
|---|---:|---:|
| NDCG@1 | 0.5455 | 0.7273 |
| NDCG@3 | 0.6974 | 0.7912 |
| NDCG@5 | 0.7356 | 0.8206 |

Dense retrieval outperformed BM25 at every cutoff in both runs, with the largest gap at rank 1.

---

## 5. Failure Analysis and Limitations

### The 14 days confusion

The question "What happens if my landlord doesn't fix something within 14 days?" should retrieve the section on non-urgent repairs that are not completed. BM25 ranked a bond claim section above it, because both sections use the phrase 14 days in unrelated legal contexts. BM25 matches on keyword overlap and cannot tell the two contexts apart.

Dense retrieval avoided this cross-document error, since its top results stayed within the repairs document. It still could not perfectly separate two adjacent sections inside that document, because they differ mainly in which party holds the obligation, and sentence embeddings do not fully capture that distinction.

### Investigation of the five failed retrieval cases

A follow-up investigation looked at five flagged retrieval cases. One of them, Q027, was in fact ranked first. In the other four the expected chunk was at ranks 3, 3, 5 and 4. In all five the correct chunk was within the top 5, which is the set that reaches the LLM. The four lower-ranked cases are ranking imperfections rather than retrieval failures, caused by genuine content overlap between knowledge base documents. Minimum standards content appears in both KB05 and KB06, and bond timing appears in both KB02 and KB07.

One question was also found to have a second legitimately correct chunk, KB07_S13, which was not marked as valid in the ground truth. The recommended action is to add it to the ground truth, and no retrieval code change is needed.

### Ranking issues found during TEST smoke testing

Live testing of the merged dense retrieval pipeline on TEST surfaced two further ranking issues. A broken-heater query ranked chunk KB01_S8 first, ahead of the more relevant repair chunk. A bond-refund query ranked the most relevant chunk, KB07_S13, fourth rather than first. Both are being included in the final end-to-end evaluation so they can be assessed alongside the other retrieval findings before production promotion.

### Live misranking observed in testing

During chatbot testing, a broken heater question returned a rent increase chunk at rank one under BM25 instead of the repair and heating chunks. This is the same keyword confusion pattern described above and is one of the reasons for moving to dense retrieval.

### Scope detection limits

A similarity-score threshold could not reliably separate jurisdiction-adjacent or property-adjacent questions from genuine in-scope ones. A question about NSW rental laws scored 0.571, similar to real in-scope questions. This is why the rule-based check is used instead of a score threshold alone.

### Answer faithfulness and source attribution

Representative questions were tested across all seven knowledge base topics, plus one out-of-scope question. The generated answers were grounded in the retrieved context. The main issue found was that the sources panel sometimes displayed extra sources from the top 5 chunks that were not directly needed for the answer. This is a display precision limitation rather than a factual error, and it is a candidate for refinement, for example by showing only the sources the answer actually relies on.

---

## 6. Deployment Workflow

```
Feature branch
      |
      v  pull request
     test   deployed to the Streamlit Cloud test environment
      |
      v  pull request
     prod   deployed to the Streamlit Cloud production environment
      |
      v  pull request after final review
     main
```

- Each team member works on a dedicated feature branch per task
- Pull requests are raised into test and reviewed by an assigned reviewer matched to the workstream
- Once features are integration-tested on test, a pull request promotes them to prod
- The test and production environments are separate Streamlit Cloud deployments, and production is reserved for the final submission
- Trello columns run from Backlog through To Do, In Progress and Testing/Review to Done, mirroring the branch flow

---

## 7. Project Progress Summary

### Completed

- Knowledge base sourced, structured, chunked and validated, giving 109 chunks across seven topics
- BM25 and dense retrieval built, evaluated and compared
- Top-K of 5 and the dense retrieval approach agreed based on evaluation
- Chatbot interface built with source and evidence display
- LLM answer generation integrated with grounded prompting, a rule-based scope check and a safe fallback
- Separate test and production environments deployed and smoke-tested
- Ground-truth evaluation dataset built across all knowledge base topics, including paraphrased and out-of-scope questions
- Retrieval performance evaluation completed and merged
- Investigation of failed retrieval cases completed
- Answer faithfulness and source attribution evaluation completed and in review
- Documentation corrected to match the implemented system after review feedback

### In progress or remaining

- Completion of TEST deployment verification
- Resolution of the two ranking issues found during initial TEST smoke testing, as part of the final end-to-end evaluation
- Promotion of the verified dense pipeline from TEST to production
- Final end-to-end chatbot evaluation, run on the current TEST pipeline, including the two ranking issues noted above
- Fixes for any critical issues found in that evaluation, split by whether they relate to retrieval, integration or generation
- A Streamlit deployment issue on TEST has already been identified and fixed, and the app rebooted and verified
- Ground-truth update to add the second valid chunk for the affected question
- Final production deployment and smoke tests
- Final documentation update with the end-to-end evaluation results, and preparation of the demo
