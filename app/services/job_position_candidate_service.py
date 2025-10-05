# internal modules
from app.database.repositories.job_position_candidate_repository import IJobPositionCandidateRepository, \
    new_job_position_candidate_repository
from app.services.candidate_service import ICandidateService, new_candidate_service
from app.services.job_position_service import IJobPositionService, new_job_position_service
from app.models.job_position_models.job_position_response_models import JobPositionResponseModel
from app.models.candidate_models.candidate_response_models import CandidateResponseModel
from app.models.job_position_candidate_models.candidate_job_position_request_models import AssignCandidateToJobPositionRequestModel, UnassignCandidateFromJobPositionRequestModel
from app.models.job_position_candidate_models.candidate_job_position_response_models import JobPositionCandidatesResponseModel, CandidateJobPositionsResponseModel
from app.custom_exceptions.custom_exceptions import DataNotFoundError, ServiceError, CustomException

# 3rd party modules
from fastapi import Depends

# 1st party modules
from typing import Protocol
from uuid import UUID
import logging


logger: logging.Logger = logging.getLogger(__name__)


class IJobPositionCandidateService(Protocol):

    async def assign_candidate_to_job_position(self,
                                               assign_candidate_to_job_position_request_model: AssignCandidateToJobPositionRequestModel) -> None:
        ...

    async def unassign_candidate_from_job_position(self,
                                                   unassign_candidate_to_job_position_request_model: UnassignCandidateFromJobPositionRequestModel) -> None:
        ...

    async def get_job_position_candidates(self, job_position_id: UUID) -> JobPositionCandidatesResponseModel:
        ...

    async def get_candidate_job_positions(self, candidate_id: UUID) -> CandidateJobPositionsResponseModel:
        ...


def new_job_position_candidate_service(
        candidate_job_position_repository: IJobPositionCandidateRepository = Depends(
            new_job_position_candidate_repository),
        candidate_service: ICandidateService = Depends(new_candidate_service),
        job_position_service: IJobPositionService = Depends(new_job_position_service),
) -> IJobPositionCandidateService:
    try:
        return JobPositionCandidateService(
            candidate_job_position_repository,
            candidate_service,
            job_position_service,
        )
    except Exception as e:
        logger.error(f"Unexpected error occurred creating job position candidate service: {e}")
        raise ServiceError(
            status_code=500,
        )


