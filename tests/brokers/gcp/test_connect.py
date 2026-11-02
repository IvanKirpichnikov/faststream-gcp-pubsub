import pytest

from faststream_gcp_pubsub import PubSubBroker

from .conftest import Settings


def test_constructor_does_no_io() -> None:
    broker = PubSubBroker(project_id="p", emulator_host="localhost:1")

    assert broker._connection is None


@pytest.mark.gcp()
@pytest.mark.asyncio()
async def test_connect_and_ping(settings: Settings) -> None:
    broker = PubSubBroker(
        project_id=settings.project_id, emulator_host=settings.emulator_host
    )

    async with broker:
        await broker.connect()
        assert await broker.ping(timeout=5)

    assert not await broker.ping(timeout=1)


@pytest.mark.gcp()
@pytest.mark.asyncio()
async def test_ping_fails_without_server() -> None:
    broker = PubSubBroker(project_id="p", emulator_host="localhost:1")

    async with broker:
        await broker.connect()
        assert not await broker.ping(timeout=0.5)
