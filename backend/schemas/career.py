"""Career catalog response schemas."""

from pydantic import BaseModel, ConfigDict


class CareerRead(BaseModel):
    id: int
    name: str
    description: str
    category: str

    model_config = ConfigDict(from_attributes=True)


class CareerSkillRead(BaseModel):
    name: str
    importance: float
    required: bool


class CareerDetailRead(CareerRead):
    required_skills: list[CareerSkillRead]