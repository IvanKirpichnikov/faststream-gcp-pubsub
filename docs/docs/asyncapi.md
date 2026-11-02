# AsyncAPI

FastStream generates an [AsyncAPI](https://www.asyncapi.com/) document of the service.
Subscribers appear with their subscription and topic, publishers with their topic.

```python title="service.py"
--8<-- "docs/docs_src/asyncapi/service.py"
```

Serve the document in the browser:

```shell
faststream docs serve service:app
```

Write it to a file:

```shell
faststream docs gen service:app
```

`title`, `description` and `include_in_schema` of subscribers and publishers set the text of the
operations. The broker's `description`, `tags`, `specification_url` and `protocol` set the server
entry. The server entry carries the coordinate the broker connects to and never credentials.
