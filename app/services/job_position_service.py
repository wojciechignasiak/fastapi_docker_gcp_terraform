# internal modules
from app.database.repositories.job_position_repository import IJobPositionRepository, new_job_position_repository
from app.models.job_position_models.job_position_request_models import CreateJobPositionRequestModel, GetAllJobPositionsRequestModel
from app.models.job_position_models.job_position_response_models import JobPositionResponseModel, GetAllJobPositionsResponseModel
from app.database.schema.job_position_schema import JobPositionSchema
from app.custom_exceptions.custom_exceptions import DataNotFoundError, ServiceError, CustomException

# 3rd party modules
from fastapi import Depends

# 1st party modules
from typing import Protocol
from uuid import UUID
import logging

logger: logging.Logger = logging.getLogger(__name__)

class IJobPositionService(Protocol):

    async def create_job_position(self, create_job_position_request_model: CreateJobPositionRequestModel) -> JobPositionResponseModel:
        ...

    async def get_job_position_by_id(self, job_position_id: UUID) -> JobPositionResponseModel:
        ...

    async def get_multiple_job_positions_by_id(self, job_position_ids: tuple[UUID, ...]) -> list[JobPositionResponseModel]:
        ...

    async def get_all_job_positions(self, pagination: GetAllJobPositionsRequestModel) -> GetAllJobPositionsResponseModel:
        ...

    async def remove_job_position_by_id(self, job_position_id: UUID) -> None:
        ...


def new_job_position_service(
        job_position_repository: IJobPositionRepository = Depends(new_job_position_repository)) -> IJobPositionService:
    try:
        return JobPositionService(job_position_repository)
    except Exception as e:
        logger.error(f"Unexpected error occurred creating job position service: {e}")
        raise ServiceError(status_code=500)


