"""Canonicalize skill labels before deterministic matching."""


def normalize_skill_name(name: str) -> str:
    """Normalize case and whitespace without guessing aliases."""
    return " ".join(name.casefold().split())