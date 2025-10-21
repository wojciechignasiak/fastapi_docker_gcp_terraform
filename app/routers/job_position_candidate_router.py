#internal modules
from app.services.job_position_candidate_service import IJobPositionCandidateService, new_job_position_candidate_service
from app.models.job_position_candidate_models.candidate_job_position_request_models import AssignCandidateToJobPositionRequestModel, UnassignCandidateFromJobPositionRequestModel
from app.models.job_position_candidate_models.candidate_job_position_response_models import JobPositionCandidatesResponseModel, CandidateJobPositionsResponseModel

#3rd party libraries
from fastapi import APIRouter, status, Depends

#1st party libraries
from uuid import UUID
import logging


logger: logging.Logger = logging.getLogger(__name__)
router: APIRouter = APIRouter()

@router.patch("/assign-candidate-to-job-position/", status_code=status.HTTP_200_OK)
async def assign_candidate_to_job_position(
    candidate_to_job_position: AssignCandidateToJobPositionRequestModel,
    job_position_candidate_service: IJobPositionCandidateService = Depends(new_job_position_candidate_service),
):
    await job_position_candidate_service.assign_candidate_to_job_position(candidate_to_job_position)


@router.patch("/unassign-candidate-from-job-position/", status_code=status.HTTP_200_OK)
async def unassign_candidate_from_job_position(
    candidate_from_job_position: UnassignCandidateFromJobPositionRequestModel,
    job_position_candidate_service: IJobPositionCandidateService = Depends(new_job_position_candidate_service),
):
    await job_position_candidate_service.unassign_candidate_from_job_position(candidate_from_job_position)

@router.get("/get-job-position-candidates/", response_model=JobPositionCandidatesResponseModel)
async def get_job_position_candidates(
    job_position_id: UUID,
    job_position_candidate_service: IJobPositionCandidateService = Depends(new_job_position_candidate_service),
):
    job_position_candidates: JobPositionCandidatesResponseModel = await job_position_candidate_service.get_job_position_candidates(job_position_id)
    return job_position_candidates


@router.get("/get-candidate-job-positions/", response_model=CandidateJobPositionsResponseModel)
async def get_candidate_job_positions(
    candidate_id: UUID,
    job_position_candidate_service: IJobPositionCandidateService = Depends(new_job_position_candidate_service),
):
    candidate_job_positions: CandidateJobPositionsResponseModel = await job_position_candidate_service.get_candidate_job_positions(candidate_id)
    return candidate_job_positions
