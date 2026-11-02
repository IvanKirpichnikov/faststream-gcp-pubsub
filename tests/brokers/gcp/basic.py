from contextlib import AbstractAsyncContextManager
from typing import Any, overload

from typing_extensions import override

from faststream_gcp_pubsub import PubSubBroker, PubSubRouter, PubSubSubscription
from tests.brokers.base.basic import BaseTestcaseConfig

from .conftest import Settings

SETTINGS = Settings()


class PubSubTestcaseConfig(BaseTestcaseConfig[PubSubBroker]):
    """Live: the broker talks to the emulator and declares what a test subscribes to."""

    def get_broker(self, apply_types: bool = False, **kwargs: Any) -> PubSubBroker:
        kwargs.setdefault("project_id", SETTINGS.project_id)
        kwargs.setdefault("emulator_host", SETTINGS.emulator_host)
        return PubSubBroker(apply_types=apply_types, **kwargs)

    def get_subscriber_params(
        self, subscription: str, *args: Any, **kwargs: Any
    ) -> tuple[tuple[Any, ...], dict[str, Any]]:
        return (PubSubSubscription(subscription, declare=True), *args), kwargs

    def get_router(self, **kwargs: Any) -> PubSubRouter:
        return PubSubRouter(**kwargs)


class PubSubMemoryTestcaseConfig(PubSubTestcaseConfig):
    """In-process: the same tests through ``TestPubSubBroker``."""

    @overload
    def patch_broker(
        self, brokers: PubSubBroker, **kwargs: Any
    ) -> AbstractAsyncContextManager[PubSubBroker]: ...

    @overload
    def patch_broker(
        self, *brokers: PubSubBroker, **kwargs: Any
    ) -> AbstractAsyncContextManager[tuple[PubSubBroker, ...]]: ...

    @override
    def patch_broker(self, *brokers: PubSubBroker, **kwargs: Any) -> Any:
        from faststream_gcp_pubsub.testing import TestPubSubBroker  # noqa: PLC0415

        return TestPubSubBroker(*brokers, **kwargs)
