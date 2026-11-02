import pytest

from docs.docs_src.consuming import (
    delivery_attempt,
    get_one,
    handler,
    iterate,
    manual_ack,
    workers,
)
from faststream_gcp_pubsub.testing import TestPubSubBroker


@pytest.mark.asyncio()
async def test_handler() -> None:
    async with TestPubSubBroker(handler.broker) as br:
        await br.publish({"id": 1}, "orders", headers={"region": "us"}, ordering_key="k")

        handler.bill.mock.assert_called_once_with({"id": 1})


@pytest.mark.asyncio()
@pytest.mark.parametrize("amount", (-1, 0, 5))
async def test_manual_ack(amount: int) -> None:
    async with TestPubSubBroker(manual_ack.broker) as br:
        await br.publish({"amount": amount}, "orders")

        manual_ack.bill.mock.assert_called_once_with({"amount": amount})


@pytest.mark.asyncio()
async def test_delivery_attempt_is_zero_without_a_service() -> None:
    async with TestPubSubBroker(delivery_attempt.broker) as br:
        with pytest.raises(ValueError, match="retry later"):
            await br.publish({"id": 1}, "orders")


@pytest.mark.asyncio()
async def test_get_one() -> None:
    async with TestPubSubBroker(get_one.broker) as br:
        assert await get_one.read_one() is None

        await br.publish({"id": 1}, "orders")

        assert await get_one.read_one() == {"id": 1}


@pytest.mark.asyncio()
async def test_iterate() -> None:
    async with TestPubSubBroker(iterate.broker) as br:
        for i in range(3):
            await br.publish({"id": i}, "orders")

        assert await iterate.read_all() == [{"id": 0}, {"id": 1}, {"id": 2}]


@pytest.mark.asyncio()
async def test_workers() -> None:
    async with TestPubSubBroker(workers.broker) as br:
        await br.publish({"id": 1}, "orders")

        workers.bill.mock.assert_called_once_with({"id": 1})
