#3rd party modules
from pydantic import BaseModel

class DatabaseCredentials(BaseModel):
    database: str
    username: str
    password: str
    host: str
    port: str

