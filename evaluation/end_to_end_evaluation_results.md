# End-to-End RAG Quality Evaluation

## Scope

The complete RAG pipeline was evaluated using all 33 questions in the evaluation dataset:

- 28 in-scope questions
- 5 out-of-scope questions
- 14 direct questions
- 14 paraphrased questions
- 5 out-of-scope controls

The evaluation considered retrieval coverage, source coverage, generated-answer quality, refusal behaviour, and generation reliability.

## Quantitative Results

| Metric | Result |
|---|---:|
| In-scope questions | 28 |
| Out-of-scope questions | 5 |
| At least one expected evidence chunk retrieved | 28/28 (100%) |
| All expected evidence chunks retrieved | 27/28 (96.4%) |
| Expected source present | 28/28 (100%) |
| Correct out-of-scope refusals | 5/5 (100%) |
| Initial generation fallbacks | 17/28 (60.7%) |
| Successful generations on initial run | 11/28 (39.3%) |
| Remaining generation fallbacks after retries | 0 |

## Answer Quality Review

Most generated answers were consistent with the expected evidence. Three notable generation-quality issues were identified.

### Q002 - Broken heater

**Result: Partial**

The retrieved context explicitly included failure of an essential heating service or appliance in the urgent-repair list.

However, the generated answer stated that there was not enough information to determine whether a broken heater was urgent and only suggested that it might be urgent.

This was an interpretation/answer-confidence issue rather than a retrieval failure.

### Q014 - Inspection at 7 pm

**Result: Incorrect**

The retrieved context clearly stated that a rental provider or agent can generally enter between 8 am and 6 pm, with entry outside those hours requiring the renter's agreement.

The generated answer incorrectly stated that 7 pm falls within the permitted 8 am to 6 pm period.

This is a generation/reasoning failure despite the correct evidence being retrieved.

### Q017 - Heating requirement

**Result: Partial**

The retrieved context stated that the energy-efficiency requirement applies to rental agreements entered into from 29 March 2023.

The generated answer omitted this date qualification and presented the energy-efficiency requirement generally.

This resulted in an overgeneralised answer even though the correct context was retrieved.

## Retrieval Failure Case

### Q028 - Fair wear and tear after moving out

Q028 was the only question for which not all expected ground-truth chunks were retrieved.

Expected:
- KB07_S11
- KB07_S13

Retrieved evidence included KB07_S13 but not KB07_S11.

Despite the incomplete expected-chunk coverage, the generated answer correctly stated that fair wear and tear cannot be claimed from the bond because sufficient supporting evidence was available in the retrieved context.

This demonstrates that missing one annotated relevant chunk does not necessarily cause an incorrect final answer when alternative supporting evidence is retrieved.

## Generation Reliability

The initial full evaluation run produced the temporary fallback:

"Answer generation is temporarily unavailable. Please refer to the retrieved evidence and sources below."

for 17 of the 28 in-scope questions.

The same questions were retried. Eight recovered during the first retry stage and the remaining nine subsequently generated successfully.

No generation fallbacks remained after retries.

This indicates that generation-service reliability is an important end-to-end limitation even when retrieval is functioning correctly.

## Source Behaviour

The expected authoritative source was present for all 28 in-scope questions.

However, the pipeline displays sources for the retrieved top-k chunks, which can include additional sources that do not materially support the final answer. This source-precision limitation was also identified during the earlier source-attribution evaluation.

## Main Failure Patterns

1. **Correct retrieval does not guarantee correct reasoning.**
   Q014 retrieved the correct entry-hours evidence but generated an answer that contradicted it.

2. **The model can be unnecessarily uncertain even when evidence is explicit.**
   Q002 retrieved the urgent-repair heating evidence but failed to give a clear conclusion.

3. **Important qualifications can be dropped during generation.**
   Q017 omitted the 29 March 2023 condition attached to the heating energy-efficiency requirement.

4. **Retrieval coverage can be incomplete without causing answer failure.**
   Q028 missed one annotated relevant chunk but still produced the correct answer using other retrieved evidence.

5. **Generation availability is a significant operational issue.**
   17 in-scope questions initially returned a temporary generation fallback, although all recovered after retries.

## Overall Findings

The integrated RAG system showed strong retrieval coverage and correct out-of-scope refusal behaviour across the evaluation dataset.

The main end-to-end weaknesses were generation reliability and occasional reasoning or qualification errors after correct evidence had already been retrieved.

Future improvements should focus on:
- retry handling for temporary generation failures,
- stronger answer validation against retrieved evidence,
- preserving legal conditions and date qualifications,
- reducing unnecessary uncertainty when evidence directly answers the question,
- improving source precision so displayed sources more clearly correspond to evidence used in the answer.
