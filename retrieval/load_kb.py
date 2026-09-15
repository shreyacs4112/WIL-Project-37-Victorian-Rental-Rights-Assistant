"""
load_kb.py
Loads pre-chunked, pre-validated Victorian Rental Rights knowledge base chunks
from data/processed/kb_chunks.json (produced by the knowledge-base preparation
pipeline) instead of re-parsing raw .txt files.
"""

import json
import os
from dataclasses import dataclass


CHUNKS_PATH = os.path.join(
    os.path.dirname(__file__), "..", "data", "processed", "kb_chunks.json"
)


@dataclass
class Chunk:
    chunk_id: str
    doc_id: str
    title: str
    category: str
    authority: str
    source_url: str
    section_number: str
    section_title: str
    text: str


def load_knowledge_base(path: str = CHUNKS_PATH):
    with open(path, encoding="utf-8") as f:
        raw_chunks = json.load(f)

    return [
        Chunk(
            chunk_id=c["chunk_id"],
            doc_id=c["document_id"],
            title=c["title"],
            category=c["category"],
            authority=c["authority"],
            source_url=c["source_url"],
            section_number=str(c["section_number"]),
            section_title=c["section_title"],
            text=c["text"],
        )
        for c in raw_chunks
    ]


if __name__ == "__main__":
    chunks = load_knowledge_base()
    print(f"Loaded {len(chunks)} chunks from {CHUNKS_PATH}\n")
    for c in chunks[:10]:
        print(f"[{c.chunk_id}] {c.section_title} ({len(c.text.split())} words)")