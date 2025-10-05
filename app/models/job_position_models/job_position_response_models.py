#1st party libraries
from uuid import UUID

#3rd party libraries
from pydantic import BaseModel

class JobPositionResponseModel(BaseModel):
    id: UUID
    name: str

class GetAllJobPositionsResponseModel(BaseModel):
    page_size: int
    page: int
    total_number_of_entities: int
    last_page: int
    entities: list[JobPositionResponseModel]