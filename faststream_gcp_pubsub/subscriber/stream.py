import asyncio
import logging
from collections.abc import AsyncIterator
from typing import TYPE_CHECKING, Any
from uuid import uuid4

from google.api_core import exceptions
from google.pubsub_v1.types import StreamingPullRequest, StreamingPullResponse

if TYPE_CHECKING:
    from google.pubsub_v1 import SubscriberAsyncClient

    from .settler import Log, Settler

__all__ = ("StreamingPull",)

# The codes the official client reopens a stream on; any other code ends the subscriber.
RETRYABLE = (
    exceptions.Aborted,
    exceptions.DeadlineExceeded,
    exceptions.GatewayTimeout,
    exceptions.InternalServerError,
    exceptions.ResourceExhausted,
    exceptions.ServiceUnavailable,
    exceptions.Unknown,
)

# The service closes a stream it hears nothing on; an empty request keeps it open.
HEARTBEAT = 30.0
MAX_BACKOFF = 10.0


class StreamingPull:
    """Reads one subscription through a streaming pull, reopening the stream on transient errors.

    Yields raw ``ReceivedMessage`` protobufs, each already leased in the settler.
    """

    __slots__ = ("_call", "_client", "_client_id", "_log", "_settler", "_stopped", "path")

    def __init__(
        self,
        client: "SubscriberAsyncClient",
        path: str,
        settler: "Settler",
        log: "Log",
    ) -> None:
        self._client = client
        self.path = path
        self._settler = settler
        self._log = log
        # One id for every stream of this subscriber, so the service keeps ordered keys on it.
        self._client_id = uuid4().hex
        self._call: Any = None
        self._stopped = False

    async def _requests(self) -> AsyncIterator[StreamingPullRequest]:
        flow = self._settler.flow
        yield StreamingPullRequest(
            subscription=self.path,
            stream_ack_deadline_seconds=flow.ack_deadline,
            max_outstanding_messages=flow.max_messages,
            max_outstanding_bytes=flow.max_bytes,
            client_id=self._client_id,
        )
        while True:
            await asyncio.sleep(HEARTBEAT)
            yield StreamingPullRequest()

    async def __aiter__(self) -> AsyncIterator[Any]:
        attempt = 0
        settler = self._settler
        while not self._stopped:
            try:
                self._call = await self._client.streaming_pull(
                    requests=self._requests(),
                    metadata=(("x-goog-request-params", f"subscription={self.path}"),),
                )
                async for response in self._call:
                    attempt = 0
                    raw = StreamingPullResponse.pb(response)
                    if raw.HasField("subscription_properties"):
                        settler.exactly_once = (
                            raw.subscription_properties.exactly_once_delivery_enabled
                        )
                    for received in raw.received_messages:
                        await settler.lease(received.ack_id)
                        yield received
            # the stream is reopened in this loop, so the handler belongs inside it
            except exceptions.GoogleAPICallError as e:  # noqa: PERF203
                if self._stopped:
                    return
                if not isinstance(e, RETRYABLE):
                    raise
                attempt += 1
                delay = min(0.1 * 2**attempt, MAX_BACKOFF)
                self._log(
                    f"Streaming pull of {self.path} interrupted ({e!r}), reopening in {delay:.1f}s",
                    logging.WARNING,
                )
                await asyncio.sleep(delay)
            except asyncio.CancelledError:
                if self._stopped:
                    return
                raise
            finally:
                self._call = None

    def stop(self) -> None:
        """Stop reading: the stream is cancelled, a delivery being handled is not."""
        self._stopped = True
        if self._call is not None:
            self._call.cancel()
