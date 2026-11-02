from typing import TYPE_CHECKING, Union

from faststream._internal.endpoint.publisher.fake import FakePublisher

from faststream_gcp_pubsub.response import PubSubPublishCommand

if TYPE_CHECKING:
    from faststream._internal.producer import ProducerProto
    from faststream.response.response import PublishCommand


class PubSubFakePublisher(FakePublisher):
    """Publishes a handler's reply to the topic its message named in ``reply_to``."""

    __slots__ = ("topic",)

    def __init__(
        self,
        producer: "ProducerProto[PubSubPublishCommand]",
        topic: str,
    ) -> None:
        super().__init__(producer=producer)
        self.topic = topic

    def patch_command(
        self,
        cmd: Union["PublishCommand", "PubSubPublishCommand"],
    ) -> "PubSubPublishCommand":
        cmd = super().patch_command(cmd)
        real_cmd = PubSubPublishCommand.from_cmd(cmd)
        real_cmd.destination = self.topic
        return real_cmd
