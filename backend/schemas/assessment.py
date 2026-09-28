"""Request and response schemas for the skill self-assessment."""

from datetime import datetime

from pydantic import BaseModel, Field, model_validator


class AssessmentOption(BaseModel):
    label: str
    proficiency: float = Field(ge=0.0, le=1.0)


class AssessmentQuestionRead(BaseModel):
    id: int
    prompt: str
    skill_name: str
    options: list[AssessmentOption]


class AssessmentAnswer(BaseModel):
    question_id: int = Field(gt=0)
    proficiency: float = Field(ge=0.0, le=1.0)


class AssessmentSubmission(BaseModel):
    student_id: int = Field(gt=0)
    answers: list[AssessmentAnswer] = Field(min_length=1, max_length=50)

    @model_validator(mode="after")
    def validate_unique_questions(self) -> "AssessmentSubmission":
        question_ids = [answer.question_id for answer in self.answers]
        if len(question_ids) != len(set(question_ids)):
            raise ValueError("Each assessment question must be answered once")
        return self


class AssessmentResultRead(BaseModel):
    id: int
    score: float
    skills_updated: list[str]
    completed_at: datetime | None