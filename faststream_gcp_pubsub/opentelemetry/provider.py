from typing import TYPE_CHECKING, Any

from faststream.opentelemetry import TelemetrySettingsProvider
from faststream.opentelemetry.consts import MESSAGING_DESTINATION_PUBLISH_NAME
from opentelemetry.semconv.trace import SpanAttributes
from typing_extensions import override

from faststream_gcp_pubsub.message import PubSubRawMessage
from faststream_gcp_pubsub.response import PubSubPublishCommand
from faststream_gcp_pubsub.schemas import short_name

if TYPE_CHECKING:
    from faststream.message import StreamMessage

__all__ = ("PubSubTelemetrySettingsProvider",)

# OpenTelemetry semantic conventions for Pub/Sub; they live in semconv's private
# `_incubating` package, whose layout changes between releases, so the values are kept here.
MESSAGING_SYSTEM = "gcp_pubsub"
MESSAGING_GCP_PUBSUB_MESSAGE_ORDERING_KEY = "messaging.gcp_pubsub.message.ordering_key"


class PubSubTelemetrySettingsProvider(
    TelemetrySettingsProvider[PubSubRawMessage, PubSubPublishCommand],
):
    """Span attributes for Pub/Sub.

    A delivery does not carry its topic, so the consume side is named by the subscription.
    A batch publish is counted by the middleware from the command's bodies.
    """

    __slots__ = ("messaging_system",)

    def __init__(self) -> None:
        self.messaging_system = MESSAGING_SYSTEM

    @override
    def get_consume_attrs_from_message(
        self,
        msg: "StreamMessage[PubSubRawMessage]",
    ) -> dict[str, Any]:
        attrs: dict[str, Any] = {
            SpanAttributes.MESSAGING_SYSTEM: self.messaging_system,
            SpanAttributes.MESSAGING_MESSAGE_ID: msg.message_id,
            SpanAttributes.MESSAGING_MESSAGE_CONVERSATION_ID: msg.correlation_id,
            SpanAttributes.MESSAGING_MESSAGE_PAYLOAD_SIZE_BYTES: len(msg.body),
            MESSAGING_DESTINATION_PUBLISH_NAME: short_name(msg.raw_message.subscription),
        }
        if ordering_key := msg.raw_message.ordering_key:
            attrs[MESSAGING_GCP_PUBSUB_MESSAGE_ORDERING_KEY] = ordering_key
        return attrs

    @override
    def get_consume_destination_name(
        self,
        msg: "StreamMessage[PubSubRawMessage]",
    ) -> str:
        return short_name(msg.raw_message.subscription)

    @override
    def get_publish_attrs_from_cmd(
        self,
        cmd: PubSubPublishCommand,
    ) -> dict[str, Any]:
        attrs: dict[str, Any] = {
            SpanAttributes.MESSAGING_SYSTEM: self.messaging_system,
            SpanAttributes.MESSAGING_DESTINATION_NAME: cmd.destination,
            SpanAttributes.MESSAGING_MESSAGE_CONVERSATION_ID: cmd.correlation_id,
        }
        if cmd.ordering_key:
            attrs[MESSAGING_GCP_PUBSUB_MESSAGE_ORDERING_KEY] = cmd.ordering_key
        return attrs

    @override
    def get_publish_destination_name(
        self,
        cmd: PubSubPublishCommand,
    ) -> str:
        return cmd.destination
