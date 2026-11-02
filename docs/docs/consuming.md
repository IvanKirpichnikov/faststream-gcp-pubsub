# Consuming

A handler is a function decorated with `@broker.subscriber`. It receives the decoded body and
any FastStream dependencies.

```python title="service.py"
--8<-- "docs/docs_src/consuming/handler.py"
```

`msg` is the `PubSubMessage` of the delivery. Its `ordering_key` and `delivery_attempt`
properties and the `raw_message` (`message_id`, `publish_time`, `attributes`, `data`) describe
what the service sent. Attributes are also available as headers.

## Acknowledgement

The default policy is `AckPolicy.NACK_ON_ERROR`: the message is acknowledged when the handler
returns and nacked when it raises. Pub/Sub maps the settlements this way:

| Settlement | What Pub/Sub does |
| --- | --- |
| ack | The message is acknowledged and not delivered again. |
| nack | The ack deadline is set to zero and the message is available for redelivery at once. |
| reject | The message is acknowledged. Pub/Sub has no reject. |

A failed message is redelivered under the subscription's
[retry policy](declaring-resources.md#retrypolicy) and moves to its
[dead-letter topic](declaring-resources.md#deadletterpolicy) after the last attempt. That is
how a poison message leaves a subscription.

The policy is set per subscriber with `ack_policy=` or for the broker with
`PubSubBroker(ack_policy=...)`.

## Manual settlement

With `AckPolicy.MANUAL` the handler settles the message.

```python title="service.py"
--8<-- "docs/docs_src/consuming/manual_ack.py"
```

## Delivery attempts

`msg.delivery_attempt` counts the deliveries of a message. The service fills it when the
subscription has a dead-letter policy and the value is 0 otherwise.

```python title="service.py"
--8<-- "docs/docs_src/consuming/delivery_attempt.py"
```

## Reading messages without a handler

A subscriber without a handler is read by hand. `get_one` pulls one message and returns
`None` when none arrives within the timeout.

```python title="service.py"
--8<-- "docs/docs_src/consuming/get_one.py"
```

Iterating the subscriber reads a stream of messages:

```python title="service.py"
--8<-- "docs/docs_src/consuming/iterate.py"
```

The messages are settled by hand, as no handler stands behind them.

## Concurrency

By default a subscriber handles one message at a time. `max_workers` handles that many at once.

```python title="service.py"
--8<-- "docs/docs_src/consuming/workers.py"
```

`max_workers` works together with [flow control](leases-and-flow-control.md): the subscriber
reads at most `max_messages` messages that are not settled.
