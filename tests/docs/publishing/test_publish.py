import pytest

from docs.docs_src.publishing.publish import bill, broker, place_orders
from docs.docs_src.publishing.publisher import (
    bill as bill_via_publisher,
    broker as publisher_broker,
    place_order,
)
from faststream_gcp_pubsub.testing import TestPubSubBroker


@pytest.mark.asyncio()
async def test_publish() -> None:
    async with TestPubSubBroker(broker):
        await place_orders()

        assert bill.mock.call_count == 3
        bill.mock.assert_any_call({"id": 1})
        bill.mock.assert_any_call({"id": 3})


@pytest.mark.asyncio()
async def test_publisher() -> None:
    async with TestPubSubBroker(publisher_broker):
        await place_order()

        assert bill_via_publisher.mock.call_count == 2
