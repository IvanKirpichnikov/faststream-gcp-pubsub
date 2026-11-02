import contextlib
from collections.abc import Iterable
from typing import TYPE_CHECKING, Any, Union

from faststream._internal.endpoint.publisher import PublisherUsecase
from faststream.response.publish_type import PublishType
from google.api_core.exceptions import AlreadyExists
from typing_extensions import override

from faststream_gcp_pubsub.response import PubSubPublishCommand

if TYPE_CHECKING:
    from faststream._internal.basic_types import SendableMessage
    from faststream._internal.endpoint.publisher import PublisherSpecification
    from faststream._internal.types import PublisherMiddleware
    from faststream.response.response import PublishCommand

    from faststream_gcp_pubsub.broker.config import PubSubBrokerConfig
    from faststream_gcp_pubsub.schemas import PubSubTopic

    from .config import PubSubPublisherConfig


class PubSubPublisher(PublisherUsecase):
    """Publisher to a Pub/Sub topic."""

    __slots__ = ("_topic", "headers", "ordering_key")

    _outer_config: "PubSubBrokerConfig"

    def __init__(
        self,
        config: "PubSubPublisherConfig",
        specification: "PublisherSpecification[Any, Any]",
    ) -> None:
        super().__init__(config, specification)

        self._topic = config.topic
        self.ordering_key = config.ordering_key
        self.headers = config.headers or {}

    @property
    def topic(self) -> str:
        """The topic name, router prefix included."""
        return f"{self._outer_config.prefix}{self._topic.name}"

    @property
    def topic_schema(self) -> "PubSubTopic":
        """The declaration this publisher was created with."""
        return self._topic

    @override
    async def start(self) -> None:
        await super().start()
        if self._topic.declare:
            config = self._outer_config
            with contextlib.suppress(AlreadyExists):
                await config.connection.publisher.create_topic(
                    request=self._topic.to_proto(config.project_id)
                )

    @override
    async def publish(
        self,
        message: "SendableMessage",
        topic: str = "",
        *,
        headers: dict[str, str] | None = None,
        ordering_key: str | None = None,
        correlation_id: str | None = None,
        reply_to: str = "",
        timeout: float | None = None,
    ) -> str:
        """Publish a message.

        Args:
            message: the message body.
            topic: a topic other than this publisher's.
            headers: attributes added to the publisher's own.
            ordering_key: an ordering key other than this publisher's.
            correlation_id: the correlation id; generated when omitted.
            reply_to: the topic a consumer sends its reply to.
            timeout: the RPC deadline in seconds; the client's default when omitted.

        Returns:
            The message id the service assigned.
        """
        cmd = PubSubPublishCommand(
            message,
            topic=topic or self.topic,
            headers=self.headers | (headers or {}),
            ordering_key=self.ordering_key if ordering_key is None else ordering_key,
            correlation_id=correlation_id or self._outer_config.id_generator(),
            reply_to=reply_to,
            timeout=timeout,
            _publish_type=PublishType.PUBLISH,
        )
        result: str = await self._basic_publish(
            cmd,
            producer=self._outer_config.producer,
            _extra_middlewares=(),
        )
        return result

    async def publish_batch(
        self,
        *messages: "SendableMessage",
        topic: str = "",
        headers: dict[str, str] | None = None,
        ordering_key: str | None = None,
        correlation_id: str | None = None,
        reply_to: str = "",
        timeout: float | None = None,
    ) -> list[str]:
        """Publish several messages in one request.

        Returns:
            The message ids, in the order of the messages.
        """
        cmd = PubSubPublishCommand(
            *messages,
            topic=topic or self.topic,
            headers=self.headers | (headers or {}),
            ordering_key=self.ordering_key if ordering_key is None else ordering_key,
            correlation_id=correlation_id or self._outer_config.id_generator(),
            reply_to=reply_to,
            timeout=timeout,
            _publish_type=PublishType.PUBLISH,
        )
        result: list[str] = await self._basic_publish_batch(
            cmd,
            producer=self._outer_config.producer,
            _extra_middlewares=(),
        )
        return result

    @override
    async def _publish(
        self,
        cmd: Union["PublishCommand", "PubSubPublishCommand"],
        *,
        _extra_middlewares: Iterable["PublisherMiddleware"],
    ) -> None:
        """Called in subscriber flow only."""
        cmd = PubSubPublishCommand.from_cmd(cmd)

        cmd.destination = cmd.destination or self.topic
        cmd.add_headers(self.headers, override=False)
        cmd.ordering_key = cmd.ordering_key or self.ordering_key

        await self._basic_publish(
            cmd,
            producer=self._outer_config.producer,
            _extra_middlewares=_extra_middlewares,
        )

    @override
    async def request(
        self,
        message: "SendableMessage",
        topic: str = "",
        *,
        correlation_id: str | None = None,
        timeout: float | None = None,
    ) -> Any:
        """Not available on Pub/Sub; raises ``FeatureNotSupportedException``."""
        cmd = PubSubPublishCommand(
            message,
            topic=topic or self.topic,
            correlation_id=correlation_id or self._outer_config.id_generator(),
            timeout=timeout,
            _publish_type=PublishType.REQUEST,
        )
        return await self._basic_request(cmd, producer=self._outer_config.producer)
