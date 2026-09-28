"""Non-persistent what-if career simulation endpoint."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.database.database import get_db
from backend.schemas.simulator import SimulationRead, SimulationRequest
from backend.services.simulator_service import simulate_careers

router = APIRouter(prefix="/simulator", tags=["simulator"])


@router.post("/{student_id}", response_model=SimulationRead)
def run_simulation(
	student_id: int,
	payload: SimulationRequest,
	session: Session = Depends(get_db),
) -> SimulationRead:
	try:
		return simulate_careers(session, student_id, payload)
	except LookupError as error:
		raise HTTPException(status_code=404, detail=str(error)) from error