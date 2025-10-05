#internal modules
from app.services.candidate_service import ICandidateService, new_candidate_service
from app.models.candidate_models.candidate_response_models import CandidateResponseModel, GetAllCandidatesResponseModel
from app.models.candidate_models.candidate_request_models import CreateCandidateRequestModel, GetAllCandidatesRequestModel
from app.custom_exceptions.custom_exceptions import CustomException

#3rd party libraries
from fastapi import APIRouter, HTTPException, status, Depends

#1st party libraries
from uuid import UUID
import logging


logger: logging.Logger = logging.getLogger(__name__)
router: APIRouter = APIRouter()

@router.post("/create-candidate/", response_model=CandidateResponseModel, status_code=status.HTTP_201_CREATED)
async def create_candidate(
    candidate: CreateCandidateRequestModel,
    candidate_service: ICandidateService = Depends(new_candidate_service),
    ):
    try:
        candidate: CandidateResponseModel = await candidate_service.create_candidate(candidate)
        return candidate
    except CustomException as e:
        if e.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")
        else:
            raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        logger.error(f"Unexpected error occurred while creating candidate: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")


@router.get("/get-candidate/", response_model=CandidateResponseModel, status_code=status.HTTP_200_OK)
async def get_candidate(
    candidate_id: UUID,
    candidate_service: ICandidateService = Depends(new_candidate_service),
    ):
    try:
        candidate: CandidateResponseModel = await candidate_service.get_candidate_by_id(candidate_id)
        return candidate
    except CustomException as e:
        if e.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")
        else:
            raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        logger.error(f"Unexpected error occurred while creating getting candidate: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")

@router.post("/get-all-candidates/", response_model=GetAllCandidatesResponseModel, status_code=status.HTTP_200_OK)
async def get_all_candidates(
    pagination: GetAllCandidatesRequestModel,
    candidate_service: ICandidateService = Depends(new_candidate_service),
    ):
    try:
        candidates: GetAllCandidatesResponseModel = await candidate_service.get_all_candidates(pagination)
        return candidates
    except CustomException as e:
        if e.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")
        else:
            raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        logger.error(f"Unexpected error occurred while getting candidates: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")