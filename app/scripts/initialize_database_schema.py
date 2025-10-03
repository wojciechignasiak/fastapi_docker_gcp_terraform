
from app.models.app_config_models.database_credentials_model import DatabaseCredentials
from app.database.schema.candidate_schema import CandidateSchema
from app.database.schema.job_position_schema import JobPositionSchema
from app.database.schema.candidate_job_position_schema import JobPositionCandidateSchema
#3rd party libraries
from sqlmodel import SQLModel, create_engine

#1st party libraries
import os





def init_db():
    database_credentials: DatabaseCredentials = DatabaseCredentials(
        database=os.environ.get("POSTGRES_DATABASE"),
        username=os.environ.get("POSTGRES_USERNAME"),
        password=os.environ.get("POSTGRES_PASSWORD"),
        host=os.environ.get("POSTGRES_HOST"),
        port=str(os.environ.get("POSTGRES_PORT"))
    )
    DATABASE_URL = f"postgresql://{
    database_credentials.username
    }:{
    database_credentials.password
    }@{
    database_credentials.host
    }:{
    database_credentials.port
    }/{
    database_credentials.database
    }"
    engine = create_engine(DATABASE_URL, echo=True)
    SQLModel.metadata.create_all(engine, tables=[CandidateSchema.__table__, JobPositionSchema.__table__, JobPositionCandidateSchema.__table__])

# Wywołaj przy starcie aplikacji
if __name__ == "__main__":
    init_db()