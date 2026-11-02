import asyncio
import logging
import time
from collections.abc import Awaitable, Callable, Sequence
from dataclasses import dataclass
from typing import TYPE_CHECKING

from faststream.exceptions import IncorrectState

if TYPE_CHECKING:
    from faststream_gcp_pubsub.message import PubSubRawMessage

__all__ = ("FlowControl", "Settler")

# The service takes at most this many ack ids in one acknowledge / modify_ack_deadline call.
MAX_IDS_PER_REQUEST = 1000

Send = Callable[[Sequence[str]], Awaitable[None]]
Extend = Callable[[Sequence[str], int], Awaitable[None]]
# (message, level): the broker's logger with the subscriber's log context bound
Log = Callable[[str, int], None]


@dataclass(frozen=True, slots=True, kw_only=True)
class FlowControl:
    """How a subscriber leases and settles deliveries.

    Attributes:
        max_messages: deliveries held at once, unsettled; the stream is not read further
            until one settles.
        max_bytes: payload bytes held at once; the service stops sending past it.
        ack_deadline: seconds a lease lasts before it is extended, 10 to 600.
        max_lease: seconds a delivery is held at most; past it the lease is no longer
            extended and the service redelivers the message.
        ack_batch_wait: seconds acks and nacks wait to be sent together.
    """

    max_messages: int = 1000
    max_bytes: int = 100 * 1024 * 1024
    ack_deadline: int = 60
    max_lease: float = 3600.0
    ack_batch_wait: float = 0.05

    def __post_init__(self) -> None:
        if self.max_messages < 1:
            msg = "max_messages must be at least 1"
            raise ValueError(msg)
        if not 10 <= self.ack_deadline <= 600:
            msg = "ack_deadline must be within 10..600 seconds"
            raise ValueError(msg)


class _Batch:
    """Ack ids waiting to be sent, and the waiters of an exactly-once subscription."""

    __slots__ = ("done", "ids")

    def __init__(self) -> None:
        self.ids: list[str] = []
        self.done: asyncio.Future[None] | None = None

    def future(self) -> "asyncio.Future[None]":
        if self.done is None:
            self.done = asyncio.get_running_loop().create_future()
        return self.done


