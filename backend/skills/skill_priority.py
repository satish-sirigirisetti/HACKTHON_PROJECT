"""Transparent skill-gap prioritization helpers."""


def prioritize_gaps(gaps: dict[str, float]) -> list[tuple[str, float]]:
    """Order gaps by descending stated importance, then by skill name."""
    return sorted(gaps.items(), key=lambda item: (-item[1], item[0].casefold()))