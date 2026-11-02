import pytest

from faststream_gcp_pubsub import PubSubPublisher, PubSubRoute
from tests.brokers.base.include_router import (
    IncludePublisherTestcase,
    IncludeSubscriberTestcase,
)
from tests.brokers.base.router import RouterLocalTestcase, RouterTestcase

from .basic import PubSubMemoryTestcaseConfig, PubSubTestcaseConfig


@pytest.mark.connected()
@pytest.mark.gcp()
@pytest.mark.asyncio()
class TestRouter(PubSubTestcaseConfig, RouterTestcase):
    route_class = PubSubRoute
    publisher_class = PubSubPublisher


@pytest.mark.asyncio()
class TestRouterLocal(PubSubMemoryTestcaseConfig, RouterLocalTestcase):
    route_class = PubSubRoute
    publisher_class = PubSubPublisher


class TestIncludeSubscriber(PubSubMemoryTestcaseConfig, IncludeSubscriberTestcase):
    pass


class TestIncludePublisher(PubSubMemoryTestcaseConfig, IncludePublisherTestcase):
    pass
