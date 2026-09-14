from pathlib import Path

import pytest

from preprocessing.prepare_chunks import (
    EXCLUDED_SECTION_TITLES,
    KNOWLEDGE_BASE_DIR,
    create_chunks,
    load_documents,
    parse_document,
    validate_chunks,
    validate_knowledge_base,
)


def test_all_seven_knowledge_base_documents_load():
    documents = load_documents()

    assert len(documents) == 7

    document_ids = {
        document.metadata.document_id
        for document in documents
    }

    assert document_ids == {
        "KB01",
        "KB02",
        "KB03",
        "KB04",
        "KB05",
        "KB06",
        "KB07",
    }


def test_current_knowledge_base_passes_validation():
    documents = load_documents()

    errors = validate_knowledge_base(documents)

    assert errors == []


def test_chunk_generation_creates_expected_number_of_chunks():
    documents = load_documents()

    chunks = create_chunks(documents)

    assert len(chunks) == 109


def test_chunk_ids_are_unique():
    documents = load_documents()

    chunks = create_chunks(documents)

    chunk_ids = [
        chunk.chunk_id
        for chunk in chunks
    ]

    assert len(chunk_ids) == len(set(chunk_ids))


def test_chunks_preserve_required_source_metadata():
    documents = load_documents()

    chunks = create_chunks(documents)

    for chunk in chunks:
        assert chunk.document_id
        assert chunk.title
        assert chunk.category
        assert chunk.authority
        assert chunk.source_url
        assert chunk.access_date
        assert chunk.jurisdiction
        assert chunk.status


def test_chunks_do_not_include_retrieval_terms_section():
    documents = load_documents()

    chunks = create_chunks(documents)

    for chunk in chunks:
        assert (
            chunk.section_title.upper()
            not in EXCLUDED_SECTION_TITLES
        )


def test_generated_chunks_pass_validation():
    documents = load_documents()

    chunks = create_chunks(documents)

    errors = validate_chunks(chunks)

    assert errors == []


def test_kb03_preserves_secondary_source_url():
    path = KNOWLEDGE_BASE_DIR / "KB03_RENT_INCREASES.txt"

    document = parse_document(path)

    assert document.metadata.secondary_source_url is not None
    assert "challenging-rent-increases-or-high-rent" in (
        document.metadata.secondary_source_url
    )


def test_kb01_first_chunk_has_expected_identity():
    documents = load_documents()

    chunks = create_chunks(documents)

    first_chunk = chunks[0]

    assert first_chunk.chunk_id == "KB01_S1"
    assert first_chunk.document_id == "KB01"
    assert (
        first_chunk.section_title
        == "URGENT AND NON-URGENT REPAIRS"
    )


def test_parse_document_raises_for_missing_file(tmp_path: Path):
    missing_path = tmp_path / "missing.txt"

    with pytest.raises(FileNotFoundError):
        parse_document(missing_path)


def test_parse_document_raises_for_empty_file(tmp_path: Path):
    empty_file = tmp_path / "empty.txt"
    empty_file.write_text("", encoding="utf-8")

    with pytest.raises(ValueError, match="empty"):
        parse_document(empty_file)


def test_parse_document_raises_without_numbered_sections(
    tmp_path: Path,
):
    invalid_file = tmp_path / "invalid.txt"

    invalid_file.write_text(
        "DOCUMENT_ID: KB99\n"
        "TITLE: Invalid Example\n"
        "SUMMARY\n"
        "No numbered sections here.\n",
        encoding="utf-8",
    )

    with pytest.raises(
        ValueError,
        match="No numbered sections found",
    ):
        parse_document(invalid_file)
