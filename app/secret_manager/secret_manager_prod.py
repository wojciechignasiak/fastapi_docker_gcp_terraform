#internal modules
from app.models.app_config_models.database_credentials_model import DatabaseCredentials

#3rd party libraries
from google.cloud import secretmanager

#1st party libraries
import logging

logger: logging.Logger = logging.getLogger(__name__)


class SecretManagerPROD:
    __slots__ = ("_environment", "_project_id", "_client")

    def __init__(
            self,
            environment: str,
            project_id: str | None,
            secret_manager_client: secretmanager.SecretManagerServiceClient
    ) -> None:
        self._environment: str = environment
        self._project_id: str = project_id
        self._client: secretmanager.SecretManagerServiceClient = secret_manager_client

    def get_database_credentials(self) -> DatabaseCredentials:
        try:
            database_credentials: DatabaseCredentials = self._get_production_database_credentials()
            return database_credentials
        except Exception as e:
            logger.error(f"Unexpected error occurred while getting database credentials: {e}")
            raise e

    def _get_production_database_credentials(self) -> DatabaseCredentials:
        try:
            return DatabaseCredentials(
                database=self._get_secret("DATABASE_NAME"),
                username=self._get_secret("DATABASE_USERNAME"),
                password=self._get_secret("DATABASE_PASSWORD"),
                host=self._get_secret("DATABASE_HOST"),
                port=self._get_secret("DATABASE_PORT"),
            )
        except Exception as e:
            logger.error(f"Unexpected error occurred while getting production database credentials: {e}")
            raise e

    def _get_secret(self, secret_id: str) -> str:
        try:
            response: secretmanager.AccessSecretVersionResponse = self._client.access_secret_version(request={"name": f"projects/{self._project_id}/secrets/{secret_id}/versions/latest"})
            return response.payload.data.decode("UTF-8")
        except Exception as e:
            logger.error(f"Unexpected error occurred while getting secret from cloud secret manager: {e}")
            raise e
