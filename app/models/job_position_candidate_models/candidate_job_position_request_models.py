#1st party libraries
from uuid import UUID

#3rd party libraries
from pydantic import BaseModel


class AssignCandidateToJobPositionRequestModel(BaseModel):
    job_position_id: UUID
    candidate_id: UUID

class UnassignCandidateFromJobPositionRequestModel(AssignCandidateToJobPositionRequestModel):
    pass