class JobPositionCandidateService(IJobPositionCandidateService):
    __slots__ = ("_job_position_candidate_repository", "_candidate_service", "_job_position_service")

    def __init__(
            self,
            job_position_candidate_repository: IJobPositionCandidateRepository,
            candidate_service: ICandidateService,
            job_position_service: IJobPositionService,
    ) -> None:
        self._job_position_candidate_repository: IJobPositionCandidateRepository = job_position_candidate_repository
        self._candidate_service: ICandidateService = candidate_service
        self._job_position_service: IJobPositionService = job_position_service

    async def assign_candidate_to_job_position(self,
                                               assign_candidate_to_job_position_request_model: AssignCandidateToJobPositionRequestModel) -> None:
        try:
            await self._job_position_service.get_job_position_by_id(
                assign_candidate_to_job_position_request_model.job_position_id
            )
            await self._candidate_service.get_candidate_by_id(
                assign_candidate_to_job_position_request_model.candidate_id
            )
            await self._job_position_candidate_repository.assign_candidate_to_job_position(
                assign_candidate_to_job_position_request_model.candidate_id,
                assign_candidate_to_job_position_request_model.job_position_id,
            )
        except CustomException as e:
            raise ServiceError(
                message=e.message,
                status_code=e.status_code,
            )
        except Exception as e:
            logger.error(f"Unexpected error occurred while assigning candidate to job position: {e}")
            raise ServiceError(
                status_code=500,
            )

    async def unassign_candidate_from_job_position(
            self,
            unassign_candidate_to_job_position_request_model: UnassignCandidateFromJobPositionRequestModel
    ) -> None:
        try:
            await self._job_position_service.get_job_position_by_id(
                unassign_candidate_to_job_position_request_model.job_position_id
            )
            await self._candidate_service.get_candidate_by_id(
                unassign_candidate_to_job_position_request_model.candidate_id
            )
            await self._job_position_candidate_repository.unassign_candidate_from_job_position(
                unassign_candidate_to_job_position_request_model.candidate_id,
                unassign_candidate_to_job_position_request_model.job_position_id
            )
        except CustomException as e:
            raise ServiceError(
                message=e.message,
                status_code=e.status_code,
            )
        except Exception as e:
            logger.error(f"Unexpected error occurred while unassigning candidate from job position: {e}")
            raise ServiceError(
                status_code=500,
            )

    async def get_job_position_candidates(self, job_position_id: UUID) -> JobPositionCandidatesResponseModel:
        try:
            job_position: JobPositionResponseModel = await self._job_position_service.get_job_position_by_id(
                job_position_id)

            candidates_id: tuple[UUID, ...] | tuple = await self._job_position_candidate_repository.get_candidates_ids_by_job_position_id(
                job_position_id
            )
            if not candidates_id:
                raise DataNotFoundError(
                    message="No candidates found for job position",
                    status_code=404,
                )

            candidates: list[CandidateResponseModel] = await self._candidate_service.get_multiple_candidates_by_id(candidates_id)

            job_position_candidates: JobPositionCandidatesResponseModel = self._create_job_position_candidates_response_model(
                job_position,
                candidates,
            )
            return job_position_candidates
        except CustomException as e:
            raise ServiceError(
                message=e.message,
                status_code=e.status_code,
            )
        except Exception as e:
            logger.error(f"Unexpected error occurred while getting job position candidates: {e}")
            raise ServiceError(
                status_code=500,
            )

    async def get_candidate_job_positions(self, candidate_id: UUID) -> CandidateJobPositionsResponseModel:
        try:
            candidate: CandidateResponseModel = await self._candidate_service.get_candidate_by_id(candidate_id)

            job_positions_ids: tuple[UUID, ...] =  await self._job_position_candidate_repository.get_job_positions_ids_by_candidate_id(candidate_id)
            if not job_positions_ids:
                raise DataNotFoundError(
                    message="No job positions found for candidate",
                    status_code=404,
                )

            job_positions: list[JobPositionResponseModel] = await self._job_position_service.get_multiple_job_positions_by_id(job_positions_ids)

            candidate_job_positions: CandidateJobPositionsResponseModel = self._create_candidate_job_positions_response_model(
                candidate,
                job_positions,
            )
            return candidate_job_positions
        except CustomException as e:
            raise ServiceError(
                message=e.message,
                status_code=e.status_code,
            )
        except Exception as e:
            logger.error(f"Unexpected error occurred while getting job position candidates: {e}")
            raise ServiceError(
                status_code=500,
            )

    @staticmethod
    def _create_job_position_candidates_response_model(job_position_response_model: JobPositionResponseModel, candidates_response_model: list[CandidateResponseModel]) -> JobPositionCandidatesResponseModel:
        try:
            return JobPositionCandidatesResponseModel(
                job_position=job_position_response_model,
                candidates=candidates_response_model
            )
        except Exception as e:
            logger.error(f"Unexpected error occurred while creating job position candidates response model: {e}")
            raise ServiceError(
                status_code=500,
            )

    @staticmethod
    def _create_candidate_job_positions_response_model(candidate_response_model: CandidateResponseModel, job_positions_response_model: list[JobPositionResponseModel]) -> CandidateJobPositionsResponseModel:
        try:
            return CandidateJobPositionsResponseModel(
                candidate=candidate_response_model,
                job_positions=job_positions_response_model,
            )
        except Exception as e:
            logger.error(f"Unexpected error occurred while creating candidate job positions response model: {e}")
            raise ServiceError(
                status_code=500,
            )