import pytest
from faststream.exceptions import FeatureNotSupportedException

from docs.docs_src.replies import reply_to, response
from faststream_gcp_pubsub.testing import TestPubSubBroker


@pytest.mark.asyncio()
async def test_reply_to() -> None:
    async with TestPubSubBroker(reply_to.broker):
        await reply_to.submit()

        reply_to.run.mock.assert_called_once_with({"id": 7})
        reply_to.collect.mock.assert_called_once_with({"done": True, "job": 7})


@pytest.mark.asyncio()
async def test_response() -> None:
    async with TestPubSubBroker(response.broker) as br:
        await br.publish({"owner": "u1"}, "jobs", reply_to="results")

        response.collect.mock.assert_called_once_with({"done": True})


@pytest.mark.asyncio()
async def test_request_is_not_supported() -> None:
    async with TestPubSubBroker(reply_to.broker) as br:
        with pytest.raises(FeatureNotSupportedException):
            await br.request({"id": 7}, "jobs")
