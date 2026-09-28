"""Input normalization used before feature extraction and model inference."""


def normalize_labels(values: list[str]) -> list[str]:
    """Normalize labels consistently for deterministic feature matching."""
    return sorted({value.strip().casefold() for value in values if value.strip()})