# Replies

A message published with `reply_to="<topic>"` gets the handler's return value published to that
topic.

```python title="service.py"
--8<-- "docs/docs_src/replies/reply_to.py"
```

The reply is an ordinary message: the caller reads it from a subscription of the reply topic,
as `collect` does.

## PubSubResponse

Return `PubSubResponse` to set the ordering key and the attributes (`headers`) of the reply. The
same options apply to every publisher the handler is decorated with.

```python title="service.py"
--8<-- "docs/docs_src/replies/response.py"
```

## No request/reply

`broker.request()` raises `FeatureNotSupportedException`. Pub/Sub has no reply channel of its
own: an answer to a request needs a reply subscription for each caller, and creating those is
resource administration (a subscription and its permissions per caller). Publish with
`reply_to` naming a topic your service subscribes to, and read the answer there.
