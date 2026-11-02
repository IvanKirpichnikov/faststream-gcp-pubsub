# Vendored from FastStream (https://github.com/ag2ai/faststream), tests/marks.py, Apache-2.0.
# Adapted for faststream-gcp-pubsub; see tests/NOTICE.

import pytest
from faststream._internal._compat import (
    IS_MACOS,
    IS_WINDOWS,
    PYDANTIC_V2,
)

skip_windows = pytest.mark.skipif(
    IS_WINDOWS,
    reason="does not run on windows",
)

skip_macos = pytest.mark.skipif(
    IS_MACOS,
    reason="does not run on macOS",
)

pydantic_v1 = pytest.mark.skipif(
    PYDANTIC_V2,
    reason="requires PydanticV2",
)

pydantic_v2 = pytest.mark.skipif(
    not PYDANTIC_V2,
    reason="requires PydanticV1",
)
