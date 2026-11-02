from typing import TYPE_CHECKING, Any

from faststream_gcp_pubsub.schemas import PubSubTopic

from .config import PubSubPublisherConfig, PubSubPublisherSpecificationConfig
from .specification import PubSubPublisherSpecification
from .usecase import PubSubPublisher

if TYPE_CHECKING:
    from faststream_gcp_pubsub.broker.config import PubSubBrokerConfig


def create_publisher(
    *,
    topic: str | PubSubTopic,
    ordering_key: str,
    headers: dict[str, str] | None,
    # Publisher args
    broker_config: "PubSubBrokerConfig",
    # AsyncAPI args
    schema_: Any | None,
    title_: str | None,
    description_: str | None,
    include_in_schema: bool,
) -> PubSubPublisher:
    topic_ = topic if isinstance(topic, PubSubTopic) else PubSubTopic(topic)

    publisher_config = PubSubPublisherConfig(
        topic=topic_,
        ordering_key=ordering_key,
        headers=headers,
        _outer_config=broker_config,
    )

    specification = PubSubPublisherSpecification(
        _outer_config=broker_config,
        specification_config=PubSubPublisherSpecificationConfig(
            topic=topic_,
            ordering_key=ordering_key,
            schema_=schema_,
            title_=title_,
            description_=description_,
            include_in_schema=include_in_schema,
        ),
    )

    return PubSubPublisher(publisher_config, specification)
