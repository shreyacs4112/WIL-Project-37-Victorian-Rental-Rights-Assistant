# Final End-to-End Chatbot Evaluation

**Evaluation date:** 3 October 2026  
**Evaluation dataset:** `evaluation/evaluation_set.json`  
**Total questions:** 33  
**In-scope questions:** 28  
**Out-of-scope questions:** 5  

## Purpose

This final evaluation assesses the complete Victorian Rental Rights Assistant after the latest RAG integration. The evaluation covers retrieval relevance, answer faithfulness and groundedness, response relevance, source attribution, out-of-scope handling, and generation reliability.

## Method

All 33 questions from the team's authoritative evaluation set were run through the current end-to-end RAG pipeline.

For each in-scope question, the evaluation checked:

- whether at least one expected evidence chunk was retrieved
- whether all expected evidence chunks were retrieved
- whether the expected source was present
- whether the generated answer was supported by the retrieved context
- whether the answer addressed the user's question correctly and completely

The five out-of-scope questions were checked for safe refusal behaviour with no retrieved evidence or sources.

Generation failures from the initial run were preserved in `final_chatbot_initial_run.json`. Failed generations were then retried so that answer quality could be reviewed independently from temporary external inference-service availability.

## Quantitative Results

| Metric | Result |
|---|---:|
| Total questions evaluated | 33 |
| In-scope questions | 28 |
| Out-of-scope questions | 5 |
| At least one expected evidence chunk retrieved | 28/28 (100%) |
| All expected evidence chunks retrieved | 27/28 (96.4%) |
| Expected source present | 28/28 (100%) |
| Correct out-of-scope refusals | 5/5 (100%) |
| Initial generation fallbacks | 19/28 (67.9%) |
| Initial successful generations | 9/28 (32.1%) |
| Remaining generation fallbacks after retries | 0 |

## Manual Answer-Quality Review

The 28 in-scope answers were manually reviewed against the expected evidence and retrieved context.

- **Fully correct and well grounded:** 20/28 (71.4%)
- **Correct but partially incomplete:** 7/28 (25.0%)
- **Incorrect:** 1/28 (3.6%)

### Incorrect Answer

**Q014 – Inspection at 7 pm**

The retrieved context correctly states that a rental provider or agent can generally enter between **8 am and 6 pm**, and that entry outside those hours is only permitted if the renter agrees.

However, the generated answer incorrectly stated that **7 pm falls within the normal permitted hours**.

This is an important example showing that correct retrieval does not always guarantee correct reasoning or answer generation.

### Partially Incomplete Answers

The following questions were grounded in the retrieved evidence but omitted an important qualification or detail:

- **Q007** – correctly stated that a renter can start a bond claim, but did not include all expected details about eligibility and Service Victoria authentication.
- **Q011** – correctly stated the 90-day notice period for a rent increase, but omitted that the notice must be written using the prescribed form.
- **Q013** – correctly stated that a routine inspection requires 7 days' notice, but omitted that routine inspections can normally occur no more than once every 6 months.
- **Q017** – correctly stated the heating requirement, but omitted the important qualification that the energy-efficiency requirement applies to rental agreements entered into from **29 March 2023**.
- **Q021** – correctly stated the 5-business-day condition-report deadline, but omitted that weekends and public holidays are not counted as business days.
- **Q023** – correctly stated the general one-month bond limit and the exception for weekly rent above $900, but omitted that in some circumstances the rental provider may apply to VCAT for an increased bond limit.
- **Q025** – correctly stated the general 28-day notice requirement, but omitted the fixed-term qualification that the notice should not specify a date earlier than the agreement's end date unless a lawful early-termination reason applies.

## Retrieval Finding

**Q028** was the only question where all expected evidence chunks were not retrieved.

Expected chunks:

- `KB07_S11`
- `KB07_S13`

Retrieved chunks included `KB07_S13` but not `KB07_S11`.

However, alternative retrieved evidence from the bond knowledge base still clearly stated that fair wear and tear cannot be claimed as damage from the bond. The generated answer was therefore correct and grounded despite incomplete expected-chunk retrieval.

This shows that exact expected-chunk coverage is useful for measuring retrieval consistency, but a missed expected chunk does not always result in an incorrect answer when equivalent evidence is available elsewhere in the knowledge base.

## Out-of-Scope Handling

All **5/5 out-of-scope questions** were handled correctly.

The chatbot returned the expected safe refusal and did not provide retrieved evidence or sources for unsupported topics.

This indicates that the scope-control behaviour worked correctly on the final evaluation set.

## Generation Reliability

The initial run produced **19 temporary generation fallbacks** across the 28 in-scope questions.

Retrieval continued to operate correctly during these failures, but the external LLM inference step returned the safe fallback message.

The initial-run results were preserved separately. The failed questions were then retried with delays and all eventually generated successfully.

After retries:

- **Remaining generation fallbacks: 0**
- **Successful final generations: 28/28**

This indicates that the main reliability issue observed during evaluation was external generation availability rather than retrieval failure.

## Source Attribution

The expected authoritative source was present for **28/28 in-scope questions**.

This confirms strong source coverage. However, expected-source presence only measures whether the correct source appears in the returned source set; it does not guarantee that every returned top-k source is equally relevant.

## Main Findings

1. **Retrieval performance was strong.** Every in-scope question retrieved at least one expected evidence chunk and 27/28 retrieved all expected evidence.

2. **Source coverage was strong.** The expected source was present for every in-scope question.

3. **Out-of-scope handling was reliable.** All five unsupported questions were refused safely.

4. **Correct retrieval does not guarantee correct reasoning.** Q014 retrieved the correct entry-hours evidence but generated an incorrect interpretation.

5. **Important legal qualifications can be omitted.** Several otherwise correct answers left out dates, conditions, notice-form requirements, or other qualifications.

6. **Equivalent evidence can compensate for incomplete retrieval.** Q028 missed one expected chunk but still generated a correct answer using alternative retrieved evidence.

7. **Generation availability remains an operational concern.** Nineteen answers initially fell back because the external inference service was temporarily unavailable, although all recovered after retries.

## Recommended Improvements

Future improvements should focus on:

- adding automatic retry handling for temporary LLM inference failures
- adding answer-validation checks for numerical values, times, dates and legal conditions
- preserving important legal qualifications from retrieved evidence
- improving completeness checks so answers do not omit important parts of the expected evidence
- monitoring source precision as well as expected-source presence
- continuing to test paraphrased and edge-case questions

## Conclusion

The final evaluation shows that the RAG pipeline provides strong retrieval coverage, authoritative source attribution and safe out-of-scope handling.

The main remaining risks are generation reliability and occasional reasoning or completeness errors after correct evidence has already been retrieved. The clearest example is Q014, where the system retrieved the correct entry-hours rule but interpreted 7 pm incorrectly.

Overall, the final evaluation provides evidence that retrieval and grounding are strong while also identifying specific areas for improving answer validation, completeness and production reliability.
