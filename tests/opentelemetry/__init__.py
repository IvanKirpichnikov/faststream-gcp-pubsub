# Vendored from FastStream (https://github.com/ag2ai/faststream), tests/opentelemetry/__init__.py, Apache-2.0.
# Adapted for faststream-gcp-pubsub; see tests/NOTICE.

import pytest

pytest.importorskip("opentelemetry.sdk")
