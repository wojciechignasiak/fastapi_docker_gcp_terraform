#internal modules
from app.services.candidate_service import ICandidateService, new_candidate_service
from app.models.candidate_models.candidate_response_models import CandidateResponseModel, GetAllCandidatesResponseModel
from app.models.candidate_models.candidate_request_models import CreateCandidateRequestModel, GetAllCandidatesRequestModel

#3rd party libraries
from fastapi import APIRouter, status, Depends

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
    candidate: CandidateResponseModel = await candidate_service.create_candidate(candidate)
    return candidate


@router.get("/get-candidate/", response_model=CandidateResponseModel, status_code=status.HTTP_200_OK)
async def get_candidate(
    candidate_id: UUID,
    candidate_service: ICandidateService = Depends(new_candidate_service),
    ):
    candidate: CandidateResponseModel = await candidate_service.get_candidate_by_id(candidate_id)
    return candidate

@router.post("/get-all-candidates/", response_model=GetAllCandidatesResponseModel, status_code=status.HTTP_200_OK)
async def get_all_candidates(
    pagination: GetAllCandidatesRequestModel,
    candidate_service: ICandidateService = Depends(new_candidate_service),
    ):
    candidates: GetAllCandidatesResponseModel = await candidate_service.get_all_candidates(pagination)
    return candidates
