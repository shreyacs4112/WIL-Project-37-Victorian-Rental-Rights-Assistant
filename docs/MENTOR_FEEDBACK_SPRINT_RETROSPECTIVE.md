# Mentor Feedback and Sprint Retrospective

**Group 37 | COSC2669/COSC2816 WIL Project — Victorian Rental Rights Assistant**

---

## Meeting 1 — 8 September 2026

**Context:** The team presented progress to date, covering the project aim, user stories, and the initial retrieval evaluation that reproduced the Walert approach across BM25, dense and intent-based retrieval on known and inferred topics.

**Mentor feedback:** Asked how well the system's predictions or analysis were performing, meaning how retrieval and answer quality were being measured and not just that retrieval existed.

**Team response and decisions:**
- Adopted NDCG at ranks 1, 3 and 5 as the core retrieval evaluation metric
- Committed to building a proper ground-truth evaluation dataset covering paraphrased and out-of-scope questions, so retrieval and answer quality could be measured systematically

---

## Meeting 2 — 22 September 2026

**Context:** The team had since built the full pipeline, including the knowledge base, BM25 and dense retrieval, the chatbot interface, LLM answer generation, source and evidence display, and separate test and production deployments.

**Mentor feedback:** Requested a full working demo of the system rather than a written or verbal progress update, so she could see the chatbot running and answering questions.

**Team response:** Prioritised getting the end-to-end pipeline deployed, stable and demoable in the production environment, and planned a final end-to-end evaluation before fixing remaining issues. The deployed demo at this point uses BM25 retrieval, and the final dense retrieval pipeline has not yet been deployed.    
---

## Sprint Retrospective

**What worked well:**
- A branch-per-task workflow kept parallel work across retrieval, knowledge base, interface and evaluation from colliding
- Daily check-ins in the group chat surfaced blockers quickly
- Pull request review caught integration issues early, including documentation that did not match the running pipeline, and avoided duplicated effort
- The team acted on mentor feedback both times, building evaluation infrastructure after the first meeting and a working deployed demo after the second
- A failure investigation showed that the flagged retrieval cases all had the correct chunk within the top 5, so no risky late code change was needed
- Evaluation covered answer faithfulness and source attribution as well as retrieval, which directly answers the mentor's first question about measuring quality

**What did not work as smoothly:**
- Documentation described dense retrieval as deployed before the pipeline actually used it.
- Some tasks took longer than expected and briefly blocked downstream integration work
- Several pull requests waited a long time for review, which held up dependent tasks

**Blockers:**
- The dense retrieval integration has been approved but is awaiting merge and verification on the test deployment, and the final end-to-end evaluation depends on both
- The sources panel sometimes shows extra top-5 sources that the answer does not need

**Next actions:**
- Merge the approved dense retrieval integration and verify it on the test deployment
- Run the final end-to-end chatbot evaluation and split any fixes by retrieval, integration or generation
- Update the ground truth with the second valid chunk found during the failure investigation
- Run final production smoke tests and lock the demo path
- Update the final documentation with the end-to-end results
