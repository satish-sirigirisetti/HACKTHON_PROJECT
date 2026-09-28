"""Small domain validators not tied to HTTP request handling."""


def validate_proficiency(value: float) -> float:
    """Validate and return a normalized proficiency value from zero to one."""
    if not 0.0 <= value <= 1.0:
        raise ValueError("Proficiency must be between 0 and 1")
    return value