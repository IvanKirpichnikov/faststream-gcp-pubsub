# Publishing

`publish` sends one message and returns the message id the service assigned. `publish_batch`
sends several messages in one request and returns their ids.

```python title="service.py"
--8<-- "docs/docs_src/publishing/publish.py"
```

A batch takes at most 1000 messages and 10 MB.

## Attributes

Headers travel as message attributes. Values are strings on the wire, so another value type is
sent as its `str()`. FastStream adds `correlation_id`, `content-type` and, when set,
`reply_to`.

## Ordering keys

Messages with one ordering key reach a subscription with `enable_message_ordering=True` in the
order the service received them. Publish them one after another, awaiting each call:
concurrent calls reach the service in any order.

## Message ids

`publish` returns the id of the message and `publish_batch` returns a list of ids in the order
of the messages. The consumer reads the id from `msg.raw_message.message_id`.

## Publisher objects

A publisher object keeps the topic and the defaults for every call.

```python title="service.py"
--8<-- "docs/docs_src/publishing/publisher.py"
```

A call can replace the ordering key. Attributes given to a call are added to the publisher's.

Decorate a handler with a publisher to publish its return value, as the
[home page](index.md) does with `@shipments`.

## Limits of the service

The service rejects a message with too many or too long attributes, an ordering key above 1024
bytes, or a body above 10 MB. The error is the service's `InvalidArgument`. The
[test broker](testing.md) raises the same error.
