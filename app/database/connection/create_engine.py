#internal libraries
from app.models.app_config_models.database_credentials_model import DatabaseCredentials

#3rd party libraries
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine
import logging


logger: logging.Logger = logging.getLogger(__name__)

def create_engine(database_credentials: DatabaseCredentials) -> AsyncEngine:
    try:
        engine = create_async_engine(
            f"postgresql+asyncpg://{
            database_credentials.username
            }:{
            database_credentials.password
            }@{
            database_credentials.host
            }:{
            database_credentials.port
            }/{
            database_credentials.database
            }"
        )
        return engine
    except Exception as e:
        logger.error(f"Unexpected error occurred creating database engine: {e}")
        raise e
