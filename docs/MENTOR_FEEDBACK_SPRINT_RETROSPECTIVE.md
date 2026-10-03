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

**Team response:** Prioritised getting the end-to-end pipeline deployed, stable and demoable in the production environment, and planned a final end-to-end evaluation before fixing remaining issues. Dense retrieval has since been merged into the TEST environment and passed all automated tests, with initial live smoke testing also completed. Formal TEST deployment verification is still pending, and production still runs BM25 pending that verification and promotion.

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
- Documentation described dense retrieval as deployed before the pipeline actually used it, and this was only caught in review
- Some tasks took longer than expected and briefly blocked downstream integration work
- Several pull requests waited a long time for review, which held up dependent tasks

**Blockers:**
- TEST deployment verification for the merged dense retrieval integration is still pending, and two ranking issues found during initial smoke testing, one on a repairs question and one on a bond-refund question, need to be covered by the final end-to-end evaluation before production promotion
- The sources panel sometimes shows extra top-5 sources that the answer does not need

**Next actions:**
- Complete TEST deployment verification for the merged dense retrieval integration
- Run the final end-to-end evaluation on the verified TEST pipeline, covering the two ranking issues found in smoke testing
- Run the final end-to-end chatbot evaluation and split any fixes by retrieval, integration or generation
- Update the ground truth with the second valid chunk found during the failure investigation
- Promote the verified dense pipeline from TEST to production and run final production smoke tests
- Update the final documentation with the end-to-end results
