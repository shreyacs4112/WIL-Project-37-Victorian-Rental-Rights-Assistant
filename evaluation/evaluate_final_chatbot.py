import json
from rag.pipeline import run_rag_pipeline

DATASET = "evaluation/evaluation_set.json"
OUTPUT = "evaluation/final_chatbot_raw_results.json"

with open(DATASET) as f:
    data = json.load(f)

results = []

for index, item in enumerate(data, start=1):
    print(f"[{index}/{len(data)}] Running {item['question_id']}...")

    result = run_rag_pipeline(item["question"])

    retrieved_ids = [
        chunk["chunk_id"]
        for chunk in result.get("retrieved_chunks", [])
    ]

    relevant_ids = item.get("relevant_chunk_ids", [])

    relevant_hits = [
        chunk_id
        for chunk_id in relevant_ids
        if chunk_id in retrieved_ids
    ]

    sources = result.get("sources", [])
    expected_url = item.get("expected_source_url")

    expected_source_present = None
    if expected_url:
        expected_source_present = any(
            expected_url in str(source.get("source", ""))
            for source in sources
        )

    answer = result.get("answer", "")

    generation_fallback = (
        "Answer generation is temporarily unavailable" in answer
        or "I could not find enough relevant information" in answer
    )

    refusal = (
        "I can only help with questions about Victorian rental rights"
        in answer
    )

    correct_refusal = None
    if item["expected_behavior"] == "refuse":
        correct_refusal = (
            refusal
            and len(result.get("retrieved_chunks", [])) == 0
            and len(sources) == 0
        )

    record = {
        "question_id": item["question_id"],
        "question_type": item["question_type"],
        "question": item["question"],
        "in_scope": item["in_scope"],
        "expected_behavior": item["expected_behavior"],
        "expected_evidence": item.get("expected_evidence"),
        "relevant_chunk_ids": relevant_ids,
        "retrieved_chunk_ids": retrieved_ids,
        "relevant_hits": relevant_hits,
        "any_relevant_retrieved": (
            bool(relevant_hits) if relevant_ids else None
        ),
        "all_relevant_retrieved": (
            set(relevant_ids).issubset(set(retrieved_ids))
            if relevant_ids else None
        ),
        "expected_source_present": expected_source_present,
        "answer": answer,
        "context": result.get("context", ""),
        "sources": sources,
        "generation_fallback": generation_fallback,
        "correct_refusal": correct_refusal,
    }

    results.append(record)

with open(OUTPUT, "w") as f:
    json.dump(results, f, indent=2)

in_scope = [r for r in results if r["expected_behavior"] == "answer"]
out_scope = [r for r in results if r["expected_behavior"] == "refuse"]

print("\n=== END-TO-END RAW RESULTS ===")
print("Total questions:", len(results))
print("In-scope questions:", len(in_scope))
print("Out-of-scope questions:", len(out_scope))

print(
    "Any expected evidence retrieved:",
    sum(r["any_relevant_retrieved"] is True for r in in_scope),
    "/",
    len(in_scope),
)

print(
    "All expected evidence retrieved:",
    sum(r["all_relevant_retrieved"] is True for r in in_scope),
    "/",
    len(in_scope),
)

print(
    "Expected source present:",
    sum(r["expected_source_present"] is True for r in in_scope),
    "/",
    len(in_scope),
)

print(
    "Generation fallbacks:",
    sum(r["generation_fallback"] for r in in_scope),
)

print(
    "Correct out-of-scope refusals:",
    sum(r["correct_refusal"] is True for r in out_scope),
    "/",
    len(out_scope),
)

print("\nSaved:", OUTPUT)
