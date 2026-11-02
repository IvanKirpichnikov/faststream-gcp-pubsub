import pytest

from docs.docs_src.leases import exactly_once, flow_control
from faststream_gcp_pubsub.testing import TestPubSubBroker


@pytest.mark.asyncio()
async def test_flow_control() -> None:
    async with TestPubSubBroker(flow_control.broker) as br:
        await br.publish({"id": 1}, "orders")

        flow_control.bill.mock.assert_called_once_with({"id": 1})


@pytest.mark.asyncio()
async def test_exactly_once() -> None:
    async with TestPubSubBroker(exactly_once.broker) as br:
        await br.publish({"id": 1}, "orders")

        exactly_once.bill.mock.assert_called_once_with({"id": 1})
