# Testing

`TestPubSubBroker` runs the broker in process, with no Pub/Sub service behind it.

```python title="test_service.py"
--8<-- "tests/docs/testing/test_service.py:bill"
```

The service under test:

```python title="service.py"
--8<-- "docs/docs_src/testing/service.py"
```

A publish reaches the handlers directly. `handler.mock` records the decoded body of each call,
and the handler's reply reaches the subscribers of its topic.

## Routing

The test broker routes the way the service does:

- A topic delivers to every subscription attached to it.
- The consumers of one subscription share its messages, in turn.
- A subscription read by `get_one()` or iteration keeps what is published until it is read.
- Ack, nack and reject settle the message once: each message reaches its handler one time.

A declaration always succeeds, and a publish reaches whichever subscriptions the service declares
for its topic.

## Validation

A publish the service would reject raises the service's `InvalidArgument`: attribute names and
sizes, the ordering key size, message and request size, and the resource id format.

```python title="test_service.py"
--8<-- "tests/docs/testing/test_service.py:invalid"
```

## Against the emulator

`with_real=True` runs the same test against a real service, such as the
[emulator](emulator-and-credentials.md#the-emulator). Declare the resources the service uses with
`declare=True`, as the example service does.

```python title="test_service.py"
--8<-- "tests/docs/testing/test_service.py:real"
```

Mark such tests `gcp` and run them with `just test-gcp` while the emulator is up.
