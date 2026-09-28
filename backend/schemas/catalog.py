"""Read schemas for structured project, learning, and trend catalogs."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ProjectRead(BaseModel):
    id: int
    title: str
    description: str
    skill_names: list[str]
    source_url: str | None = None

    model_config = ConfigDict(from_attributes=True)


class CertificationRead(BaseModel):
    id: int
    name: str
    provider: str
    description: str
    skills: list[str]
    url: str | None = None

    model_config = ConfigDict(from_attributes=True)


class InternshipRead(BaseModel):
    id: int
    title: str
    organization: str
    description: str
    skills: list[str]
    source_url: str | None = None
    is_sample: bool = True

    model_config = ConfigDict(from_attributes=True)


class LearningResourceRead(BaseModel):
    id: int
    title: str
    provider: str
    resource_type: str
    skill_name: str
    url: str | None = None

    model_config = ConfigDict(from_attributes=True)


class IndustryTrendRead(BaseModel):
    id: int
    topic: str
    summary: str
    source: str
    observed_at: datetime | None = None
    is_sample: bool

    model_config = ConfigDict(from_attributes=True)


class SkillRead(BaseModel):
    id: int
    name: str
    category: str
    description: str | None = None

    model_config = ConfigDict(from_attributes=True)