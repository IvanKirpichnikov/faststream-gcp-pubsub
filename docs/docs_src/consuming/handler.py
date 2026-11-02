from faststream import FastStream, Header, Logger

from faststream_gcp_pubsub import PubSubBroker, PubSubMessage

broker = PubSubBroker(project_id="my-project")
app = FastStream(broker)


@broker.subscriber("orders-billing", topic="orders")
async def bill(
    order: dict[str, int],
    msg: PubSubMessage,
    logger: Logger,
    region: str = Header(default="eu"),
) -> None:
    logger.info(
        "order %s from %s: message %s, key %r, published %s",
        order["id"],
        region,
        msg.raw_message.message_id,
        msg.ordering_key,
        msg.raw_message.publish_time,
    )
