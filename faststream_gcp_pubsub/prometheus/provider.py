from typing import TYPE_CHECKING

from faststream.prometheus import ConsumeAttrs, MetricsSettingsProvider
from typing_extensions import override

from faststream_gcp_pubsub.message import PubSubRawMessage
from faststream_gcp_pubsub.response import PubSubPublishCommand
from faststream_gcp_pubsub.schemas import short_name

if TYPE_CHECKING:
    from faststream.message.message import StreamMessage

__all__ = ("PubSubMetricsSettingsProvider",)


class PubSubMetricsSettingsProvider(
    MetricsSettingsProvider[PubSubRawMessage, PubSubPublishCommand],
):
    """Metric labels for Pub/Sub: a delivery is labelled by its subscription."""

    __slots__ = ("messaging_system",)

    def __init__(self) -> None:
        self.messaging_system = "gcp_pubsub"

    @override
    def get_consume_attrs_from_message(
        self,
        msg: "StreamMessage[PubSubRawMessage]",
    ) -> ConsumeAttrs:
        return {
            "destination_name": short_name(msg.raw_message.subscription),
            "message_size": len(msg.body),
            "messages_count": 1,
        }

    @override
    def get_publish_destination_name_from_cmd(
        self,
        cmd: PubSubPublishCommand,
    ) -> str:
        return cmd.destination
