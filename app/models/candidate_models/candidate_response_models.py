#1st party libraries
from uuid import UUID

#3rd party libraries
from pydantic import BaseModel


class CandidateResponseModel(BaseModel):
    id: UUID
    first_name: str
    last_name: str

class GetAllCandidatesResponseModel(BaseModel):
    page_size: int
    page: int
    last_page: int
    total_number_of_entities: int
    entities: list[CandidateResponseModel]