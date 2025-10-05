#internal modules
from app.models.app_config_models.database_credentials_model import DatabaseCredentials

#3rd party libraries
from dotenv import load_dotenv

#1st party libraries
from typing import Protocol
import os
import logging


logger: logging.Logger = logging.getLogger(__name__)
load_dotenv()

class SecretManagerDEV:
    __slots__ = "_environment"
    
    def __init__(
            self,
            environment: str,
    ) -> None:
        self._environment: str = environment

    def get_database_credentials(self) -> DatabaseCredentials:
        try:
            database_credentials: DatabaseCredentials = self._get_development_database_credentials()
            return database_credentials
        except Exception as e:
            logger.error(f"Unexpected error occurred while getting database credentials: {e}")
            raise e

    @staticmethod
    def _get_development_database_credentials() -> DatabaseCredentials:
        try:
            return DatabaseCredentials(
                database=os.environ.get("DATABASE_NAME"),
                username=os.environ.get("DATABASE_USERNAME"),
                password=os.environ.get("DATABASE_PASSWORD"),
                host=os.environ.get("DATABASE_HOST"),
                port=os.environ.get("DATABASE_PORT")
            )
        except Exception as e:
            logger.error(f"Unexpected error occurred while getting development database credentials: {e}")
            raise e