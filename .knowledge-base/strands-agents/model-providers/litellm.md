# Strands Agents — Model Provider: LiteLLM

This is the provider this project uses to reach OpenRouter (directly, or via a self-hosted LiteLLM proxy) — see [`../../integration-patterns.md`](../../integration-patterns.md) for the full picture.

## Installation

```bash
pip install 'strands-agents[litellm]' strands-agents-tools
```

## Basic setup

```python
from strands import Agent
from strands.models.litellm import LiteLLMModel

model = LiteLLMModel(
    client_args={"api_key": "<KEY>"},
    model_id="anthropic/claude-3-7-sonnet-20250219",
    params={"max_tokens": 1000, "temperature": 0.7}
)
agent = Agent(model=model)
```

## Configuration parameters

| Parameter | Location | Purpose |
|---|---|---|
| `model_id` | `LiteLLMModel(...)` | `<provider>/<model>` identifier, e.g. `anthropic/claude-3-7-sonnet-20250219` |
| `params` | `LiteLLMModel(...)` | Model-specific settings: `max_tokens`, `temperature`, etc. |
| `client_args` | `LiteLLMModel(...)` | Passed through to LiteLLM's completion API — `api_key`, `api_base`, `use_litellm_proxy` |

## Connecting to a self-hosted LiteLLM proxy

Two equivalent approaches — see [`../../litellm-proxy/_map.md`](../../litellm-proxy/_map.md) for running the proxy itself.

**Option 1 — explicit flag:**
```python
model = LiteLLMModel(
    client_args={
        "api_key": "<PROXY_KEY>",
        "api_base": "<PROXY_URL>",
        "use_litellm_proxy": True
    },
    model_id="amazon.nova-lite-v1:0"
)
```

**Option 2 — `litellm_proxy/` model-id prefix:**
```python
model = LiteLLMModel(
    client_args={"api_key": "<PROXY_KEY>", "api_base": "<PROXY_URL>"},
    model_id="litellm_proxy/amazon.nova-lite-v1:0"
)
```

## Advanced

Supports provider-agnostic prompt caching and structured output via tool calling — availability depends on whether the underlying model supports it.

## Gotchas

- **`ModuleNotFoundError` for `litellm`** → you installed `strands-agents` without the `[litellm]` extra. Fix: `pip install 'strands-agents[litellm]'`.
- **`model_id` semantics differ by target:** when talking directly to a provider, it's `<provider>/<model>`; when talking through a proxy, it's whatever `model_name` alias is defined in the proxy's `config.yaml` (see [`../../litellm-proxy/config-yaml-reference.md`](../../litellm-proxy/config-yaml-reference.md)) — optionally prefixed with `litellm_proxy/`.
- `client_args` values are literal Python values, not `os.environ/VAR`-style strings (that syntax is LiteLLM-server-config-only) — resolve env vars yourself with `os.getenv(...)` before passing them in.
