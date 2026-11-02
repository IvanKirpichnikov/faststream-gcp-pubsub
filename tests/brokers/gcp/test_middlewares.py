import pytest

from tests.brokers.base.middlewares import (
    ExceptionMiddlewareTestcase,
    MiddlewareTestcase,
    MiddlewaresOrderTestcase,
)

from .basic import PubSubMemoryTestcaseConfig


@pytest.mark.asyncio()
class TestMiddlewaresOrder(PubSubMemoryTestcaseConfig, MiddlewaresOrderTestcase):
    pass


@pytest.mark.asyncio()
class TestMiddlewares(PubSubMemoryTestcaseConfig, MiddlewareTestcase):
    pass


@pytest.mark.asyncio()
class TestExceptionMiddlewares(PubSubMemoryTestcaseConfig, ExceptionMiddlewareTestcase):
    pass
