#internal modules
from app.database.session.get_session import get_session
from app.database.schema.job_position_schema import JobPositionSchema
from app.custom_exceptions.custom_exceptions import DatabaseError

#3rd party libraries
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, Result, func
from fastapi import Depends

#1st party libraries
from typing import Protocol
from uuid import UUID
import logging


logger: logging.Logger = logging.getLogger(__name__)

class IJobPositionRepository(Protocol):

    async def create_job_position(self, job_position: JobPositionSchema) -> None:
        ...

    async def get_multiple_job_positions_by_id(self, job_positions_ids: tuple[UUID, ...]) -> tuple[JobPositionSchema, ...] | tuple:
        ...

    async def count_number_of_all_job_positions(self) -> int:
        ...

    async def get_all_job_positions(self, page_size: int, page: int) -> tuple[JobPositionSchema, ...] | tuple:
        ...

    async def get_job_position_by_id(self, job_position_id: UUID) -> JobPositionSchema | None:
        ...

    async def delete_job_position_by_id(self, job_position_id: UUID) -> None:
        ...

def new_job_position_repository(session: AsyncSession = Depends(get_session)) -> IJobPositionRepository:
    try:
        return JobPositionRepository(session)
    except Exception as e:
        logger.error(f"Unexpected error occurred while creating new job position repository: {e}")
        raise DatabaseError(
            status_code=500,
        )

class JobPositionRepository(IJobPositionRepository):
    __slots__ = 'session'
    def __init__(self, session: AsyncSession) -> None:
        self.session: AsyncSession = session

    async def create_job_position(self, job_position: JobPositionSchema) -> None:
        try:
            self.session.add(job_position)
        except Exception as e:
            logger.error(f"Unexpected error occurred while creating new job position: {e}")
            raise DatabaseError(
                status_code=500,
            )

    async def get_multiple_job_positions_by_id(self, job_positions_ids: tuple[UUID, ...]) -> tuple[JobPositionSchema, ...] | tuple:
        try:
            statement = select(JobPositionSchema).where(JobPositionSchema.id.in_(job_positions_ids))
            result: Result = await self.session.execute(statement)
            job_positions = result.scalars().all()
            return tuple(job_positions)
        except Exception as e:
            logger.error(f"Unexpected error occurred while getting candidates: {e}")
            raise DatabaseError(
                status_code=500,
            )

    async def count_number_of_all_job_positions(self) -> int:
        try:
            statement = select(func.count()).select_from(JobPositionSchema)
            total_result: Result = await self.session.execute(statement)
            total_count: int = total_result.scalar_one()
            return total_count
        except Exception as e:
            logger.error(f"Unexpected error occurred while getting all job positions: {e}")
            raise DatabaseError(
                status_code=500,
            )

    async def get_all_job_positions(self, page_size: int, page: int) -> tuple[JobPositionSchema, ...]:
        try:
            statement = select(JobPositionSchema).limit(page_size).offset((page - 1) * page_size)
            result: Result = await self.session.execute(statement)
            job_positions = result.scalars().all()
            return tuple(job_positions)
        except Exception as e:
            logger.error(f"Unexpected error occurred while getting all job positions: {e}")
            raise DatabaseError(
                status_code=500,
            )

    async def get_job_position_by_id(self, job_position_id: UUID) -> JobPositionSchema | None:
        try:
            job_position: JobPositionSchema | None = await self.session.get(JobPositionSchema, job_position_id)
            print(job_position)
            if job_position:
                return job_position
            return job_position
        except Exception as e:
            logger.error(f"Unexpected error occurred while getting job position: {e}")
            raise DatabaseError(
                status_code=500,
            )

    async def delete_job_position_by_id(self, job_position_id: UUID) -> None:
        try:
            job_position: JobPositionSchema | None = await self.session.get(JobPositionSchema, job_position_id)
            if job_position is not None:
                await self.session.delete(job_position)
        except Exception as e:
            logger.error(f"Unexpected error occurred while deleting job position: {e}")
            raise DatabaseError(
                status_code=500,
            )