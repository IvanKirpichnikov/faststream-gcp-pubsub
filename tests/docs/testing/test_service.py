import pytest
from google.api_core.exceptions import InvalidArgument

from docs.docs_src.testing.service import bill, broker, ship
from faststream_gcp_pubsub.testing import TestPubSubBroker


# --8<-- [start:bill]
@pytest.mark.asyncio()
async def test_bill_publishes_a_shipment() -> None:
    async with TestPubSubBroker(broker) as br:
        await br.publish({"id": 1}, "orders")

        bill.mock.assert_called_once_with({"id": 1})
        ship.mock.assert_called_once_with({"order_id": 1})


# --8<-- [end:bill]


# --8<-- [start:invalid]
@pytest.mark.asyncio()
async def test_a_rejected_publish_raises() -> None:
    async with TestPubSubBroker(broker) as br:
        with pytest.raises(InvalidArgument):
            await br.publish({"id": 1}, "orders", ordering_key="k" * 2000)


# --8<-- [end:invalid]


# --8<-- [start:real]
@pytest.mark.gcp()
@pytest.mark.asyncio()
async def test_bill_with_the_emulator() -> None:
    async with TestPubSubBroker(broker, with_real=True) as br:
        await br.publish({"id": 1}, "orders")
        await bill.wait_call(10)

        bill.mock.assert_called_once_with({"id": 1})


# --8<-- [end:real]