class JobPositionService(IJobPositionService):
    __slots__ = '_job_position_repository'

    def __init__(self, job_position_repository: IJobPositionRepository) -> None:
        self._job_position_repository: IJobPositionRepository = job_position_repository

    async def create_job_position(self, create_job_position_request_model: CreateJobPositionRequestModel) -> JobPositionResponseModel:
        try:
            job_position_schema: JobPositionSchema = self._convert_create_job_position_request_model_to_job_position_schema(
                create_job_position_request_model)
            await self._job_position_repository.create_job_position(job_position_schema)
            job_position: JobPositionResponseModel = self._convert_job_position_schema_to_job_position_response_model(job_position_schema)
            return job_position
        except CustomException as e:
            raise ServiceError(
                message=e.message,
                status_code=e.status_code,
            )
        except Exception as e:
            logger.error(f"Unexpected error occurred creating job position: {e}")
            raise ServiceError(
                status_code=500,
            )

    async def get_job_position_by_id(self, job_position_id: UUID) -> JobPositionResponseModel:
        try:
            job_position_schema: JobPositionSchema | None = await self._job_position_repository.get_job_position_by_id(
                job_position_id)
            if not job_position_schema:
                raise DataNotFoundError(
                    message=f"Job position not found",
                    status_code=404,
                )
            job_position_response_model: JobPositionResponseModel = self._convert_job_position_schema_to_job_position_response_model(
                job_position_schema)
            return job_position_response_model
        except CustomException as e:
            print(e.status_code)
            raise ServiceError(
                message=e.message,
                status_code=e.status_code,
            )
        except Exception as e:
            logger.error(f"Unexpected error occurred while getting job position: {e}")
            raise ServiceError(
                status_code=500,
            )

    async def get_multiple_job_positions_by_id(self, job_positions_ids: tuple[UUID, ...]) -> list[JobPositionResponseModel]:
        try:
            job_positions_schemas: tuple[
                JobPositionSchema, ...
            ] = await self._job_position_repository.get_multiple_job_positions_by_id(
                job_positions_ids
            )
            if not job_positions_schemas:
                raise DataNotFoundError(
                    message="No job positions found",
                    status_code=404,
                )
            missing_job_positions_ids: tuple[UUID, ...] | tuple = self._extract_missing_job_positions_ids(job_positions_ids,
                                                                                                   job_positions_schemas)
            if missing_job_positions_ids:
                raise DataNotFoundError(
                    message=f"Job positions with ids {missing_job_positions_ids} not found",
                    status_code=404,
                )
            job_position_response_models: list[JobPositionResponseModel] = [
                self._convert_job_position_schema_to_job_position_response_model(job_position_schema)
                for job_position_schema
                in job_positions_schemas
            ]
            return job_position_response_models
        except CustomException as e:
            raise ServiceError(
                message=e.message,
                status_code=e.status_code,
            )
        except Exception as e:
            logger.error(f"Unexpected error occurred while getting all job positions: {e}")
            raise ServiceError(
                status_code=500,
            )

    async def get_all_job_positions(self, pagination: GetAllJobPositionsRequestModel) -> GetAllJobPositionsResponseModel:
        try:
            total_number_of_job_positions: int = await self._job_position_repository.count_number_of_all_job_positions()
            if total_number_of_job_positions == 0:
                raise DataNotFoundError(
                    message="No job positions found",
                    status_code=404,
                )
            last_page: int = self._calculate_last_page_number_for_get_all_job_positions_response_model(
                total_number_of_job_positions=total_number_of_job_positions,
                page_size=pagination.page_size
            )
            job_positions_schemas: tuple[
                JobPositionSchema, ...] = await self._job_position_repository.get_all_job_positions(
                page_size=pagination.page_size,
                page=pagination.page
            )
            if not job_positions_schemas:
                raise DataNotFoundError(
                    message="No job positions found",
                    status_code=404,
                )

            job_position_response_models: list[JobPositionResponseModel] = [
                self._convert_job_position_schema_to_job_position_response_model(job_position_schema)
                for job_position_schema
                in job_positions_schemas
            ]
            get_all_job_positions_response_model: GetAllJobPositionsResponseModel = self._create_get_all_job_positions_response_model(
                page_size=pagination.page_size,
                page=pagination.page,
                total_number_of_job_positions=total_number_of_job_positions,
                last_page=last_page,
                job_positions_response_models=job_position_response_models,
            )


            return get_all_job_positions_response_model
        except CustomException as e:
            raise ServiceError(
                message=e.message,
                status_code=e.status_code,
            )
        except Exception as e:
            logger.error(f"Unexpected error occurred while getting all job positions: {e}")
            raise ServiceError(
                status_code=500,
            )

    async def remove_job_position_by_id(self, job_position_id: UUID) -> None:
        try:
            await self.get_job_position_by_id(job_position_id)
            await self._job_position_repository.delete_job_position_by_id(job_position_id)
        except CustomException as e:
            raise ServiceError(
                message=e.message,
                status_code=e.status_code,
            )
        except Exception as e:
            logger.error(f"Unexpected error occurred while removing job position by id: {e}")
            raise ServiceError(
                status_code=500,
            )

    @staticmethod
    def _convert_job_position_schema_to_job_position_response_model(
            job_position_schema: JobPositionSchema) -> JobPositionResponseModel:
        try:
            return JobPositionResponseModel(
                id=job_position_schema.id,
                name=job_position_schema.name,
            )
        except Exception as e:
            logger.error(f"Unexpected error occurred while converting job position schema to job position response model: {e}")
            raise ServiceError(
                status_code=500,
            )

    @staticmethod
    def _convert_create_job_position_request_model_to_job_position_schema(
            create_job_position_request_model: CreateJobPositionRequestModel) -> JobPositionSchema:
        try:
            return JobPositionSchema(
                name=create_job_position_request_model.name,
            )
        except Exception as e:
            logger.error(f"Unexpected error occurred while converting job position request model to job position schema: {e}")
            raise ServiceError(
                status_code=500,
            )

    @staticmethod
    def _extract_missing_job_positions_ids(job_positions_ids: tuple[UUID, ...],
                                        job_positions_schemas: tuple[JobPositionSchema, ...]) -> tuple[UUID, ...] | tuple:
        try:
            existing_ids = {schema.id for schema in job_positions_schemas}
            missing_ids = set(job_positions_ids) - existing_ids
            return tuple(missing_ids)
        except Exception as e:
            logger.error(f"Unexpected error occurred while extracting missing candidates ids: {e}")
            raise ServiceError(
                status_code=500,
            )

    @staticmethod
    def _calculate_last_page_number_for_get_all_job_positions_response_model(
            total_number_of_job_positions: int,
            page_size: int,
    ) -> int:
        try:
            return (total_number_of_job_positions + page_size - 1) // page_size
        except Exception as e:
            logger.error(
                f"Unexpected error occurred while calculating last page number for get all candidates response model: {e}")
            raise ServiceError(
                status_code=500,
            )

    @staticmethod
    def _create_get_all_job_positions_response_model(
            page_size: int,
            page: int,
            total_number_of_job_positions: int,
            last_page: int,
            job_positions_response_models: list[JobPositionResponseModel],
    ) -> GetAllJobPositionsResponseModel:
        try:
            return GetAllJobPositionsResponseModel(
                page_size=page_size,
                page=page,
                total_number_of_entities=total_number_of_job_positions,
                last_page=last_page,
                entities=job_positions_response_models,
            )
        except Exception as e:
            logger.error(f"Unexpected error occurred while creating get all job positions response model: {e}")
            raise ServiceError(
                status_code=500,
            )