# Observability

## OpenTelemetry

`PubSubTelemetryMiddleware` traces and measures publishes and deliveries. Install the `otel`
extra.

```python title="service.py"
--8<-- "docs/docs_src/observability/otel.py"
```

The middleware takes `tracer_provider`, `meter_provider`, `meter` and
`include_messages_counters`, as FastStream's `TelemetryMiddleware` does.

## Prometheus

`PubSubPrometheusMiddleware` exports the metrics of publishes and deliveries to a Prometheus
registry. Install the `prometheus` extra.

```python title="service.py"
--8<-- "docs/docs_src/observability/prometheus.py"
```

The middleware takes `registry`, `app_name`, `metrics_prefix`,
`received_messages_size_buckets` and `custom_labels`, as FastStream's `PrometheusMiddleware`
does.
