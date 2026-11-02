from faststream import FastStream
from prometheus_client import CollectorRegistry, make_asgi_app

from faststream_gcp_pubsub import PubSubBroker
from faststream_gcp_pubsub.prometheus import PubSubPrometheusMiddleware

registry = CollectorRegistry()

broker = PubSubBroker(
    project_id="my-project",
    middlewares=(PubSubPrometheusMiddleware(registry=registry, app_name="billing"),),
)
app = FastStream(broker)

# serve the metrics: `app` mounted on any ASGI server, or `FastStream.as_asgi`
metrics_app = make_asgi_app(registry)


@broker.subscriber("orders-billing", topic="orders")
async def bill(order: dict[str, int]) -> None: ...
