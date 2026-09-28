"""Student profile persistence and lookup."""

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from backend.database.models import Skill, Student, StudentSkill
from backend.schemas.student import StudentCreate, StudentUpdate


class DuplicateStudentEmailError(Exception):
    """Raised when a profile email is already registered."""


def create_student(session: Session, payload: StudentCreate) -> Student:
    values = payload.model_dump(exclude={"skills"})
    student = Student(**values)
    session.add(student)
    try:
        session.flush()
        _replace_student_skills(session, student, payload)
        session.commit()
    except IntegrityError as error:
        session.rollback()
        raise DuplicateStudentEmailError from error
    session.refresh(student)
    return student


def get_student(session: Session, student_id: int) -> Student | None:
    return session.get(Student, student_id)


def update_student(session: Session, student_id: int, payload: StudentUpdate) -> Student | None:
    student = session.get(Student, student_id)
    if student is None:
        return None
    values = payload.model_dump(exclude={"skills"})
    for field, value in values.items():
        setattr(student, field, value)
    try:
        _replace_student_skills(session, student, payload)
        session.commit()
    except IntegrityError as error:
        session.rollback()
        raise DuplicateStudentEmailError from error
    session.refresh(student)
    return student


def _replace_student_skills(session: Session, student: Student, payload: StudentUpdate | StudentCreate) -> None:
    student.skills.clear()
    for item in payload.skills:
        skill = session.scalar(select(Skill).where(func.lower(Skill.name) == item.name.lower()))
        if skill is None:
            skill = Skill(name=item.name, category="technical")
            session.add(skill)
            session.flush()
        student.skills.append(StudentSkill(skill=skill, proficiency=item.proficiency))