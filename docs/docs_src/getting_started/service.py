from faststream import FastStream, Logger

from faststream_gcp_pubsub import PubSubBroker

broker = PubSubBroker(project_id="my-project")
app = FastStream(broker)


@broker.subscriber("orders-billing", topic="orders")
async def handle(order: dict[str, int], logger: Logger) -> None:
    logger.info("order %s", order["id"])
