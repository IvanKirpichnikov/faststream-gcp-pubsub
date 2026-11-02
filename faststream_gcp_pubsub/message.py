from typing import TYPE_CHECKING, Any, Protocol

from faststream.message import StreamMessage
from typing_extensions import override

if TYPE_CHECKING:
    from datetime import datetime

__all__ = ("Acker", "PubSubMessage", "PubSubRawMessage")


class Acker(Protocol):
    """Settles deliveries of one subscription."""

    async def ack(self, message: "PubSubRawMessage") -> None: ...

    async def nack(self, message: "PubSubRawMessage") -> None: ...


class PubSubRawMessage:
    """One delivery: the received protobuf message and the subscription that settles it."""

    __slots__ = ("acker", "received", "subscription")

    def __init__(self, received: Any, subscription: str, acker: Acker) -> None:
        # `received` is the raw `ReceivedMessage` protobuf: reading its fields copies nothing.
        self.received = received
        self.subscription = subscription
        self.acker = acker

    @property
    def ack_id(self) -> str:
        """The handle the service settles this delivery by."""
        ack_id: str = self.received.ack_id
        return ack_id

    @property
    def data(self) -> bytes:
        """The payload."""
        data: bytes = self.received.message.data
        return data

    @property
    def attributes(self) -> dict[str, str]:
        """The attributes, as a new dict."""
        return dict(self.received.message.attributes)

    @property
    def message_id(self) -> str:
        """The id the service gave the message at publish."""
        message_id: str = self.received.message.message_id
        return message_id

    @property
    def ordering_key(self) -> str:
        """The ordering key, empty when the message has none."""
        key: str = self.received.message.ordering_key
        return key

    @property
    def publish_time(self) -> "datetime":
        """When the service received the message."""
        time: datetime = self.received.message.publish_time.ToDatetime()
        return time

    @property
    def delivery_attempt(self) -> int:
        """The delivery attempt; 0 unless the subscription has a dead-letter policy."""
        attempt: int = self.received.delivery_attempt
        return attempt


class PubSubMessage(StreamMessage[PubSubRawMessage]):
    """A Pub/Sub message in a handler.

    ``ack`` acknowledges the delivery, ``nack`` makes it available for redelivery at once
    (an ack deadline of zero), and ``reject`` acknowledges it too: Pub/Sub has no reject, and a
    dead-letter policy is how a message that keeps failing leaves the subscription.
    """

    @property
    def ordering_key(self) -> str:
        """The ordering key, empty when the message has none."""
        return self.raw_message.ordering_key

    @property
    def delivery_attempt(self) -> int:
        """The delivery attempt; 0 unless the subscription has a dead-letter policy."""
        return self.raw_message.delivery_attempt

    @override
    async def ack(self) -> None:
        if self.committed is None:
            await self.raw_message.acker.ack(self.raw_message)
        await super().ack()

    @override
    async def nack(self) -> None:
        if self.committed is None:
            await self.raw_message.acker.nack(self.raw_message)
        await super().nack()

    @override
    async def reject(self) -> None:
        if self.committed is None:
            await self.raw_message.acker.ack(self.raw_message)
        await super().reject()
