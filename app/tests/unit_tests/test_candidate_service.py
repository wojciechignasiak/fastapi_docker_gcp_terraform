#internal modules
from app.database.schema.candidate_schema import CandidateSchema
from app.models.candidate_models.candidate_response_models import CandidateResponseModel, GetAllCandidatesResponseModel
from app.models.candidate_models.candidate_request_models import CreateCandidateRequestModel
from app.services.candidate_service import CandidateService
from app.custom_exceptions.custom_exceptions import ServiceError

#3rd party libraries
import pytest

#1st party libraries
from uuid import UUID


class TestCandidateService:

    @pytest.fixture(autouse=True)
    def setup_method(self, mock_candidate_repository):
        self.candidate_service: CandidateService = CandidateService(mock_candidate_repository)

    @pytest.fixture(scope="function")
    def candidate_schema(self) -> CandidateSchema:
        return CandidateSchema(
            first_name="John",
            last_name="Doe",
        )

    @pytest.fixture(scope="function")
    def create_candidate_request_model(self) -> CreateCandidateRequestModel:
        return CreateCandidateRequestModel(
            first_name="John",
            last_name="Doe",
        )

    def test_convert_candidate_schema_to_candidate_response_model_success(self, candidate_schema):

        candidate_response_model = self.candidate_service._convert_candidate_schema_to_candidate_response_model(
            candidate_schema
        )

        assert isinstance(candidate_response_model, CandidateResponseModel)
        assert candidate_response_model.id == candidate_schema.id
        assert candidate_response_model.first_name == candidate_schema.first_name
        assert candidate_response_model.last_name == candidate_schema.last_name

    def test_convert_create_candidate_schema_to_candidate_response_model_failure(self):

        with pytest.raises(ServiceError) as e:
            self.candidate_service._convert_candidate_schema_to_candidate_response_model("wrong_input_data")

        assert e.value.status_code == 500

    def test_convert_candidate_request_model_to_candidate_schema_success(self, create_candidate_request_model):

        candidate_schema = self.candidate_service._convert_create_candidate_request_model_to_candidate_schema(create_candidate_request_model)

        assert isinstance(candidate_schema, CandidateSchema)
        assert isinstance(candidate_schema.id, UUID)
        assert candidate_schema.first_name == create_candidate_request_model.first_name
        assert candidate_schema.last_name == create_candidate_request_model.last_name

    def test_convert_candidate_schema_to_candidate_request_model_failure(self):
        with pytest.raises(ServiceError) as e:
            self.candidate_service._convert_create_candidate_request_model_to_candidate_schema("wrong_input_data")

        assert e.value.status_code == 500

    def test_extract_missing_candidates_ids_candidates_ids_found_success(self):
        candidates_schemas: tuple = ()
        candidate_ids: tuple = (1, 2, 3)

        missing_candidates_ids = self.candidate_service._extract_missing_candidates_ids(candidate_ids, candidates_schemas,)

        assert missing_candidates_ids == candidate_ids

    def test_extract_missing_candidates_ids_candidates_ids_not_found_success(self, candidate_schema):
        candidates_schemas: tuple[CandidateSchema, ...] = (candidate_schema,)
        candidate_ids: tuple = (candidate_schema.id,)

        missing_candidates_ids = self.candidate_service._extract_missing_candidates_ids(candidate_ids,
                                                                                        candidates_schemas, )

        assert len(missing_candidates_ids) == 0

    def test_extract_missing_candidates_ids_failure(self):

        with pytest.raises(ServiceError) as e:
            self.candidate_service._extract_missing_candidates_ids("wrong_input_data", "wrong_input_data")

        assert e.value.status_code == 500

    def test_calculate_last_page_number_for_get_all_candidates_response_model_success(self):
        total_number_of_candidates = 23
        page_size = 10

        last_page = self.candidate_service._calculate_last_page_number_for_get_all_candidates_response_model(
            total_number_of_candidates, page_size
        )

        assert isinstance(last_page, int)
        assert last_page == 3  # (23 + 10 - 1) // 10 == 3

    def test_calculate_last_page_number_for_get_all_candidates_response_model_with_exact_division_success(self):
        total_number_of_candidates = 30
        page_size = 10

        last_page = self.candidate_service._calculate_last_page_number_for_get_all_candidates_response_model(
            total_number_of_candidates, page_size
        )

        assert last_page == 3  # 30 // 10 == 3

    def test_calculate_last_page_number_for_get_all_candidates_response_model_failure(self):
        with pytest.raises(ServiceError) as e:
            self.candidate_service._calculate_last_page_number_for_get_all_candidates_response_model("wrong_input",
                                                                                                     "wrong_input")

        assert e.value.status_code == 500

    def test_create_get_all_candidates_response_model_success(self):
        candidates_response_models = [
            CandidateResponseModel(id=UUID("3f971abf-ec4b-4780-89a7-526dfef4881d"), first_name="John", last_name="Doe"),
            CandidateResponseModel(id=UUID("84467d7a-e21b-447c-b40e-e269dbf99b8c"), first_name="Jane", last_name="Smith"),
        ]

        response_model = self.candidate_service._create_get_all_candidates_response_model(
            page_size=10,
            page=1,
            total_number_of_candidates=2,
            last_page=1,
            candidates_response_models=candidates_response_models,
        )

        assert isinstance(response_model, GetAllCandidatesResponseModel)
        assert response_model.page_size == 10
        assert response_model.page == 1
        assert response_model.total_number_of_entities == 2
        assert response_model.last_page == 1
        assert response_model.entities == candidates_response_models

    def test_create_get_all_candidates_response_model_failure(self):
        with pytest.raises(ServiceError) as e:
            self.candidate_service._create_get_all_candidates_response_model(
                page_size="invalid",
                page="invalid",
                total_number_of_candidates="invalid",
                last_page="invalid",
                candidates_response_models="invalid",
            )

        assert e.value.status_code == 500