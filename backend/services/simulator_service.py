"""Evaluate hypothetical skills without changing stored profile data."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.database.models import Skill, Student, StudentSkill
from backend.schemas.simulator import CareerScenarioChange, SimulationRead, SimulationRequest
from backend.services.recommendation_service import recommend_careers_for_skills


def simulate_careers(
	session: Session, student_id: int, request: SimulationRequest
) -> SimulationRead:
	student = session.get(Student, student_id)
	if student is None:
		raise LookupError("Student not found")

	current = dict(
		session.execute(
			select(Skill.name, StudentSkill.proficiency)
			.join(StudentSkill, StudentSkill.skill_id == Skill.id)
			.where(StudentSkill.student_id == student_id)
		).all()
	)
	simulated = dict(current)
	for skill in request.skills:
		simulated[skill.name] = skill.proficiency

	baseline_results = recommend_careers_for_skills(session, current)
	simulated_results = recommend_careers_for_skills(session, simulated)
	baseline_ranks = {career.career_id: index for index, career in enumerate(baseline_results)}
	baseline_scores = {career.career_id: career.match_score for career in baseline_results}
	changes = [
		CareerScenarioChange(
			career_id=career.career_id,
			career_name=career.career_name,
			current_score=baseline_scores.get(career.career_id, 0.0),
			simulated_score=career.match_score,
			rank_change=baseline_ranks.get(career.career_id, len(baseline_ranks)) - index,
		)
		for index, career in enumerate(simulated_results)
	]
	return SimulationRead(
		method="Scenario only; hypothetical skills are not saved to the student profile.",
		baseline=baseline_results,
		simulated=simulated_results,
		changes=changes,
	)