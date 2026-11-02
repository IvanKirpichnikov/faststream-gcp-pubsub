from faststream import FastStream

from faststream_gcp_pubsub import PubSubBroker

broker = PubSubBroker(
    project_id="my-project",
    description="Orders of the shop",
)
app = FastStream(broker)

shipments = broker.publisher("shipments", description="Orders ready to ship")


@broker.subscriber("orders-billing", topic="orders", description="Bills an order")
@shipments
async def bill(order: dict[str, int]) -> dict[str, int]:
    return {"order_id": order["id"]}
