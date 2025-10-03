#internal modules
from app.database.session.get_session import get_session
from app.database.schema.candidate_schema import CandidateSchema
from app.custom_exceptions.custom_exceptions import DatabaseError

#3rd party libraries
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import insert, select, delete, Insert, Select, Delete
from sqlalchemy.engine import Result, ScalarResult
from fastapi import Depends

#1st party libraries
from typing import Protocol
from uuid import UUID
import logging


logger: logging.Logger = logging.getLogger(__name__)

class ICandidateRepository(Protocol):

    async def create_candidate(self, candidate: CandidateSchema) -> None:
        ...

    async def get_candidate_by_id(self, candidate_id: UUID) -> CandidateSchema | None:
        ...

    async def get_multiple_candidates_by_id(self, candidates_ids: tuple[UUID, ...]) -> tuple[CandidateSchema, ...] | tuple:
        ...

    async def get_all_candidates(self) -> tuple[CandidateSchema, ...] | tuple:
        ...

    async def delete_candidate_by_id(self, candidate_id: UUID) -> None:
        ...


def new_candidate_repository(session: AsyncSession = Depends(get_session)) -> ICandidateRepository:
    try:
        return CandidateRepository(session)
    except Exception as e:
        logger.error(f"Unexpected error occurred while creating new candidate repository: {e}")
        raise DatabaseError(
            status_code=500,
        )

class CandidateRepository(ICandidateRepository):
    __slots__ = 'session'
    def __init__(self, session: AsyncSession) -> None:
        self.session: AsyncSession = session

    async def create_candidate(self, candidate: CandidateSchema) -> None:
        try:
            self.session.add(candidate)
        except Exception as e:
            logger.error(f"Unexpected error occurred while creating new candidate: {e}")
            raise DatabaseError(
                status_code=500,
            )

    async def get_candidate_by_id(self, candidate_id: UUID) -> CandidateSchema | None:
        try:
            candidate: CandidateSchema | None = await self.session.get(CandidateSchema, candidate_id)
            return candidate
        except Exception as e:
            logger.error(f"Unexpected error occurred while getting candidate: {e}")
            raise DatabaseError(
                status_code=500,
            )

    async def get_multiple_candidates_by_id(
        self, candidates_ids: tuple[UUID, ...]
    ) -> tuple[CandidateSchema, ...]:
        try:
            statement = select(CandidateSchema).where(CandidateSchema.id.in_(candidates_ids))
            result = await self.session.execute(statement)
            candidates = result.scalars().all()
            return tuple(candidates)
        except Exception as e:
            logger.error(f"Unexpected error occurred while getting candidates: {e}")
            raise DatabaseError(status_code=500)

    async def get_all_candidates(self) -> tuple[CandidateSchema, ...]:
        try:
            statement = select(CandidateSchema)
            result = await self.session.execute(statement)
            candidates = result.scalars().all()
            return tuple(candidates)
        except Exception as e:
            logger.error(f"Unexpected error occurred while getting all candidates: {e}")
            raise DatabaseError(status_code=500)

    async def delete_candidate_by_id(self, candidate_id: UUID) -> None:
        try:
            candidate: CandidateSchema | None = await self.session.get(CandidateSchema, candidate_id)
            if candidate is not None:
                await self.session.delete(candidate)
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Unexpected error occurred while deleting candidate: {e}")
            raise DatabaseError(status_code=500)
