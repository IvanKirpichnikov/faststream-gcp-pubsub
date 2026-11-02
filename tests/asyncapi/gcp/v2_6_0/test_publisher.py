from faststream_gcp_pubsub import PubSubBroker
from tests.asyncapi.base.v2_6_0.publisher import PublisherTestcase


class TestPublisher(PublisherTestcase):
    broker_class = PubSubBroker
