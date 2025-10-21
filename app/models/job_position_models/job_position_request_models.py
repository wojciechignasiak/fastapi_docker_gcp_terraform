#3rd party libraries
from pydantic import BaseModel, Field, field_validator

class CreateJobPositionRequestModel(BaseModel):
    name: str = Field(..., min_length=1)

    @field_validator("name", mode="after")
    def normalize_names(cls, value: str) -> str:
        return value.strip().title()

class GetAllJobPositionsRequestModel(BaseModel):
    page_size: int = Field(50, ge=1, le=100)
    page: int = Field(1, ge=1)