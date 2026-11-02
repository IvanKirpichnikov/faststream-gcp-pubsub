import pytest

from docs.docs_src.topics.fan_out import archive, audit, bill, broker
from faststream_gcp_pubsub.testing import TestPubSubBroker


@pytest.mark.asyncio()
async def test_topic_reaches_every_subscription() -> None:
    async with TestPubSubBroker(broker) as br:
        await br.publish({"id": 1}, "orders")

        bill.mock.assert_called_once_with({"id": 1})
        audit.mock.assert_called_once_with({"id": 1})
        archive.mock.assert_not_called()


@pytest.mark.asyncio()
async def test_subscription_defaults_to_its_own_topic() -> None:
    async with TestPubSubBroker(broker) as br:
        await br.publish({"id": 2}, "invoices")

        archive.mock.assert_called_once_with({"id": 2})
        bill.mock.assert_not_called()
