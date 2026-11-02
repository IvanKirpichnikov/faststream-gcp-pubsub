from faststream._internal.endpoint.publisher import PublisherSpecification
from faststream.specification.asyncapi.utils import resolve_payloads
from faststream.specification.schema import Message, Operation, PublisherSpec

from faststream_gcp_pubsub.broker.config import PubSubBrokerConfig

from .config import PubSubPublisherSpecificationConfig


class PubSubPublisherSpecification(
    PublisherSpecification[PubSubBrokerConfig, PubSubPublisherSpecificationConfig],
):
    __slots__ = ()

    @property
    def topic(self) -> str:
        return f"{self._outer_config.prefix}{self.config.topic.name}"

    @property
    def name(self) -> str:
        if self.config.title_:
            return self.config.title_
        return f"{self.topic}:Publisher"

    def get_schema(self) -> dict[str, PublisherSpec]:
        payloads = self.get_payloads()
        return {
            self.name: PublisherSpec(
                address=self.topic,
                description=self.config.description_,
                operation=Operation(
                    message=Message(
                        title=f"{self.name}:Message",
                        payload=resolve_payloads(payloads, "Publisher"),
                    ),
                    bindings=None,
                ),
                bindings=None,
            ),
        }
