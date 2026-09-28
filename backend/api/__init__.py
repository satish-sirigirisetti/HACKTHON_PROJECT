"""API router registration."""

from fastapi import APIRouter

from backend.api.assessment import router as assessment_router
from backend.api.assistant import router as assistant_router
from backend.api.careers import router as careers_router
from backend.api.certifications import router as certifications_router
from backend.api.comparison import router as comparison_router
from backend.api.internships import router as internships_router
from backend.api.projects import router as projects_router
from backend.api.recommendations import router as recommendations_router
from backend.api.roadmap import router as roadmap_router
from backend.api.simulator import router as simulator_router
from backend.api.skills import router as skills_router
from backend.api.skill_gaps import router as skill_gaps_router
from backend.api.students import router as students_router
from backend.api.trends import router as trends_router

api_router = APIRouter()
for router in (
	students_router,
	careers_router,
	recommendations_router,
	assessment_router,
	skill_gaps_router,
	roadmap_router,
	projects_router,
	certifications_router,
	internships_router,
	trends_router,
	comparison_router,
	simulator_router,
	skills_router,
	assistant_router,
):
	api_router.include_router(router)