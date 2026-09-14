# Knowledge Base Preparation and Chunking

## Purpose

This document describes how the Victorian Rental Rights Assistant prepares
the curated rental-rights knowledge base for retrieval.

The preprocessing step converts the source knowledge-base documents in
`knowledge_base/` into structured, retrieval-ready chunks while preserving
topic identifiers and source attribution metadata.

The original KB01-KB07 files remain unchanged and are treated as read-only
source documents.

---

## Input Documents

The preprocessing pipeline reads:

- KB01_REPAIRS.txt
- KB02_BOND.txt
- KB03_RENT_INCREASES.txt
- KB04_ENTRY_INSPECTIONS.txt
- KB05_MINIMUM_STANDARDS.txt
- KB06_MOVING_IN.txt
- KB07_MOVING_OUT.txt

Each document contains:

- document identifier
- title
- category
- authority
- primary source URL
- access date
- jurisdiction
- status
- optional last-updated date
- optional secondary source URL
- summary
- numbered topic sections

---

## Chunking Strategy

The knowledge base uses section-aware chunking.

Each numbered semantic section becomes one retrieval chunk.

For example:

```text
KB01
1. URGENT AND NON-URGENT REPAIRS
2. EXAMPLES OF URGENT REPAIRS
3. REPORTING REPAIRS
```

becomes:

```text
KB01_S1
KB01_S2
KB01_S3
```

This strategy was selected after inspecting the existing documents.

Across the current knowledge base:

- 109 retrieval sections are produced
- the smallest section is approximately 9 words
- the largest section is approximately 133 words
- the average section is approximately 61 words

Because the sections are already compact and topic-focused, additional
character-based or token-based splitting is not required for the current
dataset.

Keeping each numbered section intact also avoids splitting related legal
information across arbitrary chunk boundaries.

---

## Excluded Content

Sections titled:

```text
IMPORTANT RAG RETRIEVAL TERMS
```

are not exported as retrieval chunks.

These sections are supporting keyword lists rather than authoritative content
that should be returned directly as evidence.

---

## Text Cleaning

The preprocessing step performs formatting-only cleaning.

It:

- removes unnecessary leading and trailing whitespace
- removes redundant blank lines
- preserves the original wording of the rental-rights content

The preprocessing step does not paraphrase or rewrite legal information.

---

## Chunk Metadata

Each generated chunk contains:

```text
chunk_id
document_id
title
category
authority
source_url
secondary_source_url
access_date
last_updated
jurisdiction
status
section_number
section_title
text
```

Example chunk identifier:

```text
KB01_S1
```

This allows retrieved content to retain its original topic and source context
for later citation and attribution.

---

## Output

The preprocessing script generates:

```text
data/processed/kb_chunks.json
```

The current processed knowledge base contains 109 unique retrieval chunks
across KB01-KB07.

---

## Running the Preprocessing Pipeline

From the project root, run:

```bash
python3 preprocessing/prepare_chunks.py
```

The script validates the source documents, generates the retrieval chunks,
validates the generated chunks, and writes the processed JSON file to:

```text
data/processed/kb_chunks.json
```

---

## Validation

The preprocessing pipeline checks the source documents and generated chunks
before producing the retrieval dataset.

Validation includes checks for:

- required metadata fields
- document identifiers
- numbered sections
- empty section content
- duplicate document identifiers
- duplicate section numbers
- duplicate chunk identifiers
- missing source URLs
- missing section titles
- missing chunk text

Invalid content causes preprocessing to report validation errors rather than
silently producing an incomplete retrieval dataset.

---

## Automated Tests

Automated preprocessing tests are located in:

```text
tests/test_prepare_chunks.py
```

Run the tests from the project root with:

```bash
python3 -m pytest tests/test_prepare_chunks.py -v
```

The test suite verifies:

- all seven knowledge-base documents can be loaded
- the current knowledge base passes validation
- 109 retrieval chunks are generated
- chunk identifiers are unique
- required source metadata is preserved
- retrieval-term sections are excluded
- generated chunks pass validation
- KB03 secondary-source metadata is preserved
- expected KB01 chunk identity is retained
- missing files are handled
- empty files are rejected
- documents without numbered sections are rejected

---

## Retrieval Integration

The generated JSON file provides a consistent interface between document
preparation and retrieval.

Retrieval components such as BM25 and dense retrieval can index fields such
as `text` and `section_title` while retaining the associated metadata for
topic identification and source attribution.

Each retrieval result can therefore be traced back to its original KB
document, numbered section, authority, and source URL.

Keeping preprocessing separate from retrieval ranking also allows the
retrieval implementation to change without modifying the original curated
knowledge-base documents.
