#internal modules
from app.models.app_config_models.database_credentials_model import DatabaseCredentials
from app.secret_manager.secret_manager_prod import SecretManagerPROD
from app.secret_manager.secret_manager_dev import SecretManagerDEV

#3rd party libraries
from google.cloud import secretmanager
from dotenv import load_dotenv

#1st party libraries
from typing import Protocol
import os
import logging


logger: logging.Logger = logging.getLogger(__name__)
load_dotenv()


class ISecretManager(Protocol):

    def get_database_credentials(self) -> DatabaseCredentials:
        ...


def new_secret_manager(
        environment: str = os.environ.get("ENVIRONMENT"),
) -> ISecretManager:
    try:
        if environment == "production":
            return SecretManagerPROD(
                environment,
                project_id = os.environ.get("PROJECT_ID"),
                secret_manager_client = secretmanager.SecretManagerServiceClient()
            )
        else:
            return SecretManagerDEV(
                environment,
            )

    except Exception as e:
        logger.error(f"Unexpected error occurred while getting creating new secret manager: {e}")
        raise e



