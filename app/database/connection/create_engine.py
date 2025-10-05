#internal modules
from app.models.app_config_models.database_credentials_model import DatabaseCredentials

#3rd party libraries
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine
import logging

#1st party libraries
from urllib.parse import quote_plus

logger: logging.Logger = logging.getLogger(__name__)

def create_engine(database_credentials: DatabaseCredentials) -> AsyncEngine:
    try:
        engine = create_async_engine(
            f"postgresql+asyncpg://{
            quote_plus(database_credentials.username)
            }:{
            quote_plus(database_credentials.password)
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
