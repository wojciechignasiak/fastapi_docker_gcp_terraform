#3rd party modules
from pydantic import BaseModel

class AppSettingsInformationModel(BaseModel):
    environment: str
    project_id: str
