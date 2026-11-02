import pytest

from docs.docs_src.routers.router import bill, broker, notify
from faststream_gcp_pubsub.testing import TestPubSubBroker


@pytest.mark.asyncio()
async def test_prefix_applies_to_topics_and_subscriptions() -> None:
    async with TestPubSubBroker(broker) as br:
        await br.publish({"id": 1}, "billing-orders")

        bill.mock.assert_called_once_with({"id": 1})


@pytest.mark.asyncio()
async def test_route() -> None:
    async with TestPubSubBroker(broker) as br:
        await br.publish({"id": 1}, "shop-receipts")

        assert notify is not None
