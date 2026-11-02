import pytest

from tests.brokers.base.codec import CodecTestcase

from .basic import PubSubMemoryTestcaseConfig


@pytest.mark.asyncio()
class TestCodec(PubSubMemoryTestcaseConfig, CodecTestcase):
    pass
