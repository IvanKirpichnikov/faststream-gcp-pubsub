import pytest

from docs.docs_src.resources.declare import bill, broker
from docs.docs_src.resources.manual import (
    broker as manual_broker,
    declare,
)
from faststream_gcp_pubsub.testing import TestPubSubBroker


@pytest.mark.asyncio()
async def test_declared_subscription() -> None:
    async with TestPubSubBroker(broker) as br:
        await br.publish({"id": 1}, "orders", headers={"region": "eu"})

        bill.mock.assert_called_once_with({"id": 1})


@pytest.mark.asyncio()
async def test_manual_declaration() -> None:
    async with TestPubSubBroker(manual_broker):
        await declare()
