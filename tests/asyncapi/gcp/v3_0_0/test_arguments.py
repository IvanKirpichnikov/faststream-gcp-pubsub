from faststream_gcp_pubsub import PubSubBroker
from tests.asyncapi.base.v3_0_0.arguments import ArgumentsTestcase
from tests.asyncapi.gcp.described_channel import DescribedChannelMixin


class TestArguments(DescribedChannelMixin, ArgumentsTestcase):
    broker_class = PubSubBroker
