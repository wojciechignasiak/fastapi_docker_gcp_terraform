#internal modules
from app.database.connection.create_engine import create_engine
from app.models.app_config_models.database_credentials_model import DatabaseCredentials
# from secret_manager.secret_manager import new_secret_manager, ISecretManager

##routers
from app.routers import (
    candidate_router,
    job_position_router,
    job_position_candidate_router,
    welcome_router
)

#1st party libraries
from contextlib import asynccontextmanager
import os
import logging

#3rd party libraries
from sqlalchemy.ext.asyncio import AsyncEngine
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from starlette import middleware
from dotenv import load_dotenv

load_dotenv()

ENVIRONMENT: str = os.environ.get("ENVIRONMENT")
# secret_manager: ISecretManager = new_secret_manager()

logging.basicConfig(
    filename='./app/logs/logs.log',
    level=logging.ERROR,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


middlewares = [
    middleware.Middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods="*",
        allow_headers=["*"]
    )]


@asynccontextmanager
async def lifespan(app: FastAPI):
    ''' Run at startup
            Initialise databases clients.
    '''
    print(f"Environment: {ENVIRONMENT}")
    if ENVIRONMENT == "production" or ENVIRONMENT == "sit":
        pass
    if ENVIRONMENT == "development":
        database_credentials: DatabaseCredentials = DatabaseCredentials(
            database=os.environ.get("POSTGRES_DATABASE"),
            username=os.environ.get("POSTGRES_USERNAME"),
            password=os.environ.get("POSTGRES_PASSWORD"),
            host=os.environ.get("POSTGRES_HOST"),
            port=str(os.environ.get("POSTGRES_PORT"))
        )
    # database_credentials: DatabaseCredentials = secret_manager.get_database_credentials()

    engine: AsyncEngine = create_engine(database_credentials)
    app.state.engine = engine


    yield
    ''' Run on shutdown
        Close the connection
        Clear variables and release the resources
    '''
    await engine.dispose()


def create_application() -> FastAPI:
    if ENVIRONMENT == "production":
        application = FastAPI(lifespan=lifespan, middleware=middlewares)
    else:
        application = FastAPI(lifespan=lifespan, openapi_url="/openapi.json", docs_url="/docs", middleware=middlewares)
    application.include_router(welcome_router.router, tags=["welcome"])
    application.include_router(candidate_router.router, prefix="/candidate", tags=["candidates"])
    application.include_router(job_position_router.router, prefix="/job-position", tags=["job_positions"])
    application.include_router(job_position_candidate_router.router, prefix="/job-position-candidate", tags=["job_position_candidate"])
    return application


app = create_application()