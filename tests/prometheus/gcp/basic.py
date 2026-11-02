from typing import Any

from faststream_gcp_pubsub.prometheus import PubSubPrometheusMiddleware
from faststream_gcp_pubsub.prometheus.provider import PubSubMetricsSettingsProvider
from tests.brokers.gcp.basic import PubSubMemoryTestcaseConfig, PubSubTestcaseConfig


class PubSubPrometheusSettings(PubSubMemoryTestcaseConfig):
    messaging_system = "gcp_pubsub"

    def get_middleware(self, **kwargs: Any) -> PubSubPrometheusMiddleware:
        return PubSubPrometheusMiddleware(**kwargs)

    def get_settings_provider(self) -> PubSubMetricsSettingsProvider:
        return PubSubMetricsSettingsProvider()


class PubSubLivePrometheusSettings(PubSubPrometheusSettings, PubSubTestcaseConfig):
    """The same settings against the emulator."""
