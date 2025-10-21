#internal modules
from app.services.job_position_service import IJobPositionService, new_job_position_service
from app.models.job_position_models.job_position_request_models import CreateJobPositionRequestModel, GetAllJobPositionsRequestModel
from app.models.job_position_models.job_position_response_models import JobPositionResponseModel, GetAllJobPositionsResponseModel

#3rd party libraries
from fastapi import APIRouter, status, Depends

#1st party libraries
from uuid import UUID
import logging

logger: logging.Logger = logging.getLogger(__name__)
router: APIRouter = APIRouter()


@router.post("/create-job-position/", response_model=JobPositionResponseModel, status_code=status.HTTP_201_CREATED)
async def create_job_position(
        job_position: CreateJobPositionRequestModel,
        job_position_service: IJobPositionService = Depends(new_job_position_service),
):
    job_position: JobPositionResponseModel = await job_position_service.create_job_position(job_position)
    return job_position


@router.get("/get-job-position/", response_model=JobPositionResponseModel, status_code=status.HTTP_200_OK)
async def get_job_position(
        job_position_id: UUID,
        job_position_service: IJobPositionService = Depends(new_job_position_service),
):
    job_position: JobPositionResponseModel = await job_position_service.get_job_position_by_id(job_position_id)
    return job_position


@router.post("/get-all-job-positions/", response_model=GetAllJobPositionsResponseModel, status_code=status.HTTP_200_OK)
async def get_all_job_positions(
        pagination: GetAllJobPositionsRequestModel,
        job_position_service: IJobPositionService = Depends(new_job_position_service),
):
    candidates: GetAllJobPositionsResponseModel = await job_position_service.get_all_job_positions(pagination)
    return candidates
