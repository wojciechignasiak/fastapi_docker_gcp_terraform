#internal modules
from app.main import app
from app.database.repositories.candidate_repository import CandidateRepository
from app.database.repositories.job_position_candidate_repository import JobPositionCandidateRepository
from app.database.repositories.job_position_repository import JobPositionRepository
from app.services.candidate_service import CandidateService
from app.services.job_position_candidate_service import JobPositionCandidateService
from app.services.job_position_service import JobPositionService
from app.database.schema import  CandidateSchema, JobPositionSchema, JobPositionCandidateSchema
from app.database.session.get_session import get_session

#3rd party libraries
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import StaticPool
from sqlmodel import SQLModel

#1st party libraries
from unittest.mock import Mock, AsyncMock, MagicMock


#mocks for unit tests

#mock repositories
@pytest.fixture
def mock_candidate_repository():
    return Mock(spec=CandidateRepository)

@pytest.fixture
def mock_job_position_repository():
    return Mock(spec=JobPositionRepository)

@pytest.fixture
def mock_job_position_candidate_repository():
    return Mock(spec=JobPositionCandidateRepository)

#mock services
@pytest.fixture
def mock_candidate_service():
    return Mock(spec=CandidateService)

@pytest.fixture
def mock_job_position_service():
    return Mock(spec=JobPositionService)

@pytest.fixture
def mock_job_position_candidate_service():
    return Mock(spec=JobPositionCandidateService)

#integration tests fixtures

SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

test_engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = async_sessionmaker(
    test_engine,
    class_=AsyncSession,
    expire_on_commit=False
)

@pytest_asyncio.fixture(scope="function")
async def db_session():

    async with test_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    async with TestingSessionLocal() as session:
        yield session

    async with test_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)


@pytest_asyncio.fixture(scope="function")
async def client(db_session):

    async def override_get_session():
        yield db_session

    app.dependency_overrides[get_session] = override_get_session

    app.state.engine = test_engine

    async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
    ) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest_asyncio.fixture(scope="function")
async def client_with_broken_database_session():

    async def override_get_session():
        session = MagicMock()
        session.add = MagicMock(side_effect=Exception("Database connection lost"))
        session.commit = AsyncMock(side_effect=Exception("Database connection lost"))
        session.execute = AsyncMock(side_effect=Exception("Database connection lost"))
        session.rollback = AsyncMock()
        session.close = AsyncMock()
        yield session

    app.dependency_overrides[get_session] = override_get_session

    async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
    ) as test_client:
        yield test_client

    app.dependency_overrides.clear()