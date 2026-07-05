# Integration Patterns: Strands Agent + LiteLLM + OpenRouter

This is the doc that ties the other three sections together. It assumes you've read at least the quickstarts in [`strands-agents/`](strands-agents/_map.md), [`litellm-proxy/`](litellm-proxy/_map.md), and [`openrouter/`](openrouter/_map.md).

## Why LiteLLM sits between Strands and OpenRouter

Strands Agents ships a `LiteLLMModel` provider (see [`strands-agents/model-providers/litellm.md`](strands-agents/model-providers/litellm.md)). LiteLLM itself is a unified client library **and** a proxy server — you can use its Python client without running the proxy at all, or run the proxy as a separate service. Both paths let a Strands `Agent` reach OpenRouter (or any other provider) through one consistent interface.

## Pattern 1 — Direct to OpenRouter (no proxy container)

Simplest setup: `LiteLLMModel`'s `client_args` point straight at OpenRouter's OpenAI-compatible endpoint. No Docker container needed.

```python
from strands import Agent
from strands.models.litellm import LiteLLMModel

model = LiteLLMModel(
    client_args={
        "api_key": "<OPENROUTER_API_KEY>",
        "api_base": "https://openrouter.ai/api/v1",
    },
    model_id="openai/gpt-4o",          # <provider>/<model> as OpenRouter expects
    params={"max_tokens": 1000, "temperature": 0.7},
)

agent = Agent(model=model)
agent("What is the meaning of life?")
```

**Gotcha:** the `model_id` must match the slug OpenRouter expects (e.g. `openai/gpt-4o`, `anthropic/claude-3-7-sonnet-20250219`), not a raw LiteLLM provider prefix — OpenRouter is doing the provider resolution here, not LiteLLM.

## Pattern 2 — Through a self-hosted LiteLLM proxy

Run the proxy (see [`litellm-proxy/docker-quickstart.md`](litellm-proxy/docker-quickstart.md)) with a `config.yaml` model entry that routes to OpenRouter:

```yaml
# config.yaml
model_list:
  - model_name: gpt-4o
    litellm_params:
      model: openrouter/openai/gpt-4o
      api_key: os.environ/OPENROUTER_API_KEY

general_settings:
  master_key: sk-1234
```

Start it:

```bash
docker run \
  -v $(pwd)/config.yaml:/app/config.yaml \
  -e OPENROUTER_API_KEY=your_key \
  -p 4000:4000 \
  docker.litellm.ai/berriai/litellm:latest \
  --config /app/config.yaml --detailed_debug
```

Then point the Strands agent at the proxy instead of OpenRouter directly — two equivalent ways (see [`strands-agents/model-providers/litellm.md`](strands-agents/model-providers/litellm.md) for both):

```python
from strands import Agent
from strands.models.litellm import LiteLLMModel

model = LiteLLMModel(
    client_args={
        "api_key": "sk-1234",              # the proxy's master_key or a generated virtual key
        "api_base": "http://localhost:4000",
        "use_litellm_proxy": True,
    },
    model_id="gpt-4o",                     # the model_name alias defined in config.yaml
)

agent = Agent(model=model)
agent("What is the meaning of life?")
```

## Why choose the proxy over calling OpenRouter directly

Use the proxy when the team needs things OpenRouter alone doesn't give you as a shared service:
- **Virtual keys per teammate** with independent `rpm_limit`/`tpm_limit` (see [`litellm-proxy/virtual-keys-and-rate-limits.md`](litellm-proxy/virtual-keys-and-rate-limits.md)) — useful when multiple people on the team are hitting the same upstream OpenRouter key.
- **One config.yaml swap** to change providers/models for the whole team without touching agent code.
- **Fallbacks and load balancing** across multiple model deployments (`router_settings`, `litellm_settings.fallbacks` — see [`litellm-proxy/config-yaml-reference.md`](litellm-proxy/config-yaml-reference.md)).

Skip the proxy (use Pattern 1) for a single-developer prototype where none of the above matters yet — it's one less moving part.

## End-to-end gotchas specific to this combination

- **Two different "provider" concepts stack up**: OpenRouter's own model routing (which upstream provider serves `openai/gpt-4o`) is separate from LiteLLM's `router_settings` routing (which LiteLLM deployment serves a request). Don't confuse the two when debugging a routing issue — check OpenRouter's dashboard for the former, proxy logs for the latter.
- **`os.environ/VAR` syntax is LiteLLM-only.** It works inside `config.yaml` (proxy) but not in `client_args` passed directly from Python — those need real values or your own `os.getenv(...)` call.
- **Model ID mismatches are the most common failure.** The `model_id` string in `LiteLLMModel` must match exactly one of: an OpenRouter slug (Pattern 1) or a `model_name` alias defined in the proxy's `config.yaml` (Pattern 2). Mixing these up produces a 404/"model not found" from the wrong layer.
- **Master key vs. virtual key:** don't hand out the proxy's `master_key` to the whole team — generate scoped virtual keys per teammate/service (see [`litellm-proxy/virtual-keys-and-rate-limits.md`](litellm-proxy/virtual-keys-and-rate-limits.md)) so rate limits and rotation are per-key.
