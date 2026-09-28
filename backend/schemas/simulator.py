"""What-if career simulation schemas."""

from pydantic import BaseModel, Field, field_validator, model_validator

from backend.schemas.recommendation import CareerRecommendation


class HypotheticalSkill(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    proficiency: float = Field(ge=0.0, le=1.0)

    @field_validator("name", mode="before")
    @classmethod
    def strip_name(cls, value: object) -> object:
        return value.strip() if isinstance(value, str) else value


class SimulationRequest(BaseModel):
    skills: list[HypotheticalSkill] = Field(min_length=1, max_length=50)

    @model_validator(mode="after")
    def validate_unique_skills(self) -> "SimulationRequest":
        names = [skill.name.casefold() for skill in self.skills]
        if len(names) != len(set(names)):
            raise ValueError("Each hypothetical skill may only appear once")
        return self


class CareerScenarioChange(BaseModel):
    career_id: int
    career_name: str
    current_score: float
    simulated_score: float
    rank_change: int


class SimulationRead(BaseModel):
    method: str
    baseline: list[CareerRecommendation]
    simulated: list[CareerRecommendation]
    changes: list[CareerScenarioChange]