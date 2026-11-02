from typing import Any

from faststream import FastStream

from faststream_gcp_pubsub import PubSubBroker

broker = PubSubBroker(project_id="my-project")
app = FastStream(broker)

orders = broker.subscriber("orders-billing", topic="orders")


async def read_all() -> list[Any]:
    received: list[Any] = []
    async for message in orders:
        received.append(await message.decode())
        await message.ack()
        if len(received) == 3:
            break
    return received
