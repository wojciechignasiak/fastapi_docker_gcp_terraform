#internal modules
from app.models.job_position_models.job_position_response_models import JobPositionResponseModel
from app.models.candidate_models.candidate_response_models import CandidateResponseModel

#3rd party libraries
from pydantic import BaseModel


class JobPositionCandidatesResponseModel(BaseModel):
    job_position: JobPositionResponseModel
    candidates: list[CandidateResponseModel]

class CandidateJobPositionsResponseModel(BaseModel):
    candidate: CandidateResponseModel
    job_positions: list[JobPositionResponseModel]

