#internal modules
from app.services.job_position_service import IJobPositionService, new_job_position_service
from app.models.job_position_models.job_position_request_models import CreateJobPositionRequestModel
from app.models.job_position_models.job_position_response_models import JobPositionResponseModel
from app.custom_exceptions.custom_exceptions import CustomException

#3rd party libraries
from fastapi import APIRouter, HTTPException, status, Depends

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
    try:
        job_position: JobPositionResponseModel = await job_position_service.create_job_position(job_position)
        return job_position
    except CustomException as e:
        if e.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")
        else:
            raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        logger.error(f"Unexpected error occurred while creating job position: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")


@router.get("/get-job-position/", response_model=JobPositionResponseModel, status_code=status.HTTP_200_OK)
async def get_job_position(
        job_position_id: UUID,
        job_position_service: IJobPositionService = Depends(new_job_position_service),
):
    try:
        job_position: JobPositionResponseModel = await job_position_service.get_job_position_by_id(job_position_id)
        return job_position
    except CustomException as e:
        if e.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")
        else:
            raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        logger.error(f"Unexpected error occurred while getting job position: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")


@router.get("/get-all-job-positions/", response_model=list[JobPositionResponseModel], status_code=status.HTTP_200_OK)
async def get_all_job_positions(
        job_position_service: IJobPositionService = Depends(new_job_position_service),
):
    try:
        candidates: list[JobPositionResponseModel] = await job_position_service.get_all_job_positions()
        return candidates
    except CustomException as e:
        if e.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")
        else:
            raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        logger.error(f"Unexpected error occurred while getting all job positions: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")
