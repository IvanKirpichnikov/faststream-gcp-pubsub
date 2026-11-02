from faststream import FastStream

from faststream_gcp_pubsub import PubSubBroker

broker = PubSubBroker(project_id="my-project")
app = FastStream(broker)


@broker.subscriber("orders-billing", topic="orders")
async def bill(order: dict[str, int]) -> None: ...


@broker.subscriber("orders-audit", topic="orders")
async def audit(order: dict[str, int]) -> None: ...


# a subscription named without a topic is attached to the topic of the same name
@broker.subscriber("invoices")
async def archive(invoice: dict[str, int]) -> None: ...


# a full name is used as it is: this reads a subscription of another project
@broker.subscriber("projects/other-project/subscriptions/orders-export", topic="orders")
async def export(order: dict[str, int]) -> None: ...
