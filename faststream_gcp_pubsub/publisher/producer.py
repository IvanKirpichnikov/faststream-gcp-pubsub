from typing import TYPE_CHECKING, Any, Optional

from faststream._internal.endpoint.utils import ParserComposition
from faststream._internal.parser import DefaultCodec
from faststream._internal.producer import ProducerProto
from faststream.exceptions import FeatureNotSupportedException, IncorrectState
from google.api_core import gapic_v1
from google.pubsub_v1.types import PublishRequest, PubsubMessage
from typing_extensions import override

from faststream_gcp_pubsub.parser import PubSubParser
from faststream_gcp_pubsub.schemas import resource_path

if TYPE_CHECKING:
    from fast_depends.library.serializer import SerializerProto
    from faststream._internal.parser import CodecProto
    from faststream._internal.types import AsyncCallable, CustomCallable

    from faststream_gcp_pubsub.connection import PubSubConnection
    from faststream_gcp_pubsub.response import PubSubPublishCommand

__all__ = ("FakePubSubProducer", "PubSubProducer", "build_attributes")

# Raw protobuf classes: building a proto-plus wrapper per message costs about six times more,
# and the request is wrapped once per call instead.
RawPubsubMessage: Any = PubsubMessage.pb()
RawPublishRequest: Any = PublishRequest.pb()

CORRELATION_ID = "correlation_id"
CONTENT_TYPE = "content-type"
REPLY_TO = "reply_to"

REQUEST_NOT_SUPPORTED = (
    "Pub/Sub has no reply channel for a request: publish with `reply_to` set to a topic your "
    "service subscribes to, and consume the reply there."
)


def build_attributes(
    headers: dict[str, Any] | None,
    *,
    correlation_id: str | None,
    content_type: str | None,
    reply_to: str,
) -> dict[str, str]:
    """Message attributes: the user headers plus FastStream's metadata.

    Attribute values are strings on the wire, so other header values are sent as ``str()``.
    """
    attributes = {
        k: v if isinstance(v, str) else str(v) for k, v in (headers or {}).items()
    }
    if correlation_id:
        attributes[CORRELATION_ID] = correlation_id
    if content_type:
        attributes[CONTENT_TYPE] = content_type
    if reply_to:
        attributes[REPLY_TO] = reply_to
    return attributes


class PubSubProducer(ProducerProto["PubSubPublishCommand"]):
    """Publishes through the async publisher client, one RPC per publish call."""

    __slots__ = (
        "_connection",
        "_decoder",
        "_parser",
        "codec",
        "project_id",
        "serializer",
    )

    _parser: "AsyncCallable"
    _decoder: "AsyncCallable"

    def __init__(
        self,
        parser: Optional["CustomCallable"] = None,
        decoder: Optional["CustomCallable"] = None,
    ) -> None:
        self._connection: PubSubConnection | None = None
        self.serializer: SerializerProto | None = None
        self.codec: CodecProto = DefaultCodec()
        self.project_id = ""

        default = PubSubParser()
        self._parser = ParserComposition(parser, default.parse_message)
        self._decoder = ParserComposition(decoder, default.decode_message)

    def connect(
        self,
        connection: "PubSubConnection",
        *,
        project_id: str,
        serializer: Optional["SerializerProto"],
        codec: Optional["CodecProto"] = None,
    ) -> None:
        self._connection = connection
        self.project_id = project_id
        self.serializer = serializer
        self.codec = codec or DefaultCodec()

    def disconnect(self) -> None:
        self._connection = None

    @property
    def connection(self) -> "PubSubConnection":
        if self._connection is None:
            msg = "Producer is not connected. Call broker.connect() first."
            raise IncorrectState(msg)
        return self._connection

    async def build_request(self, cmd: "PubSubPublishCommand") -> Any:
        """The raw ``PublishRequest`` for every body of the command."""
        request = RawPublishRequest(
            topic=resource_path(self.project_id, "topics", cmd.destination)
        )
        messages = request.messages
        for body in cmd.batch_bodies:
            data, content_type = await self.codec.encode(body, self.serializer)
            messages.add(
                data=data,
                attributes=build_attributes(
                    cmd.headers,
                    correlation_id=cmd.correlation_id,
                    content_type=content_type,
                    reply_to=cmd.reply_to,
                ),
                ordering_key=cmd.ordering_key,
            )
        return request

    @override
    async def publish(self, cmd: "PubSubPublishCommand") -> str:
        ids = await self._send(cmd)
        return ids[0]

    @override
    async def publish_batch(self, cmd: "PubSubPublishCommand") -> list[str]:
        return await self._send(cmd)

    async def _send(self, cmd: "PubSubPublishCommand") -> list[str]:
        connection = self.connection  # a closed broker raises before the encoding work
        request = await self.build_request(cmd)
        response = await connection.publisher.publish(
            request=PublishRequest.wrap(request),
            timeout=gapic_v1.method.DEFAULT if cmd.timeout is None else cmd.timeout,
        )
        return list(response.message_ids)

    @override
    async def request(self, cmd: "PubSubPublishCommand") -> Any:
        raise FeatureNotSupportedException(REQUEST_NOT_SUPPORTED)


class FakePubSubProducer(PubSubProducer):
    """The producer of a broker that is not connected: every publish fails loudly."""

    __slots__ = ()

    def __bool__(self) -> bool:
        return False
