#3rd party libraries
from pydantic import BaseModel, Field, field_validator

class CreateCandidateRequestModel(BaseModel):
    first_name: str = Field(..., min_length=1)
    last_name: str = Field(..., min_length=1)

    @field_validator("first_name", "last_name", mode="after")
    def capitalize_names(cls, value: str) -> str:
        return value.strip().title()

class GetAllCandidatesRequestModel(BaseModel):
    page_size: int = Field(50, ge=1, le=100)
    page: int = Field(1, ge=1)