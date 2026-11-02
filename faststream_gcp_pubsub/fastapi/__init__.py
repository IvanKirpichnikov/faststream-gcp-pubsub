"""FastAPI integration; importing it requires ``fastapi``."""

from typing import Annotated

from faststream._internal.fastapi.context import Context, ContextRepo, Logger

from faststream_gcp_pubsub.broker.broker import PubSubBroker as PSB
from faststream_gcp_pubsub.connection import PubSubConnection
from faststream_gcp_pubsub.message import PubSubMessage as PSM

from .fastapi import PubSubRouter

__all__ = (
    "Connection",
    "Context",
    "ContextRepo",
    "Logger",
    "PubSubBroker",
    "PubSubMessage",
    "PubSubRouter",
)

Connection = Annotated[PubSubConnection, Context("broker._connection")]
PubSubMessage = Annotated[PSM, Context("message")]
PubSubBroker = Annotated[PSB, Context("broker")]
