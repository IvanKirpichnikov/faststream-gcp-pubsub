import pytest

from docs.docs_src.emulator import credentials, emulator, endpoint
from faststream_gcp_pubsub.testing import TestPubSubBroker


@pytest.mark.asyncio()
async def test_emulator() -> None:
    async with TestPubSubBroker(emulator.broker) as br:
        await br.publish({"id": 1}, "orders")

        emulator.bill.mock.assert_called_once_with({"id": 1})


def test_credentials_and_endpoint_build_brokers() -> None:
    assert callable(credentials.from_key_file)
    assert callable(credentials.from_credentials)
    assert endpoint.broker.project_id == "my-project"
