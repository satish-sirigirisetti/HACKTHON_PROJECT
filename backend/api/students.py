"""Student profile endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.database.database import get_db
from backend.schemas.student import StudentCreate, StudentRead, StudentUpdate
from backend.services.student_service import (
    DuplicateStudentEmailError,
    create_student,
    get_student,
    update_student,
)

router = APIRouter(prefix="/students", tags=["students"])


@router.post("", response_model=StudentRead, status_code=status.HTTP_201_CREATED)
def create_student_profile(payload: StudentCreate, session: Session = Depends(get_db)) -> StudentRead:
    try:
        return create_student(session, payload)
    except DuplicateStudentEmailError as error:
        raise HTTPException(status_code=409, detail="A student with this email already exists") from error


@router.get("/{student_id}", response_model=StudentRead)
def read_student_profile(student_id: int, session: Session = Depends(get_db)) -> StudentRead:
    student = get_student(session, student_id)
    if student is None:
        raise HTTPException(status_code=404, detail="Student not found")
    return student


@router.put("/{student_id}", response_model=StudentRead)
def replace_student_profile(
    student_id: int, payload: StudentUpdate, session: Session = Depends(get_db)
) -> StudentRead:
    try:
        student = update_student(session, student_id, payload)
    except DuplicateStudentEmailError as error:
        raise HTTPException(status_code=409, detail="A student with this email already exists") from error
    if student is None:
        raise HTTPException(status_code=404, detail="Student not found")
    return student