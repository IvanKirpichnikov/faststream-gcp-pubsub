from faststream import FastStream

from faststream_gcp_pubsub import PubSubBroker

broker = PubSubBroker(project_id="my-project")
app = FastStream(broker)


@broker.subscriber("orders-billing", topic="orders")
async def bill(order: dict[str, int]) -> None: ...


async def place_orders() -> None:
    message_id = await broker.publish(
        {"id": 1},
        "orders",
        headers={"region": "eu"},
        ordering_key="customer-42",
        correlation_id="req-1",
    )
    ids = await broker.publish_batch({"id": 2}, {"id": 3}, topic="orders")
    assert isinstance(message_id, str)
    assert len(ids) == 2
