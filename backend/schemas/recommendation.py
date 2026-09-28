"""Explainable baseline career recommendation schemas."""

from pydantic import BaseModel


class CareerRecommendation(BaseModel):
    career_id: int
    career_name: str
    match_score: float
    matched_skills: list[str]
    missing_skills: list[str]
    method: str = "weighted required-skill proficiency; not an ML prediction"