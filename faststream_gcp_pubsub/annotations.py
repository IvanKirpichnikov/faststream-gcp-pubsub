from typing import Annotated

from faststream._internal.context import Context
from faststream.annotations import ContextRepo, Logger
from faststream.params import NoCast

from faststream_gcp_pubsub.broker.broker import PubSubBroker as PSB
from faststream_gcp_pubsub.connection import PubSubConnection
from faststream_gcp_pubsub.message import PubSubMessage as PSM

__all__ = (
    "Connection",
    "ContextRepo",
    "Logger",
    "NoCast",
    "PubSubBroker",
    "PubSubMessage",
)

Connection = Annotated[PubSubConnection, Context("broker._connection")]
PubSubMessage = Annotated[PSM, Context("message")]
PubSubBroker = Annotated[PSB, Context("broker")]
