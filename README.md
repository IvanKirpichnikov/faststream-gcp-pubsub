# faststream-gcp-pubsub

A [Google Cloud Pub/Sub](https://cloud.google.com/pubsub) broker for
[FastStream](https://github.com/ag2ai/faststream), maintained by the community.

```python
from pydantic import BaseModel

from faststream import FastStream
from faststream_gcp_pubsub import PubSubBroker, PubSubSubscription


class Order(BaseModel):
    id: int
    amount: float


broker = PubSubBroker(project_id="my-project")
app = FastStream(broker)

shipments = broker.publisher("shipments")


@broker.subscriber(PubSubSubscription("orders-billing"), topic="orders")
@shipments
async def bill(order: Order) -> dict[str, int]:
    # the return value is published to the `shipments` topic
    return {"order_id": order.id}


@app.after_startup
async def place_order() -> None:
    await broker.publish(Order(id=1, amount=9.5), "orders")
```

```shell
faststream run service:app
```

The handler reads the `orders-billing` subscription of the `orders` topic, decodes the JSON body
into `Order`, acknowledges the message once the handler returns, and publishes its result to
`shipments`.

## Install

```shell
pip install faststream-gcp-pubsub
```

The package needs Python 3.10 or newer and FastStream 0.7. Extras: `otel` (OpenTelemetry),
`prometheus`, `cli` (the `faststream` command).

## Features

### Topics and subscriptions

Pub/Sub keeps topics and subscriptions as separate resources: a publisher names a topic, a
subscriber names a subscription attached to a topic. Short ids are expanded with the broker's
project; a full name (`projects/other/subscriptions/x`) is used as it is.

```python
@broker.subscriber("orders-billing", topic="orders")
async def handler(body: dict) -> None: ...
```

A subscription named without a topic is taken as attached to the topic of the same name.

### Declaring resources

The broker creates nothing by default. A declaration with `declare=True` creates the topic and
the subscription at startup when they do not exist, with the settings you give:

```python
from datetime import timedelta

from faststream_gcp_pubsub import DeadLetterPolicy, PubSubSubscription, RetryPolicy

subscription = PubSubSubscription(
    "orders-billing",
    declare=True,
    ack_deadline_seconds=30,
    enable_message_ordering=True,
    filter='attributes.region = "eu"',
    dead_letter_policy=DeadLetterPolicy("orders-dead", max_delivery_attempts=5),
    retry_policy=RetryPolicy(minimum_backoff=timedelta(seconds=10)),
)
```

The dead-letter topic is created too. An existing subscription keeps its own settings.
`broker.declare_topic(...)` and `broker.declare_subscription(...)` create resources by hand.

### Publishing

```python
message_id = await broker.publish(
    {"id": 1},
    "orders",
    headers={"region": "eu"},
    ordering_key="customer-42",
)
ids = await broker.publish_batch({"id": 1}, {"id": 2}, topic="orders")
```

Headers travel as message attributes. FastStream adds `correlation_id`, `content-type` and,
when set, `reply_to`. `publish` returns the message id the service assigned; `publish_batch`
sends all messages in one request (at most 1000 messages and 10 MB).

A publisher object keeps defaults for every call:

```python
publisher = broker.publisher("orders", ordering_key="customer-42", headers={"source": "api"})
await publisher.publish({"id": 1})
```

### Ordering keys

Messages with one ordering key reach a subscription with `enable_message_ordering=True` in the
order the service received them. Publish them one after another (await each call): concurrent
calls reach the service in any order.

### Acknowledgement

The subscriber acknowledges a message when its handler returns and nacks it when the handler
raises (`AckPolicy.NACK_ON_ERROR`). A failed message is redelivered under the subscription's
retry policy and moves to its dead-letter topic after the last attempt. With
`ack_policy=AckPolicy.MANUAL`, `msg.ack()`, `msg.nack()` and `msg.reject()` settle by hand;
`reject` acknowledges, as Pub/Sub has no reject.

Acks and nacks of one subscription are sent together, one request per 50 ms or per 1000 ids.
On a subscription with exactly-once delivery, `ack()` waits for the service's confirmation and
raises on a failure. `msg.delivery_attempt` counts deliveries on a subscription with a
dead-letter policy.

### Leases and flow control

The subscriber reads through a streaming pull and keeps each message leased: it extends the ack
deadline of every message in work until the handler settles it, up to `max_lease`. Flow control
bounds what is held at once:

```python
from faststream_gcp_pubsub import FlowControl


@broker.subscriber(
    "orders-billing",
    flow_control=FlowControl(max_messages=100, ack_deadline=60, max_lease=3600),
    max_workers=10,
)
async def handler(body: dict) -> None: ...
```

`max_workers` handles that many messages at once. On shutdown the subscriber stops reading,
waits for handlers in work up to the broker's `graceful_timeout`, sends the pending acks and
returns the messages it still holds to the service.

### Replies

A message published with `reply_to="<topic>"` gets the handler's return value published to that
topic. `PubSubResponse` sets the reply's ordering key and headers (attributes):

```python
from faststream_gcp_pubsub import PubSubResponse


@broker.subscriber("jobs")
async def run(job: dict) -> PubSubResponse:
    return PubSubResponse({"done": True}, ordering_key=job["owner"])
```

`broker.request()` raises `FeatureNotSupportedException`: Pub/Sub has no reply channel of its
own, so a reply is a message on a topic the caller subscribes to.

### Testing

`TestPubSubBroker` runs the broker in process, with no service behind it:

```python
import pytest

from faststream_gcp_pubsub.testing import TestPubSubBroker


@pytest.mark.asyncio
async def test_bill() -> None:
    async with TestPubSubBroker(broker) as br:
        await br.publish({"id": 1, "amount": 9.5}, "orders")
        bill.mock.assert_called_once_with({"id": 1, "amount": 9.5})
```

It routes like the service: a topic delivers to every subscription attached to it, consumers of
one subscription share its messages, and a subscription read by `get_one()` keeps messages until
they are read. A publish the service would reject (attribute names and sizes, ordering key size,
message and request size, resource id format) raises the service's `InvalidArgument`.

### Emulator

The broker connects to the [Pub/Sub emulator](https://cloud.google.com/pubsub/docs/emulator)
when `PUBSUB_EMULATOR_HOST` is set or `emulator_host="localhost:8085"` is passed, with no
credentials.

### Credentials

The broker authenticates with Application Default Credentials. `GCPSecurity` passes other
credentials:

```python
from faststream_gcp_pubsub import GCPSecurity, PubSubBroker

broker = PubSubBroker(
    project_id="my-project",
    security=GCPSecurity.from_service_account_file("key.json"),
)
```

`api_endpoint="europe-west1-pubsub.googleapis.com:443"` selects a regional endpoint.

### FastAPI

```python
from fastapi import FastAPI

from faststream_gcp_pubsub.fastapi import PubSubRouter

router = PubSubRouter(project_id="my-project")


@router.subscriber("orders-billing", topic="orders")
async def bill(order: dict) -> None: ...


app = FastAPI()
app.include_router(router)
```

### Observability and AsyncAPI

`faststream_gcp_pubsub.opentelemetry.PubSubTelemetryMiddleware` and
`faststream_gcp_pubsub.prometheus.PubSubPrometheusMiddleware` follow FastStream's middlewares.
`faststream docs serve service:app` serves the AsyncAPI document: subscribers appear with their
subscription and topic, publishers with their topic.

## Development

See [CONTRIBUTING.md](CONTRIBUTING.md). The source lives at
<https://github.com/powersemmi/faststream-gcp-pubsub>.

## License

Apache License 2.0. The shared broker testcases under `tests/` are adapted from FastStream, under
the same license (see `tests/NOTICE`).
