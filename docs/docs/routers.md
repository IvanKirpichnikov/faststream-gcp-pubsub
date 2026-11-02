# Routers

A router groups subscribers and publishers in a module and is included into the broker.

```python title="service.py"
--8<-- "docs/docs_src/routers/router.py"
```

`PubSubRouter(prefix="billing-")` prepends the prefix to the topic and subscription names it
declares: the handler above reads `billing-orders` and publishes to `billing-receipts`.

## PubSubRoute and PubSubPublisher

`PubSubRoute` registers a handler without a decorator: it takes the function, the subscription
and the same options as `@broker.subscriber`. `PubSubPublisher` is a publisher registration
that a route passes in `publishers=`. Routes go to the router's `handlers=`; routers nest with
`routers=`.

## Options of the router

`PubSubRouter` also accepts `dependencies`, `middlewares`, `parser`, `decoder`, `ack_policy`
and `include_in_schema`. They apply to everything the router declares.
