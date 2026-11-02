from faststream import FastStream

from faststream_gcp_pubsub import PubSubBroker

broker = PubSubBroker(project_id="my-project")
app = FastStream(broker)


# ten deliveries are handled at once
@broker.subscriber("orders-billing", topic="orders", max_workers=10)
async def bill(order: dict[str, int]) -> None: ...
