import pytest

from docs.docs_src.observability import otel, prometheus
from faststream_gcp_pubsub.testing import TestPubSubBroker


@pytest.mark.asyncio()
async def test_otel() -> None:
    async with TestPubSubBroker(otel.broker) as br:
        await br.publish({"id": 1}, "orders")

        otel.bill.mock.assert_called_once_with({"id": 1})


@pytest.mark.asyncio()
async def test_prometheus() -> None:
    async with TestPubSubBroker(prometheus.broker) as br:
        await br.publish({"id": 1}, "orders")

        prometheus.bill.mock.assert_called_once_with({"id": 1})
