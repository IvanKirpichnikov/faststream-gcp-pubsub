from dataclasses import dataclass, field

from faststream._internal.configs import (
    SubscriberSpecificationConfig,
    SubscriberUsecaseConfig,
)
from faststream._internal.constants import EMPTY
from faststream.middlewares.acknowledgement.config import AckPolicy

from faststream_gcp_pubsub.broker.config import PubSubBrokerConfig
from faststream_gcp_pubsub.schemas import PubSubSubscription, PubSubTopic

from .settler import FlowControl


@dataclass(kw_only=True)
class PubSubSubscriberSpecificationConfig(SubscriberSpecificationConfig):
    subscription: PubSubSubscription
    topic: PubSubTopic


@dataclass(kw_only=True)
class PubSubSubscriberConfig(SubscriberUsecaseConfig):
    _outer_config: "PubSubBrokerConfig" = field(default_factory=PubSubBrokerConfig)

    subscription: PubSubSubscription
    topic: PubSubTopic
    flow_control: FlowControl

    @property
    def ack_policy(self) -> AckPolicy:
        if self._ack_policy is EMPTY:
            if self._outer_config.ack_policy is not EMPTY:
                return self._outer_config.ack_policy
            return AckPolicy.REJECT_ON_ERROR
        return self._ack_policy
