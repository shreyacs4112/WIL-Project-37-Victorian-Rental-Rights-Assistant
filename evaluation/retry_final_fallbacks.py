import json
import time
from rag.pipeline import run_rag_pipeline

FILE = "evaluation/final_chatbot_raw_results.json"

with open(FILE) as f:
    results = json.load(f)

fallbacks = [
    r for r in results
    if r.get("expected_behavior") == "answer"
    and r.get("generation_fallback") is True
]

print("Fallbacks to retry:", len(fallbacks))

for index, record in enumerate(fallbacks, start=1):
    qid = record["question_id"]
    question = record["question"]

    print(f"\n[{index}/{len(fallbacks)}] Retrying {qid}...")

    for attempt in range(1, 4):
        print(f"  Attempt {attempt}/3")

        result = run_rag_pipeline(question)
        answer = result.get("answer", "")

        still_fallback = (
            "Answer generation is temporarily unavailable" in answer
            or "I could not find enough relevant information" in answer
        )

        if not still_fallback:
            retrieved_ids = [
                chunk["chunk_id"]
                for chunk in result.get("retrieved_chunks", [])
            ]

            relevant_ids = record.get("relevant_chunk_ids", [])
            relevant_hits = [
                chunk_id
                for chunk_id in relevant_ids
                if chunk_id in retrieved_ids
            ]

            sources = result.get("sources", [])

            record["retrieved_chunk_ids"] = retrieved_ids
            record["relevant_hits"] = relevant_hits
            record["any_relevant_retrieved"] = (
                bool(relevant_hits) if relevant_ids else None
            )
            record["all_relevant_retrieved"] = (
                set(relevant_ids).issubset(set(retrieved_ids))
                if relevant_ids else None
            )
            record["answer"] = answer
            record["context"] = result.get("context", "")
            record["sources"] = sources
            record["generation_fallback"] = False
            record["retry_attempts"] = attempt

            print("  Success")
            break

        print("  Still unavailable")

        if attempt < 3:
            time.sleep(10)

    time.sleep(10)

with open(FILE, "w") as f:
    json.dump(results, f, indent=2)

remaining = sum(
    1 for r in results
    if r.get("expected_behavior") == "answer"
    and r.get("generation_fallback") is True
)

print("\nRemaining generation fallbacks:", remaining)
print("Updated:", FILE)
