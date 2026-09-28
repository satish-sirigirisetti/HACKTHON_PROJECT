"""Skill-gap and learning-roadmap request/response schemas."""

from datetime import datetime

from pydantic import BaseModel, Field


class SkillGapResource(BaseModel):
    title: str
    provider: str
    resource_type: str
    url: str | None = None


class SkillGapItem(BaseModel):
    skill_id: int
    skill_name: str
    proficiency: float = Field(ge=0.0, le=1.0)
    importance: float = Field(ge=0.0)
    priority: float = Field(ge=0.0)
    resources: list[SkillGapResource] = Field(default_factory=list)


class SkillGapRead(BaseModel):
    student_id: int
    career_id: int
    career_name: str
    gaps: list[SkillGapItem]


class RoadmapCreate(BaseModel):
    career_id: int = Field(gt=0)


class RoadmapItemUpdate(BaseModel):
    completed: bool


class RoadmapItemRead(BaseModel):
    id: int
    title: str
    description: str
    position: int = Field(ge=0)
    completed: bool = False
    resource: SkillGapResource | None = None


class RoadmapRead(BaseModel):
    id: int
    title: str
    target_role: str
    created_at: datetime | None
    items: list[RoadmapItemRead] = Field(default_factory=list)