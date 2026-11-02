from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Optional

from faststream._internal.configs import BrokerConfig
from faststream._internal.parser import DefaultCodec
from faststream.exceptions import IncorrectState

from faststream_gcp_pubsub.publisher.producer import FakePubSubProducer

if TYPE_CHECKING:
    from faststream_gcp_pubsub.connection import PubSubConnection
    from faststream_gcp_pubsub.publisher.producer import PubSubProducer


@dataclass(kw_only=True)
class PubSubBrokerConfig(BrokerConfig):
    project_id: str = ""

    producer: "PubSubProducer" = field(default_factory=FakePubSubProducer)
    _connection: Optional["PubSubConnection"] = field(
        default=None, init=False, repr=False
    )

    @property
    def connection(self) -> "PubSubConnection":
        if self._connection is None:
            msg = "Pub/Sub broker is not connected. Call connect() first."
            raise IncorrectState(msg)
        return self._connection

    def connect(self, connection: "PubSubConnection") -> None:
        self._connection = connection
        self.producer.connect(
            connection,
            project_id=self.project_id,
            serializer=self.fd_config._serializer,
            codec=self.broker_codec or DefaultCodec(),
        )

    def disconnect(self) -> None:
        self._connection = None
        self.producer.disconnect()
