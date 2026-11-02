# mypy: disable-error-code="untyped-decorator"
# `broker_class` is held as `Any` by the shared testcases, so `subscriber` is untyped here.
from typing import Any


class DescribedChannelMixin:
    """A subscriber channel is described by the subscription it reads.

    The base `test_simple_type` expects no channel description; here the default one
    (`Reads subscription ... of topic ...`) is the contract, so the payload check stays and the description
    check is restated.
    """

    broker_class: Any

    get_spec: Any

    def test_simple_type(self) -> None:
        broker = self.broker_class()

        @broker.subscriber("test")
        async def handle(msg: int) -> None: ...

        schema = self.get_spec(broker).to_jsonable()

        payload = schema["components"]["schemas"]
        assert next(iter(schema["channels"].values()))["description"] == (
            "Reads subscription `test` of topic `test`."
        )

        for key, v in payload.items():
            assert key == "Handle:Message:Payload"
            assert v == {"title": key, "type": "integer"}
