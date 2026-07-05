# LiteLLM Proxy — Calling From Python

Once the proxy is running (see [`docker-quickstart.md`](docker-quickstart.md)), call it like any OpenAI-compatible endpoint.

## Via OpenAI SDK

```python
from openai import OpenAI

client = OpenAI(
    api_key="sk-1234",
    base_url="http://0.0.0.0:4000/v1"
)

response = client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": "Hello!"}]
)
print(response.choices[0].message.content)
```

## Via LiteLLM SDK

```python
import litellm

litellm.api_base = "http://0.0.0.0:4000"
litellm.api_key = "sk-1234"

response = litellm.completion(
    model="gpt-4o",
    messages=[{"role": "user", "content": "Hello!"}]
)
```

## Via `curl` (sanity check before writing Python)

```bash
curl -X POST 'http://0.0.0.0:4000/chat/completions' \
  -H 'Content-Type: application/json' \
  -H 'Authorization: Bearer sk-1234' \
  -d '{
    "model": "gpt-4o",
    "messages": [{"role": "user", "content": "Hello!"}]
  }'
```

## From Strands Agents

See [`../strands-agents/model-providers/litellm.md`](../strands-agents/model-providers/litellm.md) — `LiteLLMModel` with `client_args={"api_base": "http://0.0.0.0:4000", "use_litellm_proxy": True}`.

## Gotcha

- The `model` value in the request (`"gpt-4o"` above) must match a `model_name` **alias** defined in the proxy's `config.yaml`, not necessarily the real upstream model ID (see [`config-yaml-reference.md`](config-yaml-reference.md)) — the proxy does the translation.
