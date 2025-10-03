#internal modules
from models.app_config_models.database_credentials_model import DatabaseCredentials

#1st party libraries
from typing import Protocol

#3rd party libraries
from google.cloud import secretmanager_v1


class ISecretManager(Protocol):

    def get_database_credentials(self) -> DatabaseCredentials:
        ...


def new_secret_manager() -> ISecretManager:
    try:
        return SecretManager()
    except Exception as e:
        raise e

class SecretManager:
    def __init__(self, environment: str):
        self.client: secretmanager_v1.SecretManagerServiceClient = secretmanager_v1.SecretManagerServiceClient()


    def get_database_credentials(self) -> DatabaseCredentials:
        try:
            database_credentials = DatabaseCredentials()
            return database_credentials
        except Exception as e:
            raise e