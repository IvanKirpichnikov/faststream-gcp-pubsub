# Getting started

A service is a `PubSubBroker`, a `FastStream` app and handlers.

```python title="service.py"
--8<-- "docs/docs_src/getting_started/service.py"
```

The handler reads the subscription `orders-billing`, which is attached to the topic `orders`.
The broker is built without any network call; it connects when the app starts.

## Run the service

Install the `cli` extra, then start the app with the `faststream` command:

```shell
pip install "faststream-gcp-pubsub[cli]"
faststream run service:app
```

The service authenticates with
[Application Default Credentials](https://cloud.google.com/docs/authentication/application-default-credentials).
On a workstation, `gcloud auth application-default login` creates them. Other ways to
authenticate are on the [Emulator and credentials](emulator-and-credentials.md) page.

Pub/Sub keeps topics and subscriptions as separate resources, and a service reads from
resources that exist. The next sections create them for local work.

## Run against the emulator

The repository ships a `docker-compose.yaml` that starts the Pub/Sub emulator:

```yaml title="docker-compose.yaml"
--8<-- "docker-compose.yaml"
```

The `justfile` has the recipes you need:

| Recipe | What it does |
| --- | --- |
| `just emulator-up` | Starts the emulator on port 8085 (set `PUBSUB_EMULATOR_PORT` to change it) and waits until it is ready. |
| `just test-gcp` | Runs the tests marked `gcp` against the emulator. |
| `just emulator-down` | Stops the emulator. |

A service connects to the emulator with `emulator_host`. A subscription declared with
`declare=True` creates its topic and itself at startup, so the emulator needs no setup:

```python title="service.py"
--8<-- "docs/docs_src/getting_started/emulator.py"
```

```shell
just emulator-up
faststream run service:app
```

The handler logs the order that `place_order` publishes after startup.

!!! tip
    Setting `PUBSUB_EMULATOR_HOST=localhost:8085` in the environment has the same effect as
    `emulator_host`, so the service code stays the same in production.

## Test the service

`TestPubSubBroker` runs the handlers in process:

```python title="test_service.py"
--8<-- "tests/docs/getting_started/test_service.py:test"
```

Read [Testing](testing.md) for the routing rules of the in-process broker.
