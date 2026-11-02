from faststream import FastStream

from faststream_gcp_pubsub import PubSubBroker

# also read from PUBSUB_EMULATOR_HOST when the argument is omitted
broker = PubSubBroker(project_id="faststream-test", emulator_host="localhost:8085")
app = FastStream(broker)


@broker.subscriber("orders-billing", topic="orders")
async def bill(order: dict[str, int]) -> None: ...
