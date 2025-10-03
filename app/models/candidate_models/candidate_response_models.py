#1st party libraries
from uuid import UUID

#3rd party libraries
from pydantic import BaseModel


class CandidateResponseModel(BaseModel):
    id: UUID
    first_name: str
    last_name: str