#internal modules
from app.models.candidate_models.candidate_request_models import CreateCandidateRequestModel, GetAllCandidatesRequestModel
#3rd party libraries
import pytest
from httpx import AsyncClient
from starlette import status

#1st party libraries
from uuid import uuid4

class TestCandidateRouter:

    @pytest.fixture(scope="class")
    def create_candidate_request_model(self) -> CreateCandidateRequestModel:
        return CreateCandidateRequestModel(
            first_name="John",
            last_name="Doe",
        )

    @pytest.fixture(scope="class")
    def create_candidate_request_model_list(self) -> list[CreateCandidateRequestModel]:
        return [
            CreateCandidateRequestModel(
                first_name="John",
                last_name="Doe",
            ),
            CreateCandidateRequestModel(
                first_name="Adam",
                last_name="Nowak",
            ),
            CreateCandidateRequestModel(
                first_name="Jan",
                last_name="Kowalski",
            ),
            ]

    @pytest.mark.asyncio
    async def test_create_candidate_router_success(
            self,
            client: AsyncClient,
            create_candidate_request_model: CreateCandidateRequestModel,
    ):


        response = await client.post("/candidate/create-candidate/", json=create_candidate_request_model.model_dump())

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["id"] is not None
        assert data["first_name"] == create_candidate_request_model.first_name
        assert data["last_name"] == create_candidate_request_model.last_name

    @pytest.mark.asyncio
    async def test_create_candidate_invalid_data(self, client: AsyncClient):
        candidate_data = {
            "first_name": "",
            "last_name": "Doe",
        }

        response = await client.post("/candidate/create-candidate/", json=candidate_data)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    @pytest.mark.asyncio
    async def test_create_candidate_missing_required_field(self, client: AsyncClient):
        candidate_data = {
            "first_name": "John",
        }

        response = await client.post("/candidate/create-candidate/", json=candidate_data)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    @pytest.mark.asyncio
    async def test_create_candidate_router_internal_error(
            self,
            client_with_broken_database_session: AsyncClient,
            create_candidate_request_model: CreateCandidateRequestModel,
    ):


        response = await client_with_broken_database_session.post("/candidate/create-candidate/", json=create_candidate_request_model.model_dump())

        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        data = response.json()
        assert data["detail"] == "Internal Server Error"

    @pytest.mark.asyncio
    async def test_get_candidate_router_success(
            self,
            client: AsyncClient,
            create_candidate_request_model: CreateCandidateRequestModel,
    ):

        response = await client.post("/candidate/create-candidate/", json=create_candidate_request_model.model_dump())

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["id"] is not None
        assert data["first_name"] == create_candidate_request_model.first_name
        assert data["last_name"] == create_candidate_request_model.last_name

        candidate_id = {
            "candidate_id": data["id"],
        }

        response = await client.get(f"/candidate/get-candidate/", params=candidate_id)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] is not None
        assert data["first_name"] == create_candidate_request_model.first_name
        assert data["last_name"] == create_candidate_request_model.last_name

    @pytest.mark.asyncio
    async def test_get_candidate_router_invalid_data(
            self,
            client: AsyncClient,
    ):

        candidate_id = {
            "candidate_id": "invalid_id"
        }

        response = await client.get(f"/candidate/get-candidate/", params=candidate_id)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    @pytest.mark.asyncio
    async def test_get_candidate_router_required_field(
            self,
            client: AsyncClient,
    ):

        candidate_id = {
            "invalid_field_id": "3f971abf-ec4b-4780-89a7-526dfef4881d"
        }

        response = await client.get(f"/candidate/get-candidate/", params=candidate_id)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    @pytest.mark.asyncio
    async def test_get_candidate_router_data_not_found(
            self,
            client: AsyncClient,
    ):

        candidate_id = {
            "candidate_id": uuid4()
        }

        response = await client.get(f"/candidate/get-candidate/", params=candidate_id)

        assert response.status_code == status.HTTP_404_NOT_FOUND
        data = response.json()
        assert data["detail"] == "Candidate not found"

    @pytest.mark.asyncio
    async def test_get_candidate_router_internal_error(
            self,
            client_with_broken_database_session: AsyncClient,
    ):
        candidate_id = {
            "candidate_id": uuid4()
        }

        response = await client_with_broken_database_session.get(f"/candidate/get-candidate/", params=candidate_id)

        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        data = response.json()
        assert data["detail"] == "Internal Server Error"

    @pytest.mark.asyncio
    async def test_get_all_candidates(
            self,
            client: AsyncClient,
            create_candidate_request_model_list: list[CreateCandidateRequestModel],
    ):

        for candidate in create_candidate_request_model_list:
            await client.post("/candidate/create-candidate/", json=candidate.model_dump())

        get_all_candidate_request_model = GetAllCandidatesRequestModel(
            page_size=1,
            page=1,
        )
        for candidate in create_candidate_request_model_list:
            response = await client.post(f"/candidate/get-all-candidates/", json=get_all_candidate_request_model.model_dump())

            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["page_size"] == get_all_candidate_request_model.page_size
            assert data["page"] == get_all_candidate_request_model.page
            assert data["total_number_of_entities"] == 3
            assert data["last_page"] == 3
            assert data["entities"][0]["id"] is not None
            assert data["entities"][0]["first_name"] == candidate.first_name
            assert data["entities"][0]["last_name"] == candidate.last_name
            get_all_candidate_request_model.page += 1


