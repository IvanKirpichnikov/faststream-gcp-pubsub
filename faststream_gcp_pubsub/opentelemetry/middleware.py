from faststream.opentelemetry.middleware import TelemetryMiddleware
from opentelemetry.metrics import Meter, MeterProvider
from opentelemetry.trace import TracerProvider

from faststream_gcp_pubsub.opentelemetry.provider import PubSubTelemetrySettingsProvider
from faststream_gcp_pubsub.response import PubSubPublishCommand

__all__ = ("PubSubTelemetryMiddleware",)


class PubSubTelemetryMiddleware(TelemetryMiddleware[PubSubPublishCommand]):
    """Traces and measures Pub/Sub publishes and deliveries with OpenTelemetry."""

    def __init__(
        self,
        *,
        tracer_provider: TracerProvider | None = None,
        meter_provider: MeterProvider | None = None,
        meter: Meter | None = None,
        include_messages_counters: bool = True,
    ) -> None:
        super().__init__(
            settings_provider_factory=lambda _: PubSubTelemetrySettingsProvider(),
            tracer_provider=tracer_provider,
            meter_provider=meter_provider,
            meter=meter,
            include_messages_counters=include_messages_counters,
        )
