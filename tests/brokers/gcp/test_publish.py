import pytest
from google.api_core.exceptions import NotFound

from tests.brokers.base.publish import BrokerPublishTestcase

from .basic import PubSubTestcaseConfig


@pytest.mark.connected()
@pytest.mark.gcp()
@pytest.mark.asyncio()
class TestPublish(PubSubTestcaseConfig, BrokerPublishTestcase):
    async def test_publisher_after_connect(self, queue: str) -> None:
        # The service refuses a publish to a topic nobody created.
        async with self.patch_broker(self.get_broker()) as br:
            with pytest.raises(NotFound):
                await br.publisher(queue).publish(None)
