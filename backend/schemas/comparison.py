"""Career comparison response schemas."""

from pydantic import BaseModel, Field

from backend.schemas.career import CareerDetailRead


class CareerComparisonRead(BaseModel):
    careers: list[CareerDetailRead] = Field(min_length=2, max_length=3)
    shared_required_skills: list[str]
    distinct_required_skills: dict[str, list[str]]
    student_skill_levels: dict[str, float]