class Settler:
    """Leases, settles and flow-controls the deliveries of one subscription.

    Acks and nacks are coalesced into one request per ``ack_batch_wait`` or per 1000 ids.
    ``ack()`` returns once the id is queued, unless the subscription has exactly-once
    delivery: then it waits for the service's answer and raises on a failure.
    """

    __slots__ = (
        "_acks",
        "_closed",
        "_extend",
        "_flusher",
        "_leased",
        "_leaser",
        "_log",
        "_nacks",
        "_send_ack",
        "_slots",
        "_wake",
        "exactly_once",
        "flow",
    )

    def __init__(
        self,
        *,
        flow: FlowControl,
        send_ack: Send,
        extend: Extend,
        log: Log,
    ) -> None:
        self.flow = flow
        self.exactly_once = False
        self._send_ack = send_ack
        self._extend = extend
        self._log = log

        # ack_id -> monotonic time the lease started; insertion order is lease age
        self._leased: dict[str, float] = {}
        self._slots = asyncio.Semaphore(flow.max_messages)
        self._acks = _Batch()
        self._nacks = _Batch()
        self._wake = asyncio.Event()
        self._closed = False
        self._flusher: asyncio.Task[None] | None = None
        self._leaser: asyncio.Task[None] | None = None

    @property
    def leased(self) -> int:
        """Deliveries held and not settled."""
        return len(self._leased)

    def start(self) -> None:
        if self._flusher is None:
            self._closed = False
            self._flusher = asyncio.create_task(self._flush_loop())
            self._leaser = asyncio.create_task(self._lease_loop())

    async def lease(self, ack_id: str) -> None:
        """Hold a delivery; waits while ``max_messages`` deliveries are held."""
        self._leased[ack_id] = time.monotonic()
        await self._slots.acquire()

    def _release(self, ack_id: str) -> bool:
        if self._leased.pop(ack_id, None) is None:
            # settled twice, or dropped after max_lease: the slot is already free
            return False
        self._slots.release()
        return True

    async def ack(self, message: "PubSubRawMessage") -> None:
        await self._settle(message.ack_id, self._acks)

    async def nack(self, message: "PubSubRawMessage") -> None:
        await self._settle(message.ack_id, self._nacks)

    async def _settle(self, ack_id: str, batch: _Batch) -> None:
        if self._closed:
            msg = "The subscriber is stopped: the delivery can no longer be settled."
            raise IncorrectState(msg)
        if not self._release(ack_id):
            return
        batch.ids.append(ack_id)
        waiter = batch.future() if self.exactly_once else None
        if len(batch.ids) >= MAX_IDS_PER_REQUEST or waiter is not None:
            self._wake.set()
        if waiter is not None:
            await asyncio.shield(waiter)

    async def _flush_loop(self) -> None:
        while True:
            await self._wake.wait()
            # gather what arrives meanwhile into the same request
            await asyncio.sleep(self.flow.ack_batch_wait)
            self._wake.clear()
            await self.flush()

    async def flush(self) -> None:
        """Send every queued ack and nack now."""
        acks, self._acks = self._acks, _Batch()
        nacks, self._nacks = self._nacks, _Batch()
        await self._send(acks, self._send_ack)
        await self._send(nacks, self._send_nack)

    async def _send_nack(self, ids: Sequence[str]) -> None:
        await self._extend(ids, 0)

    async def _send(self, batch: _Batch, send: Send) -> None:
        if not batch.ids:
            return
        error: BaseException | None = None
        for start in range(0, len(batch.ids), MAX_IDS_PER_REQUEST):
            # Without exactly-once the service redelivers what it did not take: the failure
            # is reported and the delivery is not lost.
            error = (
                await self._attempt(
                    send(batch.ids[start : start + MAX_IDS_PER_REQUEST]),
                    f"Settling {len(batch.ids)} deliveries",
                )
                or error
            )
        if batch.done is not None and not batch.done.done():
            if error is None:
                batch.done.set_result(None)
            else:
                batch.done.set_exception(error)

    async def _lease_loop(self) -> None:
        while True:
            # extend before the deadline passes, with room for the request itself
            await asyncio.sleep(self.flow.ack_deadline * 0.8)
            await self.extend_leases()

    async def extend_leases(self) -> None:
        """Extend every lease younger than ``max_lease``; drop the older ones."""
        now = time.monotonic()
        expired = [
            i for i, since in self._leased.items() if now - since >= self.flow.max_lease
        ]
        for ack_id in expired:
            self._release(ack_id)
        ids = list(self._leased)
        for start in range(0, len(ids), MAX_IDS_PER_REQUEST):
            await self._attempt(
                self._extend(
                    ids[start : start + MAX_IDS_PER_REQUEST], self.flow.ack_deadline
                ),
                "Extending leases",
            )

    async def _attempt(self, call: Awaitable[None], what: str) -> Exception | None:
        """Run one request; a failure is logged and returned, not raised."""
        try:
            await call
        except Exception as e:
            self._log(f"{what} failed: {e!r}", logging.WARNING)
            return e
        return None

    async def close(self) -> None:
        """Send what is queued, return the held deliveries to the service, stop the tasks."""
        if self._closed:
            return
        self._closed = True
        for task in (self._flusher, self._leaser):
            if task is not None:
                task.cancel()
        self._flusher = self._leaser = None
        # A delivery still held is nacked, so the service redelivers it at once instead of
        # after its ack deadline.
        self._nacks.ids.extend(self._leased)
        for ack_id in list(self._leased):
            self._release(ack_id)
        await self.flush()
