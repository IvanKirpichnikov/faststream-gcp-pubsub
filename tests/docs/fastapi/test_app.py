import pytest

from docs.docs_src.fastapi.app import bill, router
from faststream_gcp_pubsub.testing import TestPubSubBroker


@pytest.mark.asyncio()
async def test_router() -> None:
    async with TestPubSubBroker(router.broker) as br:
        await br.publish({"id": 1}, "orders")

        bill.mock.assert_called_once_with({"id": 1})
