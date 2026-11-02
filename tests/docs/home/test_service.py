import pytest

from docs.docs_src.home.service import Order, bill, broker, shipments
from faststream_gcp_pubsub.testing import TestPubSubBroker


@pytest.mark.asyncio()
async def test_service() -> None:
    async with TestPubSubBroker(broker) as br:
        await br.publish(Order(id=1, amount=9.5), "orders")

        bill.mock.assert_called_once_with({"id": 1, "amount": 9.5})
        shipments.mock.assert_called_once_with({"order_id": 1})
