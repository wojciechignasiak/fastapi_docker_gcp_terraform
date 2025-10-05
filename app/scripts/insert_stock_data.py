#internal modules
from app.models.app_config_models.database_credentials_model import DatabaseCredentials
from app.database.connection.create_engine import create_engine
from app.database.schema.candidate_schema import CandidateSchema
from app.database.schema.job_position_schema import JobPositionSchema
from app.database.schema.candidate_job_position_schema import JobPositionCandidateSchema
from app.secret_manager.secret_manager import ISecretManager, new_secret_manager
from app.database.repositories.candidate_repository import ICandidateRepository, new_candidate_repository
from app.database.repositories.job_position_repository import IJobPositionRepository, new_job_position_repository, \
    JobPositionRepository
from app.database.repositories.job_position_candidate_repository import IJobPositionCandidateRepository, new_job_position_candidate_repository

#3rd party libraries
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker
from sqlalchemy import  text

#1st party libraries
from uuid import UUID
import asyncio

def create_candidates_schema(candidate_first_name: str, candidate_last_name: str) -> CandidateSchema:
    return CandidateSchema(
        first_name=candidate_first_name,
        last_name=candidate_last_name,
    )

def create_job_position_schema(job_position_name: str) -> JobPositionSchema:
    return JobPositionSchema(
        name=job_position_name,
    )

async def insert_stock_data(
    session_maker: async_sessionmaker[AsyncSession],
    candidates_schemas: list[CandidateSchema],
    job_positions_schemas: list[JobPositionSchema],
):
    async with session_maker() as session:
        candidate_repository: ICandidateRepository = new_candidate_repository(session)
        job_position_repository: IJobPositionRepository = new_job_position_repository(session)
        job_position_candidate_repository: IJobPositionCandidateRepository = new_job_position_candidate_repository(session)

        for candidate_schema in candidates_schemas:
            await candidate_repository.create_candidate(candidate_schema)
        await session.flush()

        for job_position_schema in job_positions_schemas:
            await job_position_repository.create_job_position(job_position_schema)
        await session.flush()
        for candidate_schema, job_position_schema in zip(candidates_schemas, job_positions_schemas):
            await job_position_candidate_repository.assign_candidate_to_job_position(
                candidate_schema.id,
                job_position_schema.id
            )
        await session.commit()




if __name__ == "__main__":
    secret_manager: ISecretManager = new_secret_manager()
    database_credentials: DatabaseCredentials = secret_manager.get_database_credentials()
    engine: AsyncEngine = create_engine(database_credentials)
    new_session_maker: async_sessionmaker[AsyncSession] = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=True
    )
    candidates: list[dict[str, str]] = [
        {"first_name": "Wojciech", "last_name": "Ignasiak"},
        {"first_name": "Adam", "last_name": "Nowak"},
        {"first_name": "Jan", "last_name": "Kowalski"}
    ]
    job_positions: list[dict[str, str]] = [
        {"name": "Python Developer"},
        {"name": "Golang Developer"},
        {"name": "Java Developer"},
    ]

    candidates_schemas: list[CandidateSchema] = [
        create_candidates_schema(
            candidate["first_name"],
            candidate["last_name"],
        ) for candidate in candidates
    ]

    job_positions_schemas: list[JobPositionSchema] = [
        create_job_position_schema(
            job_position["name"],
        ) for job_position in job_positions
    ]


    asyncio.run(
        insert_stock_data(
            new_session_maker,
            candidates_schemas,
            job_positions_schemas,
        )
    )