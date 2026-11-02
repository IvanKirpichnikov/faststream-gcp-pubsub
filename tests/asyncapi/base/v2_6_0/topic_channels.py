# Vendored from FastStream (https://github.com/ag2ai/faststream), tests/asyncapi/base/v2_6_0/topic_channels.py, Apache-2.0.
# Adapted for faststream-gcp-pubsub; see tests/NOTICE.

from tests.asyncapi.base.topic_channels import (
    TopicChannelsTestcase as BaseTopicChannelsTestcase,
)

from .basic import AsyncAPI260Factory


class TopicChannelsTestcase(BaseTopicChannelsTestcase, AsyncAPI260Factory):
    pass
