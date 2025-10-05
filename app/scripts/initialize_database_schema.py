#internal modules
from app.models.app_config_models.database_credentials_model import DatabaseCredentials
from app.database.schema.candidate_schema import CandidateSchema
from app.database.schema.job_position_schema import JobPositionSchema
from app.database.schema.candidate_job_position_schema import JobPositionCandidateSchema
from app.secret_manager.secret_manager import ISecretManager, new_secret_manager

#3rd party libraries
from sqlmodel import SQLModel, create_engine

#1st party libraries
from urllib.parse import quote_plus

def init_db(database_credentials: DatabaseCredentials):
    database_url = f"postgresql://{
    quote_plus(database_credentials.username)
    }:{
    quote_plus(database_credentials.password)
    }@{
    database_credentials.host
    }:{
    database_credentials.port
    }/{
    database_credentials.database
    }"
    engine = create_engine(database_url, echo=True)
    SQLModel.metadata.create_all(engine, tables=[CandidateSchema.__table__, JobPositionSchema.__table__, JobPositionCandidateSchema.__table__])

if __name__ == "__main__":
    secret_manager: ISecretManager = new_secret_manager()
    database_credentials: DatabaseCredentials = secret_manager.get_database_credentials()
    init_db(database_credentials)