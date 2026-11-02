import pytest
from faststream.security import SASLPlaintext
from google.auth.credentials import AnonymousCredentials

from faststream_gcp_pubsub import GCPSecurity, PubSubBroker


def test_security_carries_credentials() -> None:
    credentials = AnonymousCredentials()

    broker = PubSubBroker(project_id="p", security=GCPSecurity(credentials))

    assert broker._connection_options.credentials is credentials


def test_security_is_in_the_specification() -> None:
    broker = PubSubBroker(project_id="p", security=GCPSecurity(AnonymousCredentials()))

    assert broker.specification.security is not None
    assert broker.specification.security.get_schema() == {
        "google-oauth2": {"type": "oauth2"}
    }


def test_foreign_security_is_refused() -> None:
    with pytest.raises(NotImplementedError, match="GCPSecurity"):
        PubSubBroker(project_id="p", security=SASLPlaintext(username="u", password="p"))


def test_emulator_host_comes_from_the_environment(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("PUBSUB_EMULATOR_HOST", "localhost:9999")
    monkeypatch.setenv("GOOGLE_CLOUD_PROJECT", "from-env")

    broker = PubSubBroker()

    assert broker._connection_options.emulator_host == "localhost:9999"
    assert broker.project_id == "from-env"


def test_explicit_none_ignores_the_emulator_variable(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("PUBSUB_EMULATOR_HOST", "localhost:9999")

    broker = PubSubBroker(project_id="p", emulator_host=None)

    assert broker._connection_options.emulator_host is None
    assert broker.specification.url == ["pubsub.googleapis.com:443"]


@pytest.mark.asyncio()
async def test_connect_without_project_is_refused(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from faststream.exceptions import IncorrectState

    monkeypatch.delenv("GOOGLE_CLOUD_PROJECT", raising=False)
    broker = PubSubBroker(emulator_host="localhost:1")

    with pytest.raises(IncorrectState, match="project_id"):
        await broker.connect()
