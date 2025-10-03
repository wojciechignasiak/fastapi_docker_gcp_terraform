#3rd party libraries
from pydantic import BaseModel

class CreateJobPositionRequestModel(BaseModel):
    name: str



