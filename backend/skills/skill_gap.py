"""Required-skill gap detection."""


def find_missing_skills(required: set[str], student: set[str]) -> list[str]:
    """Return sorted required skills not present in the student's skill set."""
    return sorted(required - student)