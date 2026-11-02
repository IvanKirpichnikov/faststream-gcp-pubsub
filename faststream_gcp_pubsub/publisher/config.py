from dataclasses import dataclass, field

from faststream._internal.configs import (
    PublisherSpecificationConfig,
    PublisherUsecaseConfig,
)

from faststream_gcp_pubsub.broker.config import PubSubBrokerConfig
from faststream_gcp_pubsub.schemas import PubSubTopic


@dataclass(kw_only=True)
class PubSubPublisherSpecificationConfig(PublisherSpecificationConfig):
    topic: PubSubTopic
    ordering_key: str = ""


@dataclass(kw_only=True)
class PubSubPublisherConfig(PublisherUsecaseConfig):
    _outer_config: "PubSubBrokerConfig" = field(default_factory=PubSubBrokerConfig)

    topic: PubSubTopic
    ordering_key: str
    headers: dict[str, str] | None
