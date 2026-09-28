"""Set-based skill similarity baseline; replaceable by semantic embeddings."""


def jaccard_similarity(left: set[str], right: set[str]) -> float:
    """Return Jaccard similarity, defining two empty sets as no evidence."""
    union = left | right
    return len(left & right) / len(union) if union else 0.0