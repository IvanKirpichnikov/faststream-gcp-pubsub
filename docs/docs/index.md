# faststream-gcp-pubsub

A [Google Cloud Pub/Sub](https://cloud.google.com/pubsub) broker for
[FastStream](https://faststream.ag2.ai/), maintained by the community.

```python title="service.py"
--8<-- "docs/docs_src/home/service.py"
```

```shell
faststream run service:app
```

The handler reads the `orders-billing` subscription of the `orders` topic, decodes the JSON body
into `Order`, acknowledges the message once the handler returns, and publishes its result to
`shipments`.

## Install

=== "pip"

    ```shell
    pip install faststream-gcp-pubsub
    ```

=== "uv"

    ```shell
    uv add faststream-gcp-pubsub
    ```

The package needs Python 3.10 or newer and FastStream 0.7. The extras are `otel`
(OpenTelemetry), `prometheus` and `cli` (the `faststream` command):

```shell
pip install "faststream-gcp-pubsub[cli,otel,prometheus]"
```

## What you get

- Subscribers read a subscription through a streaming pull and keep each message leased until
  the handler settles it.
- Publishers send one message or a batch, with attributes, ordering keys and message ids.
- Topics, subscriptions, dead-letter and retry policies are created at startup when you declare
  them.
- Acknowledgement follows the Pub/Sub model: ack, nack for immediate redelivery, and reject as
  an acknowledgement.
- Flow control bounds the messages and bytes held at once; acks travel in batches.
- `TestPubSubBroker` runs the service in process, with routing and validation like the real
  service.
- The Pub/Sub emulator, Application Default Credentials, service account keys and regional
  endpoints are supported.
- FastAPI, OpenTelemetry, Prometheus and AsyncAPI integrations are included.

## Where to go next

- [Getting started](getting-started.md) builds a service and runs it against the emulator.
- [Topics and subscriptions](topics-and-subscriptions.md) explains how Pub/Sub resources map to
  handlers.
- [Testing](testing.md) shows how to test a service without Google Cloud.
- The [API reference](api.md) lists every public class.
