"""
load_kb.py
Loads the Victorian Rental Rights Assistant knowledge base (KB01-KB07 .txt files)
and splits each document into retrieval-ready chunks, one per numbered section.
"""

import os
import re
import json
from dataclasses import dataclass, asdict
from typing import List

KB_DIR = os.path.join(os.path.dirname(__file__), "..", "knowledge_base")

METADATA_FIELDS = [
    "DOCUMENT_ID", "TITLE", "CATEGORY", "AUTHORITY", "SOURCE_URL",
    "ACCESS_DATE", "LAST_UPDATED", "JURISDICTION", "STATUS",
]

SECTION_HEADER_RE = re.compile(r"^\s*(\d{1,2})\.\s+(.+)$", re.MULTILINE)
EXCLUDED_SECTION_TITLES = {"IMPORTANT RAG RETRIEVAL TERMS"}


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


def _parse_metadata(header_block: str) -> dict:
    meta = {}
    for field in METADATA_FIELDS:
        m = re.search(rf"^{field}:\s*(.+)$", header_block, re.MULTILINE)
        meta[field] = m.group(1).strip() if m else ""
    return meta


def _split_sections(body: str):
    matches = list(SECTION_HEADER_RE.finditer(body))
    sections = []
    for i, m in enumerate(matches):
        sec_num, sec_title = m.group(1), m.group(2).strip()
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(body)
        text = body[start:end].strip()
        sections.append((sec_num, sec_title, text))
    return sections


def load_document(filepath: str) -> List[Chunk]:
    with open(filepath, encoding="utf-8") as f:
        content = f.read()

    first_section_match = SECTION_HEADER_RE.search(content)
    header_block = content[: first_section_match.start()] if first_section_match else content
    body = content[first_section_match.start():] if first_section_match else ""

    meta = _parse_metadata(header_block)
    doc_id = meta.get("DOCUMENT_ID") or os.path.splitext(os.path.basename(filepath))[0]

    chunks = []
    for sec_num, sec_title, text in _split_sections(body):
        if sec_title.upper() in EXCLUDED_SECTION_TITLES or not text:
            continue
        chunks.append(
            Chunk(
                chunk_id=f"{doc_id}_S{sec_num}",
                doc_id=doc_id,
                title=meta.get("TITLE", ""),
                category=meta.get("CATEGORY", ""),
                authority=meta.get("AUTHORITY", ""),
                source_url=meta.get("SOURCE_URL", ""),
                section_number=sec_num,
                section_title=sec_title,
                text=text,
            )
        )
    return chunks


def load_knowledge_base(kb_dir: str = KB_DIR) -> List[Chunk]:
    all_chunks = []
    for fname in sorted(os.listdir(kb_dir)):
        if fname.lower().endswith(".txt"):
            all_chunks.extend(load_document(os.path.join(kb_dir, fname)))
    return all_chunks


if __name__ == "__main__":
    chunks = load_knowledge_base()
    print(f"Loaded {len(chunks)} chunks from knowledge base.\n")
    for c in chunks:
        print(f"[{c.chunk_id}] {c.section_title} ({len(c.text.split())} words)")

    out_path = os.path.join(os.path.dirname(__file__), "chunks.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump([asdict(c) for c in chunks], f, indent=2)
    print(f"\nSaved chunks to {out_path}")