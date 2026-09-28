"""Document ingestion boundary for approved career-knowledge sources."""

from pathlib import Path


def ingest_document(path: Path) -> str:
    """Read a UTF-8 text document; source validation and metadata come later."""
    return path.read_text(encoding="utf-8")