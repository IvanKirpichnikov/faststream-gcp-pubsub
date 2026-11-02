import pytest

from docs.docs_src.getting_started.emulator import (
    broker as emulator_broker,
    handle as emulator_handle,
)
from docs.docs_src.getting_started.service import broker, handle
from faststream_gcp_pubsub.testing import TestPubSubBroker


# --8<-- [start:test]
@pytest.mark.asyncio()
async def test_service() -> None:
    async with TestPubSubBroker(broker) as br:
        await br.publish({"id": 1}, "orders")

        handle.mock.assert_called_once_with({"id": 1})


# --8<-- [end:test]


@pytest.mark.gcp()
@pytest.mark.asyncio()
async def test_emulator_service() -> None:
    async with TestPubSubBroker(emulator_broker, with_real=True) as br:
        await br.publish({"id": 1}, "orders")
        await emulator_handle.wait_call(10)

        emulator_handle.mock.assert_called_once_with({"id": 1})
