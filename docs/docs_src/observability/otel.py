from faststream import FastStream
from opentelemetry.sdk.trace import TracerProvider

from faststream_gcp_pubsub import PubSubBroker
from faststream_gcp_pubsub.opentelemetry import PubSubTelemetryMiddleware

tracer_provider = TracerProvider()

broker = PubSubBroker(
    project_id="my-project",
    middlewares=(PubSubTelemetryMiddleware(tracer_provider=tracer_provider),),
)
app = FastStream(broker)


@broker.subscriber("orders-billing", topic="orders")
async def bill(order: dict[str, int]) -> None: ...
