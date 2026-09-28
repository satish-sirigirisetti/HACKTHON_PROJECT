"""Career assistant request and grounded response schemas."""

from typing import Literal

from pydantic import BaseModel, Field


class AssistantQuestion(BaseModel):
    student_id: int = Field(gt=0)
    message: str = Field(min_length=1, max_length=4000)


class AssistantSource(BaseModel):
    title: str
    source_type: str
    excerpt: str
    url: str | None = None


class AssistantAnswer(BaseModel):
    answer: str
    sources: list[AssistantSource]
    generation_status: Literal["generated", "retrieval_only"]
    retrieval_method: str