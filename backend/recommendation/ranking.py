"""Stable recommendation ordering helpers."""

from backend.schemas.recommendation import CareerRecommendation


def rank_recommendations(
    recommendations: list[CareerRecommendation], limit: int = 10
) -> list[CareerRecommendation]:
    """Sort by readiness then role name, with an explicit result limit."""
    return sorted(recommendations, key=lambda item: (-item.match_score, item.career_name))[:limit]