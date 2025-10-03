#3rd party libraries
from pydantic import BaseModel

class CreateCandidateRequestModel(BaseModel):
    first_name: str
    last_name: str

