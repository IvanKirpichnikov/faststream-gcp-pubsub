from faststream import FastStream

from faststream_gcp_pubsub import (
    PubSubBroker,
    PubSubPublisher,
    PubSubRoute,
    PubSubRouter,
)

broker = PubSubBroker(project_id="my-project")
app = FastStream(broker)

router = PubSubRouter(prefix="billing-")


@router.subscriber("orders", topic="orders")
@router.publisher("receipts")
async def bill(order: dict[str, int]) -> dict[str, int]:
    return {"order_id": order["id"]}


async def notify(receipt: dict[str, int]) -> None: ...


# routes declare handlers without a decorator
routes = PubSubRouter(
    prefix="shop-",
    handlers=(
        PubSubRoute(
            notify,
            "receipts",
            topic="receipts",
            publishers=(PubSubPublisher("notifications"),),
        ),
    ),
)

broker.include_router(router)
broker.include_router(routes)
