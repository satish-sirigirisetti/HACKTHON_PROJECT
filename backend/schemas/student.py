"""Validated schemas for student profiles."""

import re

from pydantic import AliasPath, BaseModel, ConfigDict, Field, field_validator


class StudentSkillInput(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    proficiency: float = Field(default=0.5, ge=0.0, le=1.0)

    @field_validator("name", mode="before")
    @classmethod
    def strip_skill_name(cls, value: object) -> object:
        return value.strip() if isinstance(value, str) else value


class StudentSkillRead(BaseModel):
    name: str = Field(validation_alias=AliasPath("skill", "name"))
    proficiency: float

    model_config = ConfigDict(from_attributes=True)


class StudentFields(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    email: str = Field(min_length=3, max_length=254)
    major: str | None = Field(default=None, max_length=160)
    graduation_year: int | None = Field(default=None, ge=2000, le=2100)
    target_role: str | None = Field(default=None, max_length=160)
    academic_performance: dict[str, object] = Field(default_factory=dict)
    interests: list[str] = Field(default_factory=list, max_length=30)
    soft_skills: list[str] = Field(default_factory=list, max_length=30)
    learning_goals: list[str] = Field(default_factory=list, max_length=30)

    @field_validator("name", "email", mode="before")
    @classmethod
    def strip_required_text(cls, value: object) -> object:
        return value.strip() if isinstance(value, str) else value

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str) -> str:
        if not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", value):
            raise ValueError("Enter a valid email address")
        return value.lower()


class StudentProfileInput(StudentFields):
    skills: list[StudentSkillInput] = Field(default_factory=list, max_length=50)

    @field_validator("skills")
    @classmethod
    def validate_unique_skills(cls, value: list[StudentSkillInput]) -> list[StudentSkillInput]:
        names = [skill.name.casefold() for skill in value]
        if len(names) != len(set(names)):
            raise ValueError("Each skill may only appear once")
        return value


class StudentCreate(StudentProfileInput):
    pass


class StudentUpdate(StudentProfileInput):
    pass


class StudentRead(StudentFields):
    id: int
    skills: list[StudentSkillRead] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)