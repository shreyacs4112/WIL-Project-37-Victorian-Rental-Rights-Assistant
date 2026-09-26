# Faithfulness and Source Attribution Evaluation

## Scope

Representative testing was performed across all seven knowledge-base topics plus one out-of-scope question.

Questions tested:
- Q001 - Repairs
- Q005 - Bond claims
- Q009 - Rent increases
- Q013 - Entry and inspections
- Q017 - Minimum standards
- Q021 - Condition reports
- Q025 - Ending a rental agreement
- Q029 - Out-of-scope control

## Results

| Question | Expected behaviour | Faithfulness | Expected evidence retrieved | Source attribution | Observation |
|---|---|---|---|---|---|
| Q001 | Answer | Supported | Partial | Correct source present, extra sources displayed | KB01_S1 was retrieved but KB01_S2 was missed, so the answer was grounded but did not include the expected urgent-repair examples. |
| Q005 | Answer | Supported | Yes | Correct source present, extra source displayed | Bond-claim reasons were directly supported by retrieved context. |
| Q009 | Answer | Supported | Yes | Correct | The 12-month rent-increase rule was directly supported by KB03_S1. |
| Q013 | Answer | Supported | Yes | Correct source present, extra source displayed | The 7-day written notice requirement was directly supported by the retrieved context. |
| Q017 | Answer | Supported | Yes | Correct source present, extra sources displayed | Heating requirements and energy-efficiency examples were directly supported by KB05_S4. |
| Q021 | Answer | Supported | Yes | Correct | The 5-business-day condition-report deadline was directly supported by KB06_S6. |
| Q025 | Answer | Supported | Yes | Correct source present, extra sources displayed | The 28-day notice requirement was directly supported by KB07_S2. |
| Q029 | Refuse | Correct refusal | N/A | No sources displayed | Out-of-scope question was refused without retrieval or source display. |

## Summary

- 7 in-scope representative questions were evaluated for answer faithfulness.
- All 7 generated answers contained claims supported by the retrieved context.
- No unsupported or fabricated claims were observed in this representative sample.
- No expected-answer case was left unanswered.
- The out-of-scope control question was correctly refused.
- Q001 showed a completeness limitation caused by retrieval: one expected chunk (KB01_S2) was not retrieved, so the model could not provide the expected urgent-repair examples.
- Correct source topics were present for all in-scope cases.
- Source attribution precision remains a limitation because the application displays sources for every retrieved top-5 chunk, including chunks that may not contribute to the generated answer.

## Main Failure Patterns

1. **Retrieval gaps can reduce answer completeness without causing hallucination.**
   Q001 remained faithful to available context but omitted expected examples because KB01_S2 was not retrieved.

2. **Displayed sources are broader than the evidence actually used.**
   Several questions displayed unrelated source topics from lower-ranked retrieved chunks. This can make it unclear which source directly supports a particular answer claim.

3. **Faithfulness was strong in the representative sample.**
   The tested generated answers remained grounded in retrieved context and no unsupported legal requirements, amounts, timeframes, or procedures were observed.

## Suggested Refinement

Consider displaying only sources associated with the chunks that materially support the generated answer, or provide chunk-level/source-level attribution so users can see which evidence supports each answer.
