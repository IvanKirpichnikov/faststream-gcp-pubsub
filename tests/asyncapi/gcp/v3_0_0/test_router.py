from typing import Any

from faststream.specification.base import Specification

from faststream_gcp_pubsub import (
    PubSubBroker,
    PubSubPublisher,
    PubSubRoute,
    PubSubRouter,
)
from tests.asyncapi.base.v3_0_0.arguments import ArgumentsTestcase
from tests.asyncapi.base.v3_0_0.publisher import PublisherTestcase
from tests.asyncapi.base.v3_0_0.router import RouterTestcase
from tests.asyncapi.gcp.described_channel import DescribedChannelMixin


class TestRouter(RouterTestcase):
    broker_class = PubSubBroker
    router_class = PubSubRouter
    route_class = PubSubRoute
    publisher_class = PubSubPublisher


class TestRouterArguments(DescribedChannelMixin, ArgumentsTestcase):
    broker_class = PubSubRouter

    def get_spec(self, *broker: Any) -> Specification:
        spec: Specification = super().get_spec(PubSubBroker(routers=broker))
        return spec


class TestRouterPublisher(PublisherTestcase):
    broker_class = PubSubRouter

    def get_spec(self, *broker: Any) -> Specification:
        spec: Specification = super().get_spec(PubSubBroker(routers=broker))
        return spec
