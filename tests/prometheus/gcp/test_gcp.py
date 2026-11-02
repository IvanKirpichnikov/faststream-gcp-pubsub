import asyncio
from typing import Any

import pytest
from faststream.exceptions import FeatureNotSupportedException
from prometheus_client import CollectorRegistry

from faststream_gcp_pubsub import PubSubBroker
from faststream_gcp_pubsub.prometheus import PubSubPrometheusMiddleware
from tests.brokers.gcp.test_consume import TestConsume as ConsumeCase
from tests.brokers.gcp.test_publish import TestPublish as PublishCase
from tests.prometheus.basic import (
    LocalMetricsSettingsProviderTestcase,
    LocalPrometheusTestcase,
)

from .basic import PubSubLivePrometheusSettings, PubSubPrometheusSettings


class RequestNotSupported:
    async def test_rpc_request(self, queue: str, event: asyncio.Event) -> None:
        # Pub/Sub has no request/reply: the metrics of a request cannot exist.
        broker = self.get_broker(  # type: ignore[attr-defined]
            middlewares=(self.get_middleware(registry=CollectorRegistry()),)  # type: ignore[attr-defined]
        )
        async with self.patch_broker(broker) as br:  # type: ignore[attr-defined]
            await br.start()
            with pytest.raises(FeatureNotSupportedException):
                await br.request("", queue)


@pytest.mark.asyncio()
class TestPrometheus(
    RequestNotSupported, PubSubPrometheusSettings, LocalPrometheusTestcase
):
    pass


class TestMetricsSettingsProvider(
    PubSubPrometheusSettings, LocalMetricsSettingsProviderTestcase
):
    pass


@pytest.mark.connected()
@pytest.mark.gcp()
@pytest.mark.asyncio()
class TestPrometheusLive(
    RequestNotSupported, PubSubLivePrometheusSettings, LocalPrometheusTestcase
):
    pass


@pytest.mark.connected()
@pytest.mark.gcp()
class TestPublishWithPrometheus(PublishCase):
    def get_broker(self, apply_types: bool = False, **kwargs: Any) -> PubSubBroker:
        return super().get_broker(
            apply_types=apply_types,
            middlewares=(PubSubPrometheusMiddleware(registry=CollectorRegistry()),),
            **kwargs,
        )


@pytest.mark.connected()
@pytest.mark.gcp()
class TestConsumeWithPrometheus(ConsumeCase):
    def get_broker(self, apply_types: bool = False, **kwargs: Any) -> PubSubBroker:
        return super().get_broker(
            apply_types=apply_types,
            middlewares=(PubSubPrometheusMiddleware(registry=CollectorRegistry()),),
            **kwargs,
        )
