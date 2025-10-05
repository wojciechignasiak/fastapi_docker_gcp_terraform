#internal modules
from app.database.session.get_session import get_session
from app.database.schema.candidate_job_position_schema import JobPositionCandidateSchema
from app.custom_exceptions.custom_exceptions import DatabaseError

#3rd party modules
from sqlalchemy import insert, select, delete, Insert, Select, Delete
from sqlalchemy.engine import Result, ScalarResult
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends

#1st party modules
from typing import Protocol
from uuid import UUID
import logging


logger: logging.Logger = logging.getLogger(__name__)

class IJobPositionCandidateRepository(Protocol):

    async def assign_candidate_to_job_position(self, candidate_id: UUID, job_position_id: UUID) -> None:
        ...

    async def unassign_candidate_from_job_position(self, candidate_id: UUID, job_position_id: UUID) -> None:
        ...

    async def get_candidates_ids_by_job_position_id(self, job_position_id: UUID) -> tuple[UUID, ...]:
        ...

    async def get_job_positions_ids_by_candidate_id(self, candidate_id: UUID) -> tuple[UUID, ...]:
        ...

def new_job_position_candidate_repository(session: AsyncSession = Depends(get_session)) -> IJobPositionCandidateRepository:
    try:
        return JobPositionCandidateRepository(session)
    except Exception as e:
        logger.error(f"Unexpected error occurred while creating new job position candidate repository: {e}")
        raise DatabaseError(
            status_code=500,
        )

class JobPositionCandidateRepository(IJobPositionCandidateRepository):
    __slots__ = '_session'
    def __init__(self, session: AsyncSession) -> None:
        self._session: AsyncSession = session

    async def assign_candidate_to_job_position(self, candidate_id: UUID, job_position_id: UUID) -> None:
        try:
            statement: Insert = insert(JobPositionCandidateSchema).values(
                candidate_id=candidate_id,
                job_position_id=job_position_id
            )
            await self._session.execute(statement)
        except Exception as e:
            logger.error(f"Unexpected error occurred while assigning candidate to job position: {e}")
            raise DatabaseError(
                status_code=500,
            )

    async def unassign_candidate_from_job_position(self, candidate_id: UUID, job_position_id: UUID) -> None:
        try:
            statement: Delete = delete(JobPositionCandidateSchema).where(
                (JobPositionCandidateSchema.candidate_id == candidate_id) &  # type: ignore[arg-type]
                (JobPositionCandidateSchema.job_position_id == job_position_id)  # type: ignore[arg-type]
            )
            await self._session.execute(statement)
        except Exception as e:
            logger.error(f"Unexpected error occurred while unassigning candidate from job position: {e}")
            raise DatabaseError(
                status_code=500,
            )

    async def get_all_job_positions_and_candidates_ids(self) -> tuple[JobPositionCandidateSchema, ...] | tuple:
        try:
            statement: Select[tuple[JobPositionCandidateSchema]] = select(JobPositionCandidateSchema)
            result: Result[tuple[JobPositionCandidateSchema]] = await self._session.execute(statement)
            relations: ScalarResult[JobPositionCandidateSchema] = result.scalars()
            return tuple(relations.all())
        except Exception as e:
            logger.error(f"Unexpected error occurred while getting all job position and candidates ids: {e}")
            raise DatabaseError(
                status_code=500,
            )

    async def get_candidates_ids_by_job_position_id(self, job_position_id: UUID) -> tuple[UUID, ...] | tuple:
        try:
            statement: Select[tuple[JobPositionCandidateSchema]] = select(JobPositionCandidateSchema).where(
                JobPositionCandidateSchema.job_position_id == job_position_id  # type: ignore[arg-type]
            )
            result: Result[tuple[JobPositionCandidateSchema]] = await self._session.execute(statement)
            relations: ScalarResult[JobPositionCandidateSchema] = result.scalars()
            candidate_ids: tuple[UUID, ...] | tuple = tuple(relation.candidate_id for relation in relations.all())
            return candidate_ids
        except Exception as e:
            logger.error(f"Unexpected error occurred while getting candidates ids by job position id: {e}")
            raise DatabaseError(
                status_code=500,
            )

    async def get_job_positions_ids_by_candidate_id(self, candidate_id: UUID) -> tuple[UUID, ...] | tuple:
        try:
            statement: Select[tuple[JobPositionCandidateSchema]] = select(JobPositionCandidateSchema).where(
                JobPositionCandidateSchema.candidate_id == candidate_id  # type: ignore[arg-type]
            )
            result: Result[tuple[JobPositionCandidateSchema]] = await self._session.execute(statement)
            relations: ScalarResult[JobPositionCandidateSchema] = result.scalars()
            job_position_ids: tuple[UUID, ...]  | tuple= tuple(relation.job_position_id for relation in relations.all())
            return job_position_ids
        except Exception as e:
            logger.error(f"Unexpected error occurred while getting job positions ids by candidate id: {e}")
            raise DatabaseError(
                status_code=500,
            )