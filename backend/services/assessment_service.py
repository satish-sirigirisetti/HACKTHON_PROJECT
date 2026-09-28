"""Self-reported skill assessment retrieval and persistence."""

from statistics import mean

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.database.models import (
	Assessment,
	AssessmentQuestion,
	AssessmentResult,
	Skill,
	Student,
	StudentSkill,
)
from backend.schemas.assessment import (
	AssessmentQuestionRead,
	AssessmentResultRead,
	AssessmentSubmission,
)

ASSESSMENT_TITLE = "Career foundations skill self-assessment"


class AssessmentNotFoundError(Exception):
	"""Raised when the seeded assessment is unavailable."""


class IncompleteAssessmentError(Exception):
	"""Raised when a submission omits one or more assessment questions."""


class InvalidAssessmentAnswerError(Exception):
	"""Raised when a rating is not one of the question's offered options."""


def get_assessment_questions(session: Session) -> list[AssessmentQuestionRead]:
	"""Return the seeded questions and their linked canonical skills."""
	assessment = session.scalar(select(Assessment).where(Assessment.title == ASSESSMENT_TITLE))
	if assessment is None:
		return []
	rows = session.execute(
		select(AssessmentQuestion, Skill.name)
		.join(Skill, Skill.id == AssessmentQuestion.skill_id)
		.where(AssessmentQuestion.assessment_id == assessment.id)
		.order_by(AssessmentQuestion.id)
	).all()
	return [
		AssessmentQuestionRead(
			id=question.id,
			prompt=question.prompt,
			skill_name=skill_name,
			options=question.options,
		)
		for question, skill_name in rows
	]


def submit_assessment(
	session: Session, submission: AssessmentSubmission
) -> AssessmentResultRead:
	"""Persist self-ratings and update the student's current skill profile."""
	student = session.get(Student, submission.student_id)
	if student is None:
		raise LookupError("Student not found")

	assessment = session.scalar(select(Assessment).where(Assessment.title == ASSESSMENT_TITLE))
	if assessment is None:
		raise AssessmentNotFoundError

	questions = list(
		session.scalars(
			select(AssessmentQuestion)
			.where(AssessmentQuestion.assessment_id == assessment.id)
			.order_by(AssessmentQuestion.id)
		)
	)
	if not questions:
		raise AssessmentNotFoundError

	answers = {answer.question_id: answer.proficiency for answer in submission.answers}
	expected_ids = {question.id for question in questions}
	if set(answers) != expected_ids:
		raise IncompleteAssessmentError

	for question in questions:
		allowed_values = {option["proficiency"] for option in question.options}
		if answers[question.id] not in allowed_values:
			raise InvalidAssessmentAnswerError

	answer_details: list[dict[str, object]] = []
	skills_updated: list[str] = []
	for question in questions:
		if question.skill_id is None:
			continue
		skill = session.get(Skill, question.skill_id)
		if skill is None:
			continue
		proficiency = answers[question.id]
		student_skill = session.scalar(
			select(StudentSkill).where(
				StudentSkill.student_id == student.id,
				StudentSkill.skill_id == skill.id,
			)
		)
		if student_skill is None:
			student_skill = StudentSkill(
				student_id=student.id,
				skill_id=skill.id,
				proficiency=proficiency,
			)
			session.add(student_skill)
		else:
			student_skill.proficiency = proficiency
		skills_updated.append(skill.name)
		answer_details.append(
			{"question_id": question.id, "skill": skill.name, "proficiency": proficiency}
		)

	result = AssessmentResult(
		student_id=student.id,
		assessment_id=assessment.id,
		score=mean(answers.values()),
		details={"source": "self_report", "answers": answer_details},
	)
	session.add(result)
	session.commit()
	session.refresh(result)
	return AssessmentResultRead(
		id=result.id,
		score=result.score,
		skills_updated=skills_updated,
		completed_at=result.completed_at,
	)