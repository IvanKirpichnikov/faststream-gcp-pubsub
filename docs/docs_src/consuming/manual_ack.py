from faststream import AckPolicy, FastStream

from faststream_gcp_pubsub import PubSubBroker, PubSubMessage

broker = PubSubBroker(project_id="my-project")
app = FastStream(broker)


@broker.subscriber("orders-billing", topic="orders", ack_policy=AckPolicy.MANUAL)
async def bill(order: dict[str, int], msg: PubSubMessage) -> None:
    if order["amount"] < 0:
        # Pub/Sub has no reject: the message is acknowledged and dropped
        await msg.reject()
    elif order["amount"] == 0:
        # available for redelivery at once
        await msg.nack()
    else:
        await msg.ack()
