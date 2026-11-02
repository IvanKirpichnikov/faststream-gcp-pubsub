from faststream_gcp_pubsub import PubSubBroker, PubSubPublisher, PubSubRoute, PubSubRouter
from tests.brokers.base.option_surface import (
    assert_every_level_takes_the_options_the_broker_takes,
)


def test_every_level_takes_the_options_the_broker_takes() -> None:
    assert_every_level_takes_the_options_the_broker_takes(
        PubSubBroker,
        PubSubRouter,
        PubSubRoute,
        PubSubPublisher,
    )
