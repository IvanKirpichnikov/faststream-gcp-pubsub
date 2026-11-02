from fastapi import FastAPI

from faststream_gcp_pubsub.fastapi import PubSubRouter

router = PubSubRouter(project_id="my-project")


@router.subscriber("orders-billing", topic="orders")
async def bill(order: dict[str, int]) -> None: ...


@router.post("/orders")
async def place_order(order: dict[str, int]) -> str:
    return await router.broker.publish(order, "orders")


app = FastAPI()
app.include_router(router)
