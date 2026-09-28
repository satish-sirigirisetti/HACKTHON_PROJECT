"""Explainable weighted skills match for a career's required skills."""

from collections.abc import Sequence


def match_required_skills(
    required_skills: Sequence[tuple[str, float]], student_proficiency: dict[str, float]
) -> tuple[float, list[str], list[str]]:
    """Return weighted readiness and matched/missing required skills."""
    if not required_skills:
        return 0.0, [], []
    total_weight = sum(weight for _, weight in required_skills)
    if total_weight <= 0:
        return 0.0, [], [name for name, _ in required_skills]
    normalized_proficiency = {name.casefold(): value for name, value in student_proficiency.items()}
    matched = [
        name for name, _ in required_skills if normalized_proficiency.get(name.casefold(), 0) > 0
    ]
    missing = [name for name, _ in required_skills if name not in matched]
    earned = sum(
        weight * normalized_proficiency.get(name.casefold(), 0.0)
        for name, weight in required_skills
    )
    return round(earned / total_weight, 3), matched, missing