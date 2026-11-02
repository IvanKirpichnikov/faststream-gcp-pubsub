from typing import TYPE_CHECKING, Any

from faststream._internal.endpoint.subscriber import SubscriberSpecification
from faststream.specification.asyncapi.utils import resolve_payloads
from faststream.specification.schema import Message, Operation, SubscriberSpec

from faststream_gcp_pubsub.broker.config import PubSubBrokerConfig

from .config import PubSubSubscriberSpecificationConfig

if TYPE_CHECKING:
    from faststream._internal.endpoint.subscriber.call_item import CallsCollection


class PubSubSubscriberSpecification(
    SubscriberSpecification[PubSubBrokerConfig, PubSubSubscriberSpecificationConfig],
):
    __slots__ = ()

    def __init__(
        self,
        _outer_config: "PubSubBrokerConfig",
        specification_config: "PubSubSubscriberSpecificationConfig",
        calls: "CallsCollection[Any]",
    ) -> None:
        super().__init__(_outer_config, specification_config, calls)

    @property
    def subscription(self) -> str:
        return f"{self._outer_config.prefix}{self.config.subscription.name}"

    @property
    def topic(self) -> str:
        """The topic a message arrives on: the channel a consumer and a publisher share."""
        return f"{self._outer_config.prefix}{self.config.topic.name}"

    @property
    def channel_labels(self) -> list[str]:
        return [self.subscription]

    def get_schema(self) -> dict[str, SubscriberSpec]:
        payloads = self.get_payloads()
        description = self.description or (
            f"Reads subscription `{self.subscription}` of topic `{self.topic}`."
        )
        return {
            self.name: SubscriberSpec(
                address=self.topic,
                description=description,
                operation=Operation(
                    message=Message(
                        title=f"{self.name}:Message",
                        payload=resolve_payloads(payloads),
                    ),
                    bindings=None,
                ),
                bindings=None,
            ),
        }
