from faststream import AsyncAPI

from docs.docs_src.asyncapi.service import broker


def test_schema_names_subscription_and_topic() -> None:
    schema = AsyncAPI(broker).to_specification().to_jsonable()

    channels = " ".join(schema["channels"])
    assert "orders-billing" in channels
    assert "shipments" in channels
