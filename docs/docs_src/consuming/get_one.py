from typing import Any

from faststream import FastStream

from faststream_gcp_pubsub import PubSubBroker

broker = PubSubBroker(project_id="my-project")
app = FastStream(broker)

# a subscriber without a handler is read by hand
orders = broker.subscriber("orders-billing", topic="orders")


async def read_one() -> Any | None:
    message = await orders.get_one(timeout=5.0)
    if message is None:
        return None
    order = await message.decode()
    await message.ack()
    return order
