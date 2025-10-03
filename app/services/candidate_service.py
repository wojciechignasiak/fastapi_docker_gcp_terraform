#internal modules
from app.database.repositories.candidate_repository import ICandidateRepository, new_candidate_repository
from app.models.candidate_models.candidate_request_models import CreateCandidateRequestModel
from app.models.candidate_models.candidate_response_models import CandidateResponseModel
from app.database.schema.candidate_schema import CandidateSchema
from app.custom_exceptions.custom_exceptions import DataNotFoundError, ServiceError, CustomException

#3rd party modules
from fastapi import Depends

#1st party modules
from typing import Protocol
from uuid import UUID
import logging


logger: logging.Logger = logging.getLogger(__name__)

class ICandidateService(Protocol):

    async def create_candidate(self, created_candidate: CreateCandidateRequestModel) -> CandidateResponseModel:
        ...

    async def get_candidate_by_id(self, candidate_id: UUID) -> CandidateResponseModel:
        ...

    async def get_multiple_candidates_by_id(self, candidates_ids: tuple[UUID, ...]) -> list[CandidateResponseModel]:
        ...

    async def get_all_candidates(self) -> list[CandidateResponseModel]:
        ...

    async def remove_candidate_by_id(self, candidate_id: UUID) -> None:
        ...


def new_candidate_service(candidate_repository: ICandidateRepository = Depends(new_candidate_repository)) -> ICandidateService:
    try:
        return CandidateService(candidate_repository)
    except Exception as e:
        logger.error(f"Unexpected error occurred creating candidate service: {e}")
        raise ServiceError(
            status_code=500,
        )

class CandidateService(ICandidateService):
    __slots__ = 'candidate_repository'
    def __init__(self, candidate_repository: ICandidateRepository) -> None:
        self._candidate_repository: ICandidateRepository = candidate_repository

    async def create_candidate(self, created_candidate: CreateCandidateRequestModel) -> CandidateResponseModel:
        try:
            candidate_schema: CandidateSchema = self._convert_create_candidate_request_model_to_candidate_schema(created_candidate)
            await self._candidate_repository.create_candidate(candidate_schema)
            candidate_response_model: CandidateResponseModel = self._convert_candidate_schema_to_candidate_response_model(candidate_schema)
            return candidate_response_model
        except CustomException as e:
            raise ServiceError(
                message=e.message,
                status_code=e.status_code,
            )
        except Exception as e:
            logger.error(f"Unexpected error occurred creating candidate: {e}")
            raise ServiceError(
                status_code=500,
            )

    async def get_candidate_by_id(self, candidate_id: UUID) -> CandidateResponseModel:
        try:
            candidate_schema: CandidateSchema | None = await self._candidate_repository.get_candidate_by_id(candidate_id)
            if not candidate_schema:
                raise DataNotFoundError(
                    message=f"Candidate not found",
                    status_code=404,
                )
            candidate_response_model: CandidateResponseModel = self._convert_candidate_schema_to_candidate_response_model(candidate_schema)
            return candidate_response_model
        except CustomException as e:
            raise ServiceError(
                message=e.message,
                status_code=e.status_code,
            )
        except Exception as e:
            logger.error(f"Unexpected error occurred while getting candidate: {e}")
            raise ServiceError(
                status_code=500,
            )

    async def get_multiple_candidates_by_id(self, candidates_ids: tuple[UUID, ...]) -> list[CandidateResponseModel]:
        try:
            candidates_schemas: tuple[CandidateSchema, ...] | tuple = await self._candidate_repository.get_multiple_candidates_by_id(candidates_ids)
            if not candidates_schemas:
                raise DataNotFoundError(
                    message=f"Candidates with provided ids not found",
                    status_code=404,
                )
            missing_customers_ids: tuple[UUID, ...] | tuple = self._extract_missing_candidates_ids(candidates_ids, candidates_schemas)
            if missing_customers_ids:
                raise DataNotFoundError(
                    message=f"Candidates not found",
                    status_code=404,
                )

            candidate_response_models: list[CandidateResponseModel] = [
                self._convert_candidate_schema_to_candidate_response_model(candidate_schema)
                for candidate_schema
                in candidates_schemas
            ]

            return candidate_response_models
        except CustomException as e:
            raise ServiceError(
                message=e.message,
                status_code=e.status_code,
            )
        except Exception as e:
            logger.error(f"Unexpected error occurred while getting candidates: {e}")
            raise ServiceError(
                status_code=500,
            )

    async def get_all_candidates(self) -> list[CandidateResponseModel]:
        try:
            candidates_schemas: tuple[CandidateSchema, ...] | tuple = await self._candidate_repository.get_all_candidates()
            if not candidates_schemas:
                raise DataNotFoundError(
                    message="No candidates found",
                    status_code=404,
                )
            candidate_response_models: list[CandidateResponseModel] = [
                self._convert_candidate_schema_to_candidate_response_model(candidate_schema)
                for candidate_schema
                in candidates_schemas
            ]
            return candidate_response_models
        except CustomException as e:
            raise ServiceError(
                message=e.message,
                status_code=e.status_code,
            )
        except Exception as e:
            logger.error(f"Unexpected error occurred while getting all candidates: {e}")
            raise ServiceError(
                status_code=500,
            )

    async def remove_candidate_by_id(self, candidate_id: UUID) -> None:
        try:
            await self.get_candidate_by_id(candidate_id)
            await self._candidate_repository.delete_candidate_by_id(candidate_id)
        except CustomException as e:
            raise ServiceError(
                message=e.message,
                status_code=e.status_code,
            )
        except Exception as e:
            logger.error(f"Unexpected error occurred while removing candidate by id: {e}")
            raise ServiceError(
                status_code=500,
            )

    @staticmethod
    def _convert_candidate_schema_to_candidate_response_model(candidate_schema: CandidateSchema) -> CandidateResponseModel:
        try:
            return CandidateResponseModel(
                id=candidate_schema.id,
                first_name=candidate_schema.first_name,
                last_name=candidate_schema.last_name,
            )
        except Exception as e:
            logger.error(f"Unexpected error occurred while converting candidate schema to candidate response model: {e}")
            raise ServiceError(
                status_code=500,
            )

    @staticmethod
    def _convert_create_candidate_request_model_to_candidate_schema(create_candidate_request_model: CreateCandidateRequestModel) -> CandidateSchema:
        try:
            return CandidateSchema(
                first_name=create_candidate_request_model.first_name,
                last_name=create_candidate_request_model.last_name,
            )
        except Exception as e:
            logger.error(f"Unexpected error occurred while converting candidate request model to candidate schema: {e}")
            raise ServiceError(
                status_code=500,
            )

    @staticmethod
    def _extract_missing_candidates_ids(candidate_ids: tuple[UUID, ...], candidates_schemas: tuple[CandidateSchema, ...]) -> tuple[UUID, ...] | tuple:
        try:
            candidates_ids_from_schemas: tuple[UUID, ...] | tuple = tuple(candidate_schema. id for candidate_schema in candidates_schemas)
            return tuple(candidate_id for candidate_id in candidate_ids if candidate_id not in candidates_ids_from_schemas)
        except Exception as e:
            logger.error(f"Unexpected error occurred while extracting missing candidates ids: {e}")
            raise ServiceError(
                status_code=500,
            )