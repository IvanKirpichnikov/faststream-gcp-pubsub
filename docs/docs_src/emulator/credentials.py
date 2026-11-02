from google.oauth2 import service_account

from faststream_gcp_pubsub import GCPSecurity, PubSubBroker


def from_key_file() -> PubSubBroker:
    return PubSubBroker(
        project_id="my-project",
        security=GCPSecurity.from_service_account_file("key.json"),
    )


def from_credentials() -> PubSubBroker:
    credentials = service_account.Credentials.from_service_account_file("key.json")
    return PubSubBroker(project_id="my-project", security=GCPSecurity(credentials))
