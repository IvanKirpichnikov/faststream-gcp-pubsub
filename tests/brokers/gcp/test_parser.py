import pytest

from tests.brokers.base.parser import CustomParserTestcase

from .basic import PubSubMemoryTestcaseConfig


@pytest.mark.asyncio()
class TestCustomParser(PubSubMemoryTestcaseConfig, CustomParserTestcase):
    pass
