from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, cast

import anyio
import grpc
from google.api_core.client_options import ClientOptions
from google.auth.credentials import AnonymousCredentials
from google.pubsub_v1 import PublisherAsyncClient, SubscriberAsyncClient
from google.pubsub_v1.services.publisher.transports import PublisherGrpcAsyncIOTransport
from google.pubsub_v1.services.subscriber.transports import SubscriberGrpcAsyncIOTransport

if TYPE_CHECKING:
    from google.auth.credentials import Credentials

__all__ = ("ConnectionOptions", "PubSubConnection")


@dataclass(frozen=True, slots=True, kw_only=True)
class ConnectionOptions:
    """How the broker reaches Pub/Sub: recorded by the constructor, used by ``connect()``."""

    emulator_host: str | None
    credentials: "Credentials | None"
    api_endpoint: str | None
    client_options: dict[str, Any] | None


class PubSubConnection:
    """The two async GAPIC clients of one broker and the channel(s) under them."""

    __slots__ = ("_channel", "publisher", "subscriber")

    def __init__(
        self,
        publisher: PublisherAsyncClient,
        subscriber: SubscriberAsyncClient,
        channel: grpc.aio.Channel | None = None,
    ) -> None:
        self.publisher = publisher
        self.subscriber = subscriber
        self._channel = channel

    @classmethod
    def open(cls, options: ConnectionOptions) -> "PubSubConnection":
        """Build the clients. gRPC connects lazily, so this does no network I/O by itself."""
        if options.emulator_host:
            # The emulator speaks plaintext gRPC and checks no credentials; one channel serves
            # both clients.
            channel = grpc.aio.insecure_channel(options.emulator_host)
            return cls(
                PublisherAsyncClient(
                    transport=PublisherGrpcAsyncIOTransport(
                        channel=channel, credentials=AnonymousCredentials()
                    )
                ),
                SubscriberAsyncClient(
                    transport=SubscriberGrpcAsyncIOTransport(
                        channel=channel, credentials=AnonymousCredentials()
                    )
                ),
                channel,
            )

        settings = dict(options.client_options or {})
        if options.api_endpoint:
            settings["api_endpoint"] = options.api_endpoint
        client_options = ClientOptions(**settings) if settings else None
        return cls(
            PublisherAsyncClient(
                credentials=options.credentials, client_options=client_options
            ),
            SubscriberAsyncClient(
                credentials=options.credentials, client_options=client_options
            ),
        )

    async def ready(self, timeout: float) -> bool:
        """Whether the channel connects within ``timeout``; asks for no permission."""
        channels = (
            (self._channel,)
            if self._channel is not None
            else (
                cast(
                    "PublisherGrpcAsyncIOTransport", self.publisher.transport
                ).grpc_channel,
                cast(
                    "SubscriberGrpcAsyncIOTransport", self.subscriber.transport
                ).grpc_channel,
            )
        )
        with anyio.move_on_after(timeout) as scope:
            for channel in channels:
                await channel.channel_ready()
        return not scope.cancelled_caught

    async def close(self) -> None:
        """Close the transports; calls in flight are cancelled."""
        if self._channel is not None:
            await self._channel.close()
            return
        await self.publisher.transport.close()
        await self.subscriber.transport.close()
