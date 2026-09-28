"""Overlap-aware text chunking for retrieval preparation."""


def chunk_text(text: str, chunk_size: int = 800, overlap: int = 120) -> list[str]:
    """Split text into bounded character windows with validated overlap."""
    if chunk_size <= 0 or overlap < 0 or overlap >= chunk_size:
        raise ValueError("Require chunk_size > overlap >= 0")
    normalized = " ".join(text.split())
    return [normalized[start : start + chunk_size] for start in range(0, len(normalized), chunk_size - overlap)]