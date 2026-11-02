# Emulator and credentials

## The emulator

The broker connects to the [Pub/Sub emulator](https://cloud.google.com/pubsub/docs/emulator),
with no credentials, when the `PUBSUB_EMULATOR_HOST` variable is set or `emulator_host` is
passed.

```python title="service.py"
--8<-- "docs/docs_src/emulator/emulator.py"
```

`emulator_host=None` connects to Google Cloud even when the variable is set. The
[getting started](getting-started.md#run-against-the-emulator) page shows how to start the
emulator with the repository's `docker-compose.yaml`.

## Project

`project_id` names the project short topic and subscription names belong to. When it is
omitted, the broker reads `GOOGLE_CLOUD_PROJECT`.

## Credentials

Without a security object the broker uses Application Default Credentials: the
`GOOGLE_APPLICATION_CREDENTIALS` key file, the gcloud login, or the metadata server of Google
Cloud. `GCPSecurity` passes other credentials.

```python title="service.py"
--8<-- "docs/docs_src/emulator/credentials.py"
```

`GCPSecurity` also has `from_service_account_info`, which takes the parsed JSON key. Any
`google.auth` credentials object works with `GCPSecurity(credentials)`.

## Endpoints and client options

`api_endpoint` selects a regional or private endpoint. `client_options` passes other
`google.api_core.client_options` to both clients.

```python title="service.py"
--8<-- "docs/docs_src/emulator/endpoint.py"
```
