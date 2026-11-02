# Vendored from FastStream (https://github.com/ag2ai/faststream), tests/asyncapi/base/topic_channels.py, Apache-2.0.
# Adapted for faststream-gcp-pubsub; see tests/NOTICE.

from typing import Any

from .basic import SpecificationFactory


class TopicChannelsTestcase(SpecificationFactory):
    """One subscriber over several topics is one channel per topic, in order.

    Mixed into brokers whose subscriber takes
    more than one address at a declaration site.
    """

    broker_class: Any

    def test_channels_follow_declaration_order(self) -> None:
        broker = self.broker_class()

        @broker.subscriber("gamma", "alpha", "beta")
        async def handle() -> None: ...

        # a document that shuffles its own channels cannot be diffed in CI
        assert list(self.get_spec(broker).to_jsonable()["channels"]) == [
            "gamma:Handle",
            "alpha:Handle",
            "beta:Handle",
        ]

    def test_a_title_prefixes_several_channels(self) -> None:
        broker = self.broker_class()

        @broker.subscriber("first", "second", title="Titled")
        async def handle() -> None: ...

        # keys are unique, so a title written once per topic kept only the last
        assert list(self.get_spec(broker).to_jsonable()["channels"]) == [
            "Titled:first",
            "Titled:second",
        ]
