from typing import Any

from faststream_gcp_pubsub.prometheus import PubSubPrometheusMiddleware
from faststream_gcp_pubsub.prometheus.provider import PubSubMetricsSettingsProvider
from tests.brokers.gcp.basic import PubSubInProcessTestcaseConfig, PubSubTestcaseConfig


class PrometheusSettings:
    messaging_system = "gcp_pubsub"

    def get_middleware(self, **kwargs: Any) -> PubSubPrometheusMiddleware:
        return PubSubPrometheusMiddleware(**kwargs)

    def get_settings_provider(self) -> PubSubMetricsSettingsProvider:
        return PubSubMetricsSettingsProvider()


class PubSubPrometheusSettings(PrometheusSettings, PubSubInProcessTestcaseConfig):
    """In process: every broker goes through ``TestPubSubBroker``."""


class PubSubLivePrometheusSettings(PrometheusSettings, PubSubTestcaseConfig):
    """The same settings against the emulator."""
