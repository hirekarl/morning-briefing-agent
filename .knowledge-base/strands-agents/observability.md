# Strands Agents — Observability

## Debug logging

```python
import logging
logging.getLogger("strands").setLevel(logging.DEBUG)
logging.basicConfig(
    format="%(levelname)s | %(name)s | %(message)s",
    handlers=[logging.StreamHandler()]
)
```

## Metrics on every invocation

Every agent call returns an `AgentResult` with detailed metrics:

```python
result = agent("What is the square root of 144?")
print(result.metrics.get_summary())
```

Includes: latency, token usage, tool statistics, traces, cycle count, execution timings.

- `result.metrics.get_summary()` — in-memory metrics
- OpenTelemetry export — for external observability platforms

## Gotcha

- Metrics/traces are per-invocation on the `AgentResult`, not accumulated automatically across calls — aggregate them yourself if you need cross-request stats (e.g. for a team dashboard).
