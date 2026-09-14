"""Prepare Victorian rental-rights documents for retrieval.

This module reads the curated KB01-KB07 text documents, extracts metadata,
summaries, and numbered sections, validates the document structure, and
prepares the knowledge base for later chunk generation.

The original knowledge-base files are treated as read-only source documents.
"""

from dataclasses import dataclass
from pathlib import Path
import re
from typing import Optional


PROJECT_ROOT = Path(__file__).resolve().parent.parent
KNOWLEDGE_BASE_DIR = PROJECT_ROOT / "knowledge_base"


SECTION_PATTERN = re.compile(
    r"^\s*(\d{1,2})\.\s+(.+?)\s*$",
    re.MULTILINE,
)


REQUIRED_METADATA_FIELDS = (
    "document_id",
    "title",
    "category",
    "authority",
    "source_url",
    "access_date",
    "jurisdiction",
    "status",
)


@dataclass(frozen=True)
class DocumentMetadata:
    """Metadata preserved from a rental-rights knowledge-base document."""

    document_id: str
    title: str
    category: str
    authority: str
    source_url: str
    access_date: str
    jurisdiction: str
    status: str
    last_updated: Optional[str] = None
    secondary_source_url: Optional[str] = None


@dataclass(frozen=True)
class Section:
    """A numbered semantic section extracted from a KB document."""

    number: int
    title: str
    text: str


@dataclass(frozen=True)
class KnowledgeDocument:
    """Structured representation of one source knowledge-base document."""

    metadata: DocumentMetadata
    summary: str
    sections: tuple[Section, ...]


def _normalise_text(text: str) -> str:
    """Normalise whitespace without changing the original wording."""

    cleaned_lines = []

    for line in text.splitlines():
        stripped = line.strip()

        if stripped:
            cleaned_lines.append(stripped)

    return "\n".join(cleaned_lines)


def _metadata_value(header: str, field: str) -> Optional[str]:
    """Return one metadata value from the document header."""

    match = re.search(
        rf"^{re.escape(field)}:\s*(.+?)\s*$",
        header,
        re.MULTILINE,
    )

    if match is None:
        return None

    return match.group(1).strip()


def _extract_summary(header: str) -> str:
    """Extract the SUMMARY block from the document header."""

    summary_match = re.search(
        r"^SUMMARY\s*\n(.*)",
        header,
        re.MULTILINE | re.DOTALL,
    )

    if summary_match is None:
        return ""

    return _normalise_text(summary_match.group(1))


def _extract_sections(
    content: str,
    section_matches: list[re.Match],
) -> tuple[Section, ...]:
    """Extract numbered sections from a knowledge-base document."""

    sections = []

    for index, match in enumerate(section_matches):
        section_number = int(match.group(1))
        section_title = match.group(2).strip()

        start = match.end()

        if index + 1 < len(section_matches):
            end = section_matches[index + 1].start()
        else:
            end = len(content)

        section_text = _normalise_text(content[start:end])

        sections.append(
            Section(
                number=section_number,
                title=section_title,
                text=section_text,
            )
        )

    return tuple(sections)


def parse_document(path: Path) -> KnowledgeDocument:
    """Parse one rental-rights knowledge-base text document."""

    if not path.exists():
        raise FileNotFoundError(f"Knowledge-base file not found: {path}")

    if not path.is_file():
        raise ValueError(f"Knowledge-base path is not a file: {path}")

    content = path.read_text(encoding="utf-8")

    if not content.strip():
        raise ValueError(f"Knowledge-base file is empty: {path.name}")

    section_matches = list(SECTION_PATTERN.finditer(content))

    if not section_matches:
        raise ValueError(
            f"No numbered sections found in {path.name}"
        )

    first_section_start = section_matches[0].start()
    header = content[:first_section_start]

    metadata = DocumentMetadata(
        document_id=_metadata_value(header, "DOCUMENT_ID") or "",
        title=_metadata_value(header, "TITLE") or "",
        category=_metadata_value(header, "CATEGORY") or "",
        authority=_metadata_value(header, "AUTHORITY") or "",
        source_url=_metadata_value(header, "SOURCE_URL") or "",
        access_date=_metadata_value(header, "ACCESS_DATE") or "",
        jurisdiction=_metadata_value(header, "JURISDICTION") or "",
        status=_metadata_value(header, "STATUS") or "",
        last_updated=_metadata_value(header, "LAST_UPDATED"),
        secondary_source_url=_metadata_value(
            header,
            "SECONDARY_SOURCE_URL",
        ),
    )

    summary = _extract_summary(header)

    sections = _extract_sections(
        content=content,
        section_matches=section_matches,
    )

    return KnowledgeDocument(
        metadata=metadata,
        summary=summary,
        sections=sections,
    )


def validate_document(document: KnowledgeDocument) -> list[str]:
    """Return validation errors for one parsed knowledge-base document."""

    errors = []
    metadata = document.metadata

    for field_name in REQUIRED_METADATA_FIELDS:
        value = getattr(metadata, field_name)

        if not value:
            errors.append(
                f"{metadata.document_id or 'UNKNOWN'}: "
                f"missing required metadata field '{field_name}'"
            )

    if not document.summary:
        errors.append(
            f"{metadata.document_id or 'UNKNOWN'}: "
            "missing SUMMARY text"
        )

    if not document.sections:
        errors.append(
            f"{metadata.document_id or 'UNKNOWN'}: "
            "no numbered sections found"
        )

    seen_section_numbers = set()

    for section in document.sections:
        if section.number in seen_section_numbers:
            errors.append(
                f"{metadata.document_id}: "
                f"duplicate section number {section.number}"
            )

        seen_section_numbers.add(section.number)

        if not section.title:
            errors.append(
                f"{metadata.document_id}: "
                f"section {section.number} has no title"
            )

        if (
            section.title.upper() != "IMPORTANT RAG RETRIEVAL TERMS"
            and not section.text
        ):
            errors.append(
                f"{metadata.document_id}: "
                f"section {section.number} has no content"
            )

    return errors


def load_documents(
    kb_dir: Path = KNOWLEDGE_BASE_DIR,
) -> tuple[KnowledgeDocument, ...]:
    """Load all KB text files in deterministic filename order."""

    paths = sorted(kb_dir.glob("KB*.txt"))

    if not paths:
        raise FileNotFoundError(
            f"No KB text files found in {kb_dir}"
        )

    documents = []

    for path in paths:
        documents.append(parse_document(path))

    return tuple(documents)


def validate_knowledge_base(
    documents: tuple[KnowledgeDocument, ...],
) -> list[str]:
    """Validate the complete rental-rights knowledge base."""

    errors = []
    seen_document_ids = set()

    for document in documents:
        document_id = document.metadata.document_id

        if document_id in seen_document_ids:
            errors.append(
                f"Duplicate DOCUMENT_ID: {document_id}"
            )

        seen_document_ids.add(document_id)

        errors.extend(
            validate_document(document)
        )

    return errors


def main() -> None:
    """Load and validate the current knowledge base."""

    documents = load_documents()
    errors = validate_knowledge_base(documents)

    print(f"Documents loaded: {len(documents)}")

    if errors:
        print("Validation failed:")

        for error in errors:
            print(f"- {error}")

        raise SystemExit(1)

    print("Validation passed.")

    for document in documents:
        retrieval_sections = [
            section
            for section in document.sections
            if section.title.upper()
            != "IMPORTANT RAG RETRIEVAL TERMS"
        ]

        print(
            f"{document.metadata.document_id}: "
            f"{len(retrieval_sections)} retrieval sections"
        )


if __name__ == "__main__":
    main()