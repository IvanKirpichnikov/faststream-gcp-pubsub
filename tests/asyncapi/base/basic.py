# Vendored from FastStream (https://github.com/ag2ai/faststream), tests/asyncapi/base/basic.py, Apache-2.0.
# Adapted for faststream-gcp-pubsub; see tests/NOTICE.

from typing import Any

from faststream.specification.base import Specification


class SpecificationFactory:
    def get_spec(self, *brokers: Any) -> Specification:
        raise NotImplementedError